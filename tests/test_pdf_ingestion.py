
from pathlib import Path

import pytest

from src.ingestion.pdf_ingestion import (
    extract_images_from_pdf,
    extract_tables_from_pdf,
    extract_text_from_pdf,
)


PDF_PATH = Path("data/sample_research_paper.pdf")


def test_extract_text_from_pdf():
    text = extract_text_from_pdf(str(PDF_PATH))

    assert text
    assert "Attention Is All You Need" in text


def test_extract_text_from_missing_pdf():
    missing_path = "data/missing_research_paper.pdf"

    with pytest.raises(FileNotFoundError):
        extract_text_from_pdf(missing_path)


def test_extract_tables_from_pdf():
    tables = extract_tables_from_pdf(str(PDF_PATH))

    assert isinstance(tables, list)

    for table in tables:
        assert "page" in table
        assert "data" in table
        assert isinstance(table["data"], list)


def test_extract_tables_from_missing_pdf():
    missing_path = "data/missing_research_paper.pdf"

    with pytest.raises(FileNotFoundError):
        extract_tables_from_pdf(missing_path)


def test_extract_images_from_pdf(tmp_path):
    images = extract_images_from_pdf(
        str(PDF_PATH),
        output_dir=str(tmp_path),
    )

    assert isinstance(images, list)

    for image in images:
        assert "page" in image
        assert "path" in image
        assert Path(image["path"]).is_file()


def test_extract_images_from_missing_pdf(tmp_path):
    missing_path = "data/missing_research_paper.pdf"

    with pytest.raises(FileNotFoundError):
        extract_images_from_pdf(
            missing_path,
            output_dir=str(tmp_path),
        )
