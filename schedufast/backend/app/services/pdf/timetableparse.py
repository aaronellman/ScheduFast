import pandas as pd
import os
from pathlib import Path
from app.services.google.new_event_create import insert_multiple_json_files
from app.services.pdf.pdftoexcel import extract_all_content_to_excel as convert
from .sheet_split import split_sheets
from app.services.ai import ai_parser
import asyncio

def getfilename(path):
    return os.path.basename(path)

async def process_file(new_path):
    pdf_path = new_path
    file_name = getfilename(new_path)
    xl_path = pdf_path.replace(".pdf", ".xlsx")

    print(f"Converting PDF: {pdf_path} → Excel: {xl_path}")
    convert(pdf_path, xl_path)

    # Split Excel sheets and convert to CSV
    output_files = split_sheets(xl_path, output_dir="split_sheets")

    loop = asyncio.get_running_loop()

    for file_path in output_files:
        df = pd.read_excel(file_path)
        csv_path = file_path.with_suffix(".csv")
        df.to_csv(csv_path, index=False)
        print(f"💾 Saved CSV: {csv_path}")

        # Create a unique JSON path for this CSV
        json_path = file_path.with_name(file_path.stem + "_events.json")
        
        # Run AI parser on this CSV, save to unique JSON
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, ai_parser.main, str(csv_path), str(json_path))
        
    json_dir = Path("split_sheets")
    all_jsons = list(json_dir.glob("*_events.json"))
    insert_multiple_json_files([str(p) for p in all_jsons])