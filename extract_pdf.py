from pypdf import PdfReader
import sys

def extract_text(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        print(f"Number of pages: {len(reader.pages)}")
        for i, page in enumerate(reader.pages):
            print(f"--- Page {i+1} ---")
            print(page.extract_text())
    except Exception as e:
        print(f"Error reading PDF: {e}")

if __name__ == "__main__":
    pdf_path = r"d:\Study\EquipSimulator\장비 메뉴얼\CAS CI-600A.pdf"
    output_path = r"d:\Study\EquipSimulator\pdf_text.txt"
    
    # Redirect stdout to file
    original_stdout = sys.stdout
    with open(output_path, 'w', encoding='utf-8') as f:
        sys.stdout = f
        extract_text(pdf_path)
    sys.stdout = original_stdout
