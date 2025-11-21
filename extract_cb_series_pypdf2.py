import PyPDF2
import sys

pdf_path = r"d:\Study\EquipSimulator\장비 메뉴얼\AND CB Series.pdf"
output_path = r"d:\Study\EquipSimulator\and_cb_series_text_pypdf2.txt"

def extract_all():
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            with open(output_path, 'w', encoding='utf-8') as out_f:
                for i, page in enumerate(reader.pages):
                    out_f.write(f"\n--- Page {i+1} ---\n")
                    text = page.extract_text()
                    if text:
                        out_f.write(text)
                    out_f.write("\n")
        print(f"Extracted to {output_path}")
    except Exception as e:
        print(f"Error: {e}")

extract_all()
