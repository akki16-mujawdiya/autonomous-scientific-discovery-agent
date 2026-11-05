from pathlib import Path

from src.ingestion.pdf_ingestion import (
    ingest_pdf_with_multimodal_analysis,
)

pdf_files = list(Path("data").rglob("*.pdf"))

if not pdf_files:
    print("No PDF found inside the data folder.")
    print("Place a research paper PDF inside data/ and run again.")
    raise SystemExit(1)

pdf_path = pdf_files[0]

print(f"Testing PDF: {pdf_path}")

result = ingest_pdf_with_multimodal_analysis(
    pdf_path=str(pdf_path),
    analyze_images=True,
)

print("\n=== PDF INGESTION RESULTS ===")
print("PDF:", result["pdf_path"])
print("Extracted text characters:", len(result["text"]))
print("Images extracted:", result["image_count"])

for item in result["images"]:
    print(f"\nImage: {item['path']}")

    if item["error"]:
        print("Error:", item["error"])
    else:
        print("Analysis:", item["analysis"])

if not result["text"].strip():
    print("\nWarning: No extractable text was found.")
