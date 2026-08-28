"""Document text extraction utilities for Canvas course files and syllabi."""

from __future__ import annotations

import io
import re
import xml.etree.ElementTree as ET
import zipfile
from typing import Optional, Tuple


def _extract_docx_text(content: bytes) -> Optional[str]:
    """Extract plain text from DOCX document XML without external dependencies."""
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as zf:
            if "word/document.xml" not in zf.namelist():
                return None
            xml_data = zf.read("word/document.xml")
            root = ET.fromstring(xml_data)

            # Extract all text nodes within w:p (paragraphs)
            paragraphs: list[str] = []
            ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

            for p in root.findall(".//w:p", ns):
                texts = [
                    node.text
                    for node in p.findall(".//w:t", ns)
                    if node.text is not None
                ]
                if texts:
                    paragraph_text = "".join(texts).strip()
                    if paragraph_text:
                        paragraphs.append(paragraph_text)

            if not paragraphs:
                # Fallback: extract any text node in the entire XML tree
                all_text = [elem.text for elem in root.iter() if elem.text]
                combined = " ".join(t.strip() for t in all_text if t.strip())
                return combined if combined else None

            return "\n\n".join(paragraphs)
    except Exception:
        return None


def _extract_pdf_text(content: bytes) -> Optional[str]:
    """Extract text from PDF using pypdf if available or basic text stream extraction."""
    # 1. Try pypdf if available
    try:
        import pypdf  # type: ignore

        reader = pypdf.PdfReader(io.BytesIO(content))
        pages_text: list[str] = []
        for page in reader.pages:
            t = page.extract_text()
            if t and t.strip():
                pages_text.append(t.strip())
        if pages_text:
            return "\n\n".join(pages_text)
    except ImportError:
        pass
    except Exception:
        pass

    # 2. Basic stream heuristic for uncompressed text streams in simple PDFs
    try:
        # Match standard PDF text operators (Tj, TJ within BT...ET blocks)
        bt_blocks = re.findall(rb"BT[\s\S]*?ET", content)
        extracted_strings: list[str] = []
        for block in bt_blocks:
            # Match (text) Tj or \[(...)\] TJ
            matches = re.findall(rb"\(([\s\S]*?)\)\s*Tj", block)
            for m in matches:
                try:
                    s = m.decode("latin-1").strip()
                    if s:
                        extracted_strings.append(s)
                except Exception:
                    continue
        if extracted_strings and len(" ".join(extracted_strings)) > 50:
            return " ".join(extracted_strings)
    except Exception:
        pass

    return None


def extract_text_from_bytes(
    content: bytes,
    filename: Optional[str] = None,
    content_type: Optional[str] = None,
) -> Tuple[Optional[str], str]:
    """
    Extract readable text from file bytes based on filename or MIME type.

    Returns:
        tuple[Optional[str], str]: (extracted_text, status)
        Status values: 'ok', 'empty', 'text_extraction_unavailable', 'unsupported_format'
    """
    if not content:
        return None, "empty"

    name_lower = (filename or "").lower()
    type_lower = (content_type or "").lower()

    # Plain text, markdown, CSV, JSON, HTML
    if (
        name_lower.endswith((".txt", ".md", ".csv", ".json", ".tsv", ".html", ".htm"))
        or "text/" in type_lower
        or "application/json" in type_lower
        or "application/csv" in type_lower
    ):
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                text = content.decode("latin-1")
            except Exception:
                return None, "text_extraction_unavailable"
        clean = text.strip()
        if not clean:
            return None, "empty"
        return clean, "ok"

    # DOCX
    if (
        name_lower.endswith(".docx")
        or "wordprocessingml" in type_lower
        or (content.startswith(b"PK\x03\x04") and name_lower.endswith(".docx"))
    ):
        docx_text = _extract_docx_text(content)
        if docx_text and docx_text.strip():
            return docx_text.strip(), "ok"
        return None, "text_extraction_unavailable"

    # PDF
    if (
        name_lower.endswith(".pdf")
        or "application/pdf" in type_lower
        or content.startswith(b"%PDF")
    ):
        pdf_text = _extract_pdf_text(content)
        if pdf_text and pdf_text.strip():
            return pdf_text.strip(), "ok"
        return None, "text_extraction_unavailable"

    return None, "unsupported_format"
