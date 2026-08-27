"""Tests for file download path and HTML helpers."""

from pathlib import Path

import pytest

from canvas_mcp_server.utils.file_download import (
    extract_file_ids_from_html,
    resolve_download_dir,
    resolve_unique_download_path,
    sanitize_path_component,
    validate_canvas_download_url,
    validate_relative_folder,
)


def test_sanitize_path_component_replaces_slashes_and_unsafe_chars() -> None:
    assert sanitize_path_component("foo/bar:baz<>") == "foo-barbaz"
    assert sanitize_path_component("   .hidden.  ") == "hidden"
    assert sanitize_path_component("") == "untitled"


def test_validate_relative_folder_accepts_nested_paths() -> None:
    assert validate_relative_folder("Homework 1/readings") == "Homework 1/readings"
    assert validate_relative_folder(None) is None
    assert validate_relative_folder("") is None


@pytest.mark.parametrize(
    "folder",
    [
        "../escape",
        "/absolute",
        "~/.ssh",
        "C:\\Windows",
        "safe\x00path",
    ],
)
def test_validate_relative_folder_rejects_unsafe_paths(folder: str) -> None:
    with pytest.raises(ValueError):
        validate_relative_folder(folder)


def test_resolve_download_dir_stays_under_root(download_dir: Path) -> None:
    course_dir, root = resolve_download_dir("Intro to Testing", "Week 1")

    assert root == download_dir.resolve()
    assert course_dir == download_dir / "Intro to Testing" / "Week 1"
    assert course_dir.is_relative_to(download_dir)


def test_extract_file_ids_from_html_deduplicates_and_preserves_order() -> None:
    html = """
    <a href="/courses/100001/files/500001/download">one</a>
    <a href="/files/500002/download">two</a>
    <a href="/courses/100001/files/500001/download">duplicate</a>
    <a href="/courses/100001/files/500003/download">three</a>
    """

    assert extract_file_ids_from_html(html) == ["500001", "500002", "500003"]


def test_extract_file_ids_from_html_empty_input() -> None:
    assert extract_file_ids_from_html(None) == []
    assert extract_file_ids_from_html("") == []
    assert extract_file_ids_from_html("<p>No files here</p>") == []


def test_resolve_unique_download_path_adds_numeric_suffix(tmp_path: Path) -> None:
    directory = tmp_path / "course"
    directory.mkdir()
    existing = directory / "notes.pdf"
    existing.write_bytes(b"original")

    resolved = resolve_unique_download_path(directory, "notes.pdf")

    assert resolved == directory / "notes (1).pdf"
    assert resolved.exists() is False


def test_validate_canvas_download_url_accepts_config_host(monkeypatch) -> None:
    monkeypatch.setattr(
        "canvas_mcp_server.config.Config.CANVAS_BASE_URL",
        "https://canvas.example.edu/api",
    )

    validate_canvas_download_url(
        "https://canvas.example.edu/files/500001/download?verifier=abc",
    )


def test_validate_canvas_download_url_rejects_foreign_host(monkeypatch) -> None:
    monkeypatch.setattr(
        "canvas_mcp_server.config.Config.CANVAS_BASE_URL",
        "https://canvas.example.edu/api",
    )

    with pytest.raises(ValueError, match="does not match"):
        validate_canvas_download_url("https://evil.example.edu/files/1/download")


def test_validate_canvas_download_url_rejects_non_https(monkeypatch) -> None:
    monkeypatch.setattr(
        "canvas_mcp_server.config.Config.CANVAS_BASE_URL",
        "https://canvas.example.edu/api",
    )

    with pytest.raises(ValueError, match="https"):
        validate_canvas_download_url("http://canvas.example.edu/files/1/download")
