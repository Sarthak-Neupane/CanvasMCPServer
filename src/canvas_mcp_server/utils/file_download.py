"""Shared logic for downloading Canvas files to the local filesystem."""

import re
from pathlib import Path
from typing import List, Optional, Tuple, Union
from urllib.parse import urlparse

from ..config import config
from ..models import DownloadBatchResult, DownloadFailure, DownloadedFile, FileDetail
from .canvas_api import canvas_api_client
from .http_client import HTTPError

_UNSAFE_PATH_CHARS = re.compile(r'[<>:"|?*\x00]')


def sanitize_path_component(name: str, *, max_length: int = 200) -> str:
    """Make a string safe for use as a single path component."""
    cleaned = name.replace("\\", "-").replace("/", "-")
    cleaned = _UNSAFE_PATH_CHARS.sub("", cleaned).strip().strip(".")
    if not cleaned:
        cleaned = "untitled"
    return cleaned[:max_length]


def validate_relative_folder(folder: Optional[str]) -> Optional[str]:
    """
    Validate an optional relative subfolder under the course directory.

    Raises:
        ValueError: If folder is absolute or attempts path traversal.
    """
    if folder is None or folder == "":
        return None
    if "\x00" in folder:
        raise ValueError("folder must not contain null bytes")
    if folder.startswith(("/", "~")) or folder.startswith("\\"):
        raise ValueError("folder must be a relative path")
    if re.match(r"^[A-Za-z]:", folder):
        raise ValueError("folder must not be an absolute path")
    parts = Path(folder).parts
    if ".." in parts:
        raise ValueError("folder must not contain '..'")
    return folder


def validate_canvas_download_url(url: str) -> None:
    """
    Ensure a file download URL points at the configured Canvas instance.

    Raises:
        ValueError: If the URL scheme or host is not allowed.
    """
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise ValueError(
            f"Download URL must use https scheme, got {parsed.scheme!r}",
        )
    if not parsed.hostname:
        raise ValueError("Download URL must include a host")

    base_host = urlparse(config.CANVAS_BASE_URL).hostname
    if not base_host:
        raise ValueError("CANVAS_BASE_URL must include a host for download validation")
    if parsed.hostname != base_host:
        raise ValueError(
            f"Download URL host {parsed.hostname!r} does not match "
            f"CANVAS_BASE_URL host {base_host!r}",
        )


def resolve_unique_download_path(directory: Path, filename: str) -> Path:
    """
    Return a destination path that does not collide with existing files.

    Uses ``name (1).ext``, ``name (2).ext``, ... when ``filename`` exists.
    """
    candidate = directory / filename
    if not candidate.exists():
        return candidate

    path = Path(filename)
    stem = path.stem
    suffix = path.suffix
    for counter in range(1, 1000):
        alt_name = sanitize_path_component(f"{stem} ({counter}){suffix}")
        candidate = directory / alt_name
        if not candidate.exists():
            return candidate

    raise ValueError(f"Could not find a unique filename for {filename!r}")


def _assert_within_root(path: Path, root: Path) -> None:
    """Ensure resolved path stays under the download root."""
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("Resolved download path escapes CANVAS_DOWNLOAD_DIR")


async def resolve_course_name(course_id: str) -> str:
    """Fetch the course display name for directory layout."""
    response = await canvas_api_client.get_rest(f"v1/courses/{course_id}")
    data = response.data
    if not isinstance(data, dict) or not data.get("name"):
        return f"course_{course_id}"
    return str(data["name"])


def resolve_download_dir(
    course_name: str,
    folder: Optional[str] = None,
) -> Tuple[Path, Path]:
    """
    Resolve course and file destination directories under CANVAS_DOWNLOAD_DIR.

    Returns:
        Tuple of (course_dir, download_root).
    """
    download_root = config.get_download_dir()
    relative_folder = validate_relative_folder(folder)
    course_dir = download_root / sanitize_path_component(course_name)
    if relative_folder:
        course_dir = course_dir / Path(relative_folder)
    _assert_within_root(course_dir, download_root)
    return course_dir.resolve(), download_root.resolve()


def extract_file_ids_from_html(html: Optional[str]) -> List[str]:
    """Extract Canvas file IDs embedded in HTML (descriptions, syllabi)."""
    from .html import extract_canvas_resource_references

    file_ids: List[str] = []
    seen: set[str] = set()
    for reference in extract_canvas_resource_references(html):
        if reference.get("type") != "file":
            continue
        file_id = reference.get("id")
        if file_id and file_id not in seen:
            seen.add(file_id)
            file_ids.append(file_id)
    return file_ids


async def _file_detail_or_error(file_id: str) -> Union[FileDetail, str]:
    try:
        response = await canvas_api_client.get_rest(f"v1/files/{file_id}")
        if not isinstance(response.data, dict):
            return "Canvas file response was not an object"
        return FileDetail.model_validate(response.data)
    except HTTPError as e:
        return str(e)


async def download_one_file(
    file_id: str,
    course_id: str,
    folder: Optional[str] = None,
) -> Union[DownloadedFile, DownloadFailure]:
    """Download a single file into the course directory."""
    try:
        course_name = await resolve_course_name(course_id)
        course_dir, _ = resolve_download_dir(course_name, folder)

        detail = await _file_detail_or_error(file_id)
        if isinstance(detail, str):
            return DownloadFailure(file_id=file_id, message=detail)

        if not detail.url:
            return DownloadFailure(
                file_id=file_id,
                message="File metadata did not include a download URL",
            )

        max_bytes = config.get_max_download_bytes()
        if detail.size is not None and detail.size > max_bytes:
            return DownloadFailure(
                file_id=file_id,
                message=(
                    f"File size {detail.size} bytes exceeds the "
                    f"{config.CANVAS_MAX_DOWNLOAD_SIZE_MB} MB download limit"
                ),
            )

        validate_canvas_download_url(detail.url)

        display_name = detail.display_name or detail.filename or f"file_{file_id}"
        filename = sanitize_path_component(display_name)
        local_path = resolve_unique_download_path(course_dir, filename)
        _assert_within_root(local_path, config.get_download_dir())

        course_dir.mkdir(parents=True, exist_ok=True)
        bytes_written = await canvas_api_client.download_file_to_path(
            detail.url,
            local_path,
            max_bytes=max_bytes,
        )

        return DownloadedFile(
            file_id=file_id,
            display_name=display_name,
            local_path=str(local_path.resolve()),
            bytes_written=bytes_written,
            skipped=False,
        )

    except (HTTPError, ValueError, OSError) as e:
        return DownloadFailure(file_id=file_id, message=str(e))


async def download_many_files(
    file_ids: List[str],
    course_id: str,
    folder: Optional[str] = None,
) -> DownloadBatchResult:
    """
    Download multiple files into the same course directory.

    Each file is attempted independently; successes and failures are reported
    separately so one bad file does not abort the rest of the batch.
    """
    course_name = await resolve_course_name(course_id)
    course_dir, _download_root = resolve_download_dir(course_name, folder)

    downloaded: List[DownloadedFile] = []
    failed: List[DownloadFailure] = []

    for file_id in file_ids:
        result = await download_one_file(file_id, course_id, folder)
        if isinstance(result, DownloadFailure):
            failed.append(result)
        else:
            downloaded.append(result)

    return DownloadBatchResult(
        destination_root=str(course_dir),
        downloaded=downloaded,
        failed=failed,
        downloaded_count=len(downloaded),
        failed_count=len(failed),
        result_count=len(downloaded) + len(failed),
    )
