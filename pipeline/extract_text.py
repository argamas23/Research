import argparse
import os
import shutil
import subprocess
import sys
import tempfile

import fitz  # PyMuPDF


MIN_TEXT_CHARS = 20
OCR_DPI = 300


def page_text(page):
    return page.get_text("text").strip()


def ocr_page(page, tesseract):
    pix = page.get_pixmap(dpi=OCR_DPI, alpha=False)
    with tempfile.NamedTemporaryFile(suffix=".png") as image:
        pix.save(image.name)
        result = subprocess.run(
            [tesseract, image.name, "stdout", "--psm", "6"],
            check=True,
            capture_output=True,
            text=True,
        )
    return result.stdout.strip()


def pdf_to_text(pdf_path, txt_path):
    tesseract = shutil.which("tesseract")
    used_ocr = False
    missing_ocr_warning = False

    os.makedirs(os.path.dirname(os.path.abspath(txt_path)), exist_ok=True)
    with fitz.open(pdf_path) as doc, open(txt_path, "w", encoding="utf-8") as out:
        for page_num, page in enumerate(doc, start=1):
            text = page_text(page)
            if len(text) < MIN_TEXT_CHARS:
                if tesseract:
                    text = ocr_page(page, tesseract)
                    used_ocr = True
                    print(f"Page {page_num}: OCR fallback used.")
                elif not missing_ocr_warning:
                    print("OCR fallback skipped: install the tesseract binary for scanned PDFs.")
                    missing_ocr_warning = True
            out.write(text + "\n\n")

    suffix = " with OCR fallback" if used_ocr else ""
    print(f"Text{suffix} successfully saved to {txt_path}")


def main():
    parser = argparse.ArgumentParser(description="Extract text from a PDF, using OCR for scanned pages when Tesseract is installed.")
    parser.add_argument("input_pdf")
    parser.add_argument("output_txt")
    args = parser.parse_args()
    pdf_to_text(args.input_pdf, args.output_txt)


if __name__ == "__main__":
    try:
        main()
    except (fitz.FileDataError, subprocess.CalledProcessError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
