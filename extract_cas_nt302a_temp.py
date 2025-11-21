import pdfplumber
import sys

pdf_path = r"d:\Study\EquipSimulator\장비 메뉴얼\CAS NT-302A.pdf"
output_path = r"d:\Study\EquipSimulator\cas_nt302a_text.txt"

def extract_all():
    try:
        with pdfplumber.open(pdf_path) as pdf:
            with open(output_path, 'w', encoding='utf-8') as f:
                for i, page in enumerate(pdf.pages):
                    f.write(f"\n--- Page {i+1} ---\n")
                    text = page.extract_text()
                    if text:
                        f.write(text)
                    f.write("\n")
        print(f"Extracted to {output_path}")
    except Exception as e:
        print(f"Error: {e}")

extract_all()
