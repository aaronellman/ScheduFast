import pandas as pd
import numpy as np
import math
import re
import calendar
from datetime import datetime, timezone, time, timedelta
from app.services.google.eventcreate import create_event
from app.services.pdf.pdftoexcel import extract_all_content_to_excel as convert
import os
from .xl_to_csv import main as to_csv
from app.services.ai import ai_parser
from app.services.google.new_event_create import main as create_events

def getfilename(path):
    return os.path.basename(path)

async def process_file(new_path):
    pdf_path = new_path
    file_name = getfilename(new_path)
    xl_path = pdf_path.replace(".pdf",".xlsx")
    csv_path = file_name.replace(".pdf",".")
    print(f"Converting PDF: {pdf_path} → Excel: {xl_path}")
    convert(pdf_path, xl_path)

    print(f"Converting Excel: {xl_path} → CSV: timetable.csv")
    to_csv(xl_path, "timetable.csv")
    import asyncio
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, ai_parser.main, "timetable.csv")
    json_path = os.path.join(os.getcwd(), "timetable_events.json")
    if os.path.exists(json_path):
        create_events(json_path)
    else:
        print(f"❌ Error: {json_path} was not created by ai_parser.main")



