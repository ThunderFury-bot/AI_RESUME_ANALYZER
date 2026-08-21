"""
Tests for pdf_extraction.py — verifies text extraction behavior,
including error handling for invalid, empty, and non-text PDFs.
"""

import pytest
import io
from app.pdf_extraction import extract_text_from_pdf, PDFExtractionError


def make_simple_pdf_bytes(text: str = "Hello World") -> bytes:
    """
    Helper to generate a minimal valid PDF containing the given text,
    using reportlab if available, otherwise skips tests that need it.
    """
    reportlab = pytest.importorskip("reportlab")
    from reportlab.pdfgen import canvas

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(100, 750, text)
    c.save()
    return buffer.getvalue()


def test_extract_text_from_valid_pdf():
    """A PDF containing real text should return that text, not raise."""
    pdf_bytes = make_simple_pdf_bytes("John Doe Software Engineer")
    result = extract_text_from_pdf(pdf_bytes)
    assert "John Doe" in result
    assert "Software Engineer" in result


def test_extract_text_from_invalid_bytes_raises():
    """Passing bytes that aren't a real PDF should raise PDFExtractionError."""
    invalid_bytes = b"this is not a pdf file at all"
    with pytest.raises(PDFExtractionError):
        extract_text_from_pdf(invalid_bytes)


def test_extract_text_from_empty_bytes_raises():
    """Passing empty bytes should raise PDFExtractionError."""
    with pytest.raises(PDFExtractionError):
        extract_text_from_pdf(b"")