
from pathlib import Path

import pdfplumber
from pypdf import PdfReader


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF research paper."""
    reader = PdfReader(pdf_path)

    extracted_text = []

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            extracted_text.append(page_text)

    return "\n".join(extracted_text)


def extract_tables_from_pdf(pdf_path):
    """Extract tables from each page of a PDF."""
    extracted_tables = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()

            for table in tables:
                extracted_tables.append({
                    "page": page_number,
                    "data": table,
                })

    return extracted_tables


def extract_images_from_pdf(pdf_path, output_dir="data/extracted_images"):
    """Extract embedded images from a PDF and save them as files."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    reader = PdfReader(pdf_path)
    extracted_images = []

    for page_number, page in enumerate(reader.pages, start=1):
        for image_number, image in enumerate(page.images, start=1):
            image_path = output_path / (
                f"page_{page_number}_image_{image_number}_{image.name}"
            )

            image_path.write_bytes(image.data)

            extracted_images.append({
                "page": page_number,
                "path": str(image_path),
            })

    return extracted_images
