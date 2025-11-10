from PIL import Image
import pytesseract
import os

# Ensure tesseract is installed on host system and accessible
# On Ubuntu: sudo apt install -y tesseract-ocr

def ocr_image_file(path: str) -> str:
    try:
        text = pytesseract.image_to_string(Image.open(path))
        return text
    except Exception as e:
        print('OCR error', e)
        return ''