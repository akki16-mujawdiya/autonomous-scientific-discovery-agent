
import base64
import io
from pathlib import Path

import pdfplumber
import requests
from PIL import Image
from pypdf import PdfReader


# Ollama configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llava:latest"
REQUEST_TIMEOUT = 180


def _validate_pdf_path(pdf_path):
    """Validate and return a PDF path."""
    path = Path(pdf_path)

    if not path.is_file():
        raise FileNotFoundError(f"PDF file not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a PDF file, got: {path}")

    return path


def extract_text_from_pdf(pdf_path):
    """Extract readable text from every page of a PDF."""
    pdf_path = _validate_pdf_path(pdf_path)
    extracted_pages = []

    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""

                if text.strip():
                    extracted_pages.append(
                        f"--- Page {page_number} ---\n{text.strip()}"
                    )

    except Exception as exc:
        raise RuntimeError(
            f"Failed to extract PDF text: {exc}"
        ) from exc

    return "\n\n".join(extracted_pages)


def extract_tables_from_pdf(pdf_path):
    """
    Extract tables from a PDF.

    Returns a list of dictionaries. Each dictionary contains the page
    number, table number, and table rows.
    """
    pdf_path = _validate_pdf_path(pdf_path)
    extracted_tables = []

    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                tables = page.extract_tables() or []

                for table_number, table in enumerate(tables, start=1):
                    if not table:
                        continue

                    extracted_tables.append(
                        {
                            "page": page_number,
                            "table_number": table_number,
                            "data": table,
                        }
                    )

    except Exception as exc:
        raise RuntimeError(
            f"Failed to extract PDF tables: {exc}"
        ) from exc

    return extracted_tables


def extract_images_from_pdf(
    pdf_path,
    output_dir="data/extracted_images",
):
    """
    Extract embedded raster images from a PDF.

    Returns image metadata containing page number, image number,
    and the saved image path.
    """
    pdf_path = _validate_pdf_path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    extracted_images = []

    try:
        reader = PdfReader(str(pdf_path))

        for page_number, page in enumerate(reader.pages, start=1):
            try:
                page_images = page.images
            except Exception as exc:
                print(
                    f"Warning: Cannot read images on page "
                    f"{page_number}: {exc}"
                )
                continue

            for image_number, image in enumerate(page_images, start=1):
                try:
                    image_data = image.data

                    with Image.open(io.BytesIO(image_data)) as source:
                        source.load()

                        # Save in a consistent format supported by LLaVA.
                        converted = source.convert("RGB")
                        image_name = (
                            f"{pdf_path.stem}_page_{page_number}"
                            f"_image_{image_number}.png"
                        )
                        image_path = output_dir / image_name
                        converted.save(image_path, format="PNG")

                    extracted_images.append(
                        {
                            "page": page_number,
                            "image_number": image_number,
                            "path": str(image_path),
                        }
                    )

                except Exception as exc:
                    print(
                        f"Warning: Could not extract image "
                        f"{image_number} on page {page_number}: {exc}"
                    )

    except Exception as exc:
        raise RuntimeError(
            f"Failed to extract PDF images: {exc}"
        ) from exc

    return extracted_images


def analyze_image_with_llava(image_path, prompt=None):
    """
    Analyze a scientific figure, chart, graph, or diagram using Ollama LLaVA.

    Ollama must be running locally and the configured model must be installed.
    """
    image_path = Path(image_path)

    if not image_path.is_file():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    if prompt is None:
        prompt = (
            "Analyze this scientific image. Identify visible labels, "
            "components, relationships, axes, units, and values where "
            "applicable. Explain charts, graphs, and diagrams clearly. "
            "Distinguish directly visible information from interpretation. "
            "Do not invent missing labels, values, or connections. "
            "State when something is unclear."
        )

    try:
        # Verify the image can be opened before sending it.
        with Image.open(image_path) as image:
            image.verify()

        encoded_image = base64.b64encode(
            image_path.read_bytes()
        ).decode("utf-8")

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "images": [encoded_image],
                "stream": False,
            },
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()

        result = response.json()
        description = result.get("response", "").strip()

        if not description:
            raise RuntimeError(
                "Ollama returned an empty image description."
            )

        return description

    except requests.ConnectionError as exc:
        raise RuntimeError(
            "Cannot connect to Ollama. Check that Ollama is running "
            "at http://localhost:11434."
        ) from exc

    except requests.Timeout as exc:
        raise RuntimeError(
            "Ollama image analysis timed out. Try again or increase "
            "REQUEST_TIMEOUT."
        ) from exc

    except requests.HTTPError as exc:
        raise RuntimeError(
            f"Ollama API request failed: {exc}"
        ) from exc

    except (OSError, ValueError) as exc:
        raise RuntimeError(
            f"Could not process image {image_path}: {exc}"
        ) from exc


def ingest_pdf_with_multimodal_analysis(
    pdf_path,
    output_dir="data/extracted_images",
    analyze_images=True,
):
    """
    Extract text, tables, and images from a PDF and optionally analyze
    extracted images using LLaVA.

    Returns a dictionary containing all extracted information.
    """
    pdf_path = _validate_pdf_path(pdf_path)

    text = extract_text_from_pdf(pdf_path)
    tables = extract_tables_from_pdf(pdf_path)

    images = extract_images_from_pdf(
        pdf_path=pdf_path,
        output_dir=output_dir,
    )

    image_results = []

    for image_info in images:
        result = {
            **image_info,
            "analysis": None,
            "error": None,
        }

        if analyze_images:
            try:
                result["analysis"] = analyze_image_with_llava(
                    image_info["path"]
                )
            except (RuntimeError, FileNotFoundError) as exc:
                result["error"] = str(exc)

        image_results.append(result)

    return {
        "pdf_path": str(pdf_path),
        "text": text,
        "tables": tables,
        "images": image_results,
        "image_count": len(image_results),
    }
