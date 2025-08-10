import pymupdf
import pandas as pd

def extract_all_content_to_excel(pdf_path, excel_path):
    doc = pymupdf.open(pdf_path)
    all_data = []

    for page in doc:
        # Extract ALL text as fallback (not just tables)
        full_text = page.get_text("text")
        if full_text.strip():  # If page has text
            all_data.append(full_text)

        # Extract tables (if any)
        tables = page.find_tables()
        if tables.tables:
            for table in tables:
                all_data.append(table.to_pandas())

    # Save everything to Excel
    with pd.ExcelWriter(excel_path) as writer:
        for i, item in enumerate(all_data):
            if isinstance(item, pd.DataFrame):
                item.to_excel(writer, sheet_name=f"Table_{i}", index=False)
    print(f"All content saved to {excel_path}")
    return excel_path
    

# Usage
#pdf_path = r"C:\vscode\Python\schedufast\data\input\timetable.pdf"
#extract_all_content_to_excel(pdf_path, "timetable_converted.xlsx")