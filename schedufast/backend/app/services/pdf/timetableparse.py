import pandas as pd
import numpy as np
import math
import re
import calendar
from datetime import datetime, timezone, time, timedelta
from app.services.google.eventcreate import create_event
from app.services.pdf.pdftoexcel import extract_all_content_to_excel as convert
import os
from xl_to_csv import main as xl_to_csv
from app.services.ai import ai_parser

def create_events():
    pass

def main(xlsx_path, file_num):
    print(f"main() called with: {xlsx_path}, file_num: {file_num}")
    #Convert, split, Read 

def process_file(new_path):
    pdf_path = new_path
    file_name = getfilename(new_path)
    xl_path = pdf_path.replace(".pdf",".xlsx")
    filename = file_name.replace(".pdf",".xlsx")
    convert(pdf_path,xl_path) #converting to excel
    xl_to_csv(xl_path, "timetable.csv")
    ai_parser.main()

def getfilename(path):
    return os.path.basename(path)


