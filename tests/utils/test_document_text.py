"""Unit tests for document text extraction utilities."""

import io
import zipfile

from canvas_mcp_server.utils.document_text import extract_text_from_bytes


def test_extract_text_from_plain_text() -> None:
    content = b"Course Syllabus: Welcome to CS 101.\nInstructor: Dr. Smith."
    text, status = extract_text_from_bytes(content, filename="syllabus.txt")
    assert status == "ok"
    assert text == "Course Syllabus: Welcome to CS 101.\nInstructor: Dr. Smith."


def test_extract_text_from_markdown() -> None:
    content = b"# CS 101 Syllabus\n\n- Homework: 40%\n- Exams: 60%"
    text, status = extract_text_from_bytes(content, filename="syllabus.md")
    assert status == "ok"
    assert text is not None
    assert "- Homework: 40%" in text


def test_extract_text_from_empty_content() -> None:
    text, status = extract_text_from_bytes(b"", filename="empty.txt")
    assert status == "empty"
    assert text is None


def test_extract_text_from_docx() -> None:
    # Build an in-memory docx zip file
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        document_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            "<w:body>"
            "<w:p><w:r><w:t>CS 201 Data Structures</w:t></w:r></w:p>"
            "<w:p><w:r><w:t>Late policy: 10% penalty per day.</w:t></w:r></w:p>"
            "</w:body>"
            "</w:document>"
        )
        zf.writestr("word/document.xml", document_xml)

    docx_bytes = buf.getvalue()
    text, status = extract_text_from_bytes(docx_bytes, filename="syllabus.docx")
    assert status == "ok"
    assert text is not None
    assert "CS 201 Data Structures" in text
    assert "Late policy: 10% penalty per day." in text


def test_extract_text_from_scanned_or_empty_pdf() -> None:
    # A dummy PDF with no extractable text
    dummy_pdf = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\nxref\n0 1\n0000000000 65535 f \ntrailer<</Size 1/Root 1 0 R>>\nstartxref\n50\n%%EOF"
    text, status = extract_text_from_bytes(dummy_pdf, filename="scanned.pdf")
    assert status == "text_extraction_unavailable"
    assert text is None


def test_extract_text_unsupported_format() -> None:
    image_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR..."
    text, status = extract_text_from_bytes(image_bytes, filename="diagram.png")
    assert status == "unsupported_format"
    assert text is None
