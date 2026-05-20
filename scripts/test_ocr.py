import os
import json
import fitz
import cv2
import numpy as np

from paddleocr import PPStructure


PDF_PATH = "samples/sample.pdf"
OUTPUT_JSON = "output/ocr_result.json"


# Initialize OCR engine
engine = PPStructure(show_log=True)


def pdf_to_images(pdf_path):
    doc = fitz.open(pdf_path)

    pages = []

    for page_index in range(len(doc)):
        page = doc[page_index]

        pix = page.get_pixmap(dpi=300)

        img = np.frombuffer(
            pix.samples,
            dtype=np.uint8
        ).reshape(
            pix.height,
            pix.width,
            pix.n
        )

        if pix.n == 4:
            img = cv2.cvtColor(
                img,
                cv2.COLOR_BGRA2BGR
            )

        pages.append({
            "page_index": page_index,
            "image": img
        })

    return pages


def run_ocr(pages):
    results = []

    for page_data in pages:

        page_index = page_data["page_index"]

        print(f"Processing page {page_index}")

        image = page_data["image"]

        result = engine(image)

        results.append({
            "page": page_index,
            "ocr_result": result
        })

    return results


def save_results(results):
    os.makedirs("output", exist_ok=True)

    with open(OUTPUT_JSON, "w") as f:
        json.dump(
            results,
            f,
            indent=2,
            default=str
        )

    print(f"\nSaved OCR output to:")
    print(OUTPUT_JSON)


def main():

    print("\nRendering PDF pages...")
    pages = pdf_to_images(PDF_PATH)

    print(f"Rendered {len(pages)} pages")

    print("\nRunning OCR...")
    results = run_ocr(pages)

    print("\nSaving results...")
    save_results(results)

    print("\nDONE")


if __name__ == "__main__":
    main()