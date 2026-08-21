import pdfplumber
import io

class PDFExtractionError(Exception):
    pass

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extracts text from a PDF file's raw bytes.
    Raises PDFExtractionError if the file is invalid or contains no extractable text.
    """
    try:
        text_parts = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            if len(pdf.pages) == 0:
                raise PDFExtractionError("The PDF has no pages.")
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
    except PDFExtractionError:
        raise
    except Exception as e:
        raise PDFExtractionError(f"Could not read PDF file: {str(e)}")

    full_text = "\n".join(text_parts).strip()

    if not full_text:
        raise PDFExtractionError(
            "No extractable text found in this PDF. It may be a scanned image "
            "without a text layer, which is outside the scope of this tool."
        )

    return full_text