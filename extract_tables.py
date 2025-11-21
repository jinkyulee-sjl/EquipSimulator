import pdfplumber
import sys

pdf_path = r"d:\Study\EquipSimulator\장비 메뉴얼\AND GP Series.pdf"
output_path = r"d:\Study\EquipSimulator\table_content.txt"

def extract_pages(pages):
    with pdfplumber.open(pdf_path) as pdf:
        with open(output_path, 'w', encoding='utf-8') as f:
            for p in pages:
                if p < len(pdf.pages):
                    f.write(f"\n--- Page {p+1} ---\n")
                    page = pdf.pages[p]
                    text = page.extract_text()
                    f.write(text + "\n")
                    # Also try to extract tables
                    tables = page.extract_tables()
                    for i, table in enumerate(tables):
                        f.write(f"\n[Table {i+1}]\n")
                        for row in table:
                            f.write(str(row) + "\n")
    print(f"Extracted to {output_path}")

# Pages 46-49 (Data Format Examples) -> 45-48
# Pages 81-85 (Commands) -> 80-84
pages_to_extract = [45, 46, 47, 48, 80, 81, 82, 83, 84]

try:
    extract_pages(pages_to_extract)
except Exception as e:
    print(f"Error: {e}")
