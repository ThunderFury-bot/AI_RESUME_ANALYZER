"""
pdf_extraction.py

Handles extraction of text content from uploaded PDF resume files.
Uses pdfplumber to read PDF pages and extract raw text for downstream
analysis by the Ollama LLM.
"""

import pdfplumber
import io


class PDFExtractionError(Exception):
    """
    Raised when a PDF cannot be read or contains no extractable text.

    This is used to distinguish PDF-specific failures (corrupt file,
    scanned/image-only PDF, empty document) from other unexpected errors,
    so the API layer can return a clean, user-friendly error message.
    """
    pass


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract all readable text from a PDF file's raw bytes.

    Args:
        file_bytes (bytes): The raw binary content of the uploaded PDF file.

    Returns:
        str: The concatenated text extracted from every page of the PDF,
             with leading/trailing whitespace stripped.

    Raises:
        PDFExtractionError: If the file cannot be opened as a valid PDF,
            has zero pages, or contains no extractable text (e.g. it is
            a scanned image without a text layer).
    """
    try:
        text_parts = []
        # Open the PDF directly from in-memory bytes (no temp file needed)
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            if len(pdf.pages) == 0:
                raise PDFExtractionError("The PDF has no pages.")

            # Extract text page by page and collect non-empty results
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)

    except PDFExtractionError:
        # Re-raise our own error type as-is without wrapping it again
        raise
    except Exception as e:
        # Any other failure (corrupt file, unsupported format, etc.)
        # is wrapped into our custom exception for consistent handling
        raise PDFExtractionError(f"Could not read PDF file: {str(e)}")

    # Join all page texts into a single string, trimming whitespace
    full_text = "\n".join(text_parts).strip()

    if not full_text:
        # This typically happens with scanned/image-only PDFs that have
        # no embedded text layer — OCR is intentionally out of scope
        raise PDFExtractionError(
            "No extractable text found in this PDF. It may be a scanned image "
            "without a text layer, which is outside the scope of this tool."
        )

    return full_text