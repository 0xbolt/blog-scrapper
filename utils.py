from io import BytesIO
from pypdf import PdfReader, PdfWriter

def merge_pdfs(pdfs: list[bytes]) -> bytes:
    buffer = BytesIO()
    writer = PdfWriter()
    for pdf_bytes in pdfs:
        pdf_buffer = BytesIO(pdf_bytes)
        pdf_reader = PdfReader(pdf_buffer)
        writer.append(pdf_reader)
    writer.write(buffer)
    buffer.seek(0)
    return buffer.read()
