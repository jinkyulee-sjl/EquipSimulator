import sys
import os

pdf_path = r"d:\Study\EquipSimulator\장비 메뉴얼\AND GP Series.pdf"
output_path = r"d:\Study\EquipSimulator\full_text.txt"

def extract_all():
    try:
        import PyPDF2
        print("Using PyPDF2")
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            with open(output_path, 'w', encoding='utf-8') as out:
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    out.write(f"\n--- Page {i+1} ---\n")
                    out.write(text)
        print(f"Extracted to {output_path}")
    except Exception as e:
        print(f"Error: {e}")

extract_all()
