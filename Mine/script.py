# import fitz  # PyMuPDF
# import camelot  # For extracting tables
# import pytesseract  # OCR for image-based PDFs
# from pdf2image import convert_from_path  # Convert PDF pages to images
# import cv2
# import numpy as np
# import sys

# def preprocess_image(image):
#     """Preprocess image for better OCR and table extraction."""
#     gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
#     thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
#     return thresh

# def extract_tables_from_image(image):
#     """Detects tables from an image using OpenCV."""
#     processed_image = preprocess_image(image)
#     contours, _ = cv2.findContours(processed_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#     table_data = []
#     for contour in contours:
#         x, y, w, h = cv2.boundingRect(contour)
#         if w > 50 and h > 20:  # Filtering small noise
#             cell_img = image[y:y+h, x:x+w]
#             cell_text = pytesseract.image_to_string(cell_img, config='--psm 6')
#             table_data.append(cell_text.strip())
#     return table_data

# def extract_text_and_tables(pdf_path, txt_path):
#     try:
#         doc = fitz.open(pdf_path)  # Open the PDF file
#         with open(txt_path, "w", encoding="utf-8") as txt_file:
#             for page_num in range(len(doc)):
#                 text = doc[page_num].get_text("text")  # Extract text
                
#                 if not text.strip():  # If no text is found, use OCR
#                     images = convert_from_path(pdf_path, first_page=page_num+1, last_page=page_num+1)
#                     ocr_text = pytesseract.image_to_string(images[0])
#                     text = ocr_text.strip()
                
#                 txt_file.write(f"Page {page_num + 1}\n")
#                 txt_file.write(text + "\n\n")
                
#                 # Extract tables using Camelot for text-based PDFs
#                 tables = camelot.read_pdf(pdf_path, pages=str(page_num + 1))
#                 if tables.n > 0:
#                     txt_file.write("Tables:\n")
#                     for i, table in enumerate(tables):
#                         txt_file.write(f"Table {i + 1}:\n")
#                         txt_file.write(table.df.to_string(index=False) + "\n\n")  # Format table
                
#                 # Extract tables from image-based PDFs
#                 if not text.strip():  # If it was image-based, extract tables from image
#                     table_data = extract_tables_from_image(np.array(images[0]))
#                     if table_data:
#                         txt_file.write("Extracted Tables from Image:\n")
#                         txt_file.write("\n".join(table_data) + "\n\n")
#         print(f"Text and tables successfully saved to {txt_path}")
#     except Exception as e:
#         print(f"Error: {e}")

# if __name__ == "__main__":
#     if len(sys.argv) != 3:
#         print("Usage: python script.py input.pdf output.txt")
#     else:
#         extract_text_and_tables(sys.argv[1], sys.argv[2])


import fitz  # PyMuPDF
import sys

def pdf_to_text(pdf_path, txt_path):
    try:
        doc = fitz.open(pdf_path)  # Open the PDF file
        with open(txt_path, "w", encoding="utf-8") as txt_file:
            for page_num in range(len(doc)):
                text = doc[page_num].get_text("text")  # Extract text
                txt_file.write(text + "\n\n")  # Write text with spacing
        print(f"Text successfully saved to {txt_path}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py input.pdf output.txt")
    else:
        pdf_to_text(sys.argv[1], sys.argv[2])