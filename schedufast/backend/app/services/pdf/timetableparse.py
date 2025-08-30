import pandas as pd
import os
from pathlib import Path
from app.services.google.new_event_create import insert_multiple_json_files
from app.services.pdf.pdftoexcel import extract_all_content_to_excel as convert
from .sheet_split import split_sheets
from .format_csv import reformat_timetable  # Import your reformatting function
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

    reformatted_files = []

    for file_path in output_files:
        df = pd.read_excel(file_path)
        csv_path = file_path.with_suffix(".csv")
        df.to_csv(csv_path, index=False)
        print(f"💾 Saved CSV: {csv_path}")

        # Use your formatter instead of AI parser
        try:
            # FIXED: Calculate the expected output path BEFORE calling reformat_timetable
            reformatted_csv_path = csv_path.with_name(csv_path.stem + "_reformatted.csv")
            
            # FIXED: Pass the output path to reformat_timetable
            reformatted_df = reformat_timetable(str(csv_path), str(reformatted_csv_path))
            
            # Add to our list of reformatted files
            reformatted_files.append(str(reformatted_csv_path))
            
            print(f"📅 Reformatted timetable saved: {reformatted_csv_path}")
            print(f"📊 Found {len(reformatted_df)} classes")
            
        except Exception as e:
            print(f"⚠️  Error reformatting {csv_path}: {e}")
            continue

    # Convert reformatted CSVs to JSON format for Google Calendar
    json_files = []
    for csv_file in reformatted_files:
        json_path = Path(csv_file).with_suffix(".json")
        csv_to_calendar_json(csv_file, str(json_path))
        json_files.append(str(json_path))
    
    # Insert events to Google Calendar
    insert_multiple_json_files(json_files)

def csv_to_calendar_json(csv_path, json_path):
    """
    Convert reformatted Day,Time,Subject CSV to JSON format for Google Calendar
    """
    import json
    from datetime import datetime
    
    df = pd.read_csv(csv_path)
    events = []
    
    # Month name to number mapping
    month_map = {
        'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
        'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
        'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
    }
    
    for _, row in df.iterrows():
        try:
            # Parse the time range (e.g., "08:00-08:50")
            time_parts = row['Time'].split('-')
            start_time = time_parts[0].strip()
            end_time = time_parts[1].strip()
            
            # Parse the date (e.g., "Wed 6 Aug")
            date_parts = row['Day'].split()
            
            if len(date_parts) == 3:
                day_name, day_num, month_name = date_parts
                month_num = month_map.get(month_name, '08')  # Default to August
                day_padded = day_num.zfill(2)
                
                # Assume current academic year (2025)
                year = "2025"
                date_str = f"{year}-{month_num}-{day_padded}"
                
                # Create event in Google Calendar format
                event = {
                    "summary": row['Subject'],
                    "description": f"Class: {row['Subject']}",
                    "start": {
                        "dateTime": f"{date_str}T{start_time}:00",
                        "timeZone": "Africa/Johannesburg"
                    },
                    "end": {
                        "dateTime": f"{date_str}T{end_time}:00", 
                        "timeZone": "Africa/Johannesburg"
                    },
                }
                events.append(event)
                
        except Exception as e:
            print(f"⚠️  Error processing row {row}: {e}")
            continue
    
    # Save events to JSON file
    with open(json_path, 'w') as f:
        json.dump(events, f, indent=2)
    
    print(f"🗓️  Created calendar JSON: {json_path} with {len(events)} events")