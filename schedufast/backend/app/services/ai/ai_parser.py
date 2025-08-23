from google import genai
from google.genai import types
import json
import re
import csv
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("GENAI_API_KEY")

client = genai.Client(api_key=API_KEY)

def read_csv(file_path):
    """Read CSV file and return its content as text"""
    try:
        with open(file_path, 'r', encoding='utf-8') as csv_file:
            return csv_file.read()
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return None

def parse_csv_structure(csv_content):
    """Parse the CSV structure to understand weeks, days, and times"""
    lines = csv_content.split('\n')
    header = []
    schedule_data = []
    
    # Find where the schedule starts
    schedule_start = 0
    for i, line in enumerate(lines):
        if 'Academic Week' in line or 'Assess Week' in line or 'ASSESS' in line:
            schedule_start = i
            break
        header.append(line)
    
    # Extract column headers (days of week)
    day_headers = lines[schedule_start].split(',')
    
    # Extract time slots
    time_slots = []
    for line in lines[schedule_start+1:]:
        if not line.strip():
            continue
        cells = line.split(',')
        if cells[0] and ('H' in cells[0] or ':' in cells[0]):  # If first cell has a time
            time_slots.append(cells[0])
    
    return {
        'header': header,
        'day_headers': day_headers,
        'time_slots': time_slots,
        'schedule_lines': lines[schedule_start:]
    }

def is_week_header(line):
    """Check if a line is a week header"""
    line_upper = line.upper()
    has_week_identifier = ('ACADEMIC WEEK' in line_upper or 
                          'ASSESS WEEK' in line_upper or 
                          'ASSESS' in line_upper)
    has_month = any(month.upper() in line_upper for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    return has_week_identifier and has_month

def create_structured_prompt(csv_batch, structure_info):
    """Create a more structured prompt for the AI"""
    
    module_mapping = {
        "CONE5112": "Computer Networks 1B",
        "INSY6112": "Information Systems 1B", 
        "ITPP5112": "IT Professional Practice",
        "PROG6112": "Programming 1B",
        "PROG6112 WKSP": "Programming 1B Workshop"
    }
    
    prompt = f"""
Please convert this timetable data into a JSON array of class events.

MODULE CODE MAPPING (USE THESE NAMES):
{json.dumps(module_mapping, indent=2)}

CSV STRUCTURE:
- Days of week: {structure_info['day_headers']}
- Time slots: {structure_info['time_slots']}

INSTRUCTIONS:
1. Process each cell that contains a class like "PROG6112 CR02"
2. Extract: module code, room (if available)
3. Use the module mapping above for the summary field
4. Determine the date based on the week and day information
5. Determine the time based on the time slot
6. Skip holidays, assessment weeks, and empty cells
7. Use 2025 as the year for all dates
8. Timezone: Africa/Johannesburg (UTC+2)

OUTPUT FORMAT:
Return ONLY a JSON array with objects like:
{{
  "summary": "Lecture: Programming 1B",
  "start": {{
    "dateTime": "2025-08-05T08:00:00+02:00",
    "timeZone": "Africa/Johannesburg"
  }},
  "end": {{
    "dateTime": "2025-08-05T08:50:00+02:00", 
    "timeZone": "Africa/Johannesburg"
  }}
}}

REMEMBER AlWAYS:
- "Oct" ALWAYS means October
- Dates must always be converted to this format e.g.(5 August 2025 becomes 2025-08-05T08:00:00+02:00)

CSV DATA:
{csv_batch}
"""
    return prompt

def process_batch_with_retry(csv_batch, batch_num, structure_info, max_retries=3):
    """Process a batch with improved error handling and retry logic"""
    prompt = create_structured_prompt(csv_batch, structure_info)
    
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-001",
                contents=[prompt],
                config=types.GenerateContentConfig(
                    max_output_tokens=8192,
                    temperature=0.1,
                )
            )
            
            # Clean the response
            response_text = response.text.strip()
            response_text = re.sub(r'^```json\s*|\s*```$', '', response_text)
            
            # Parse JSON
            events = json.loads(response_text)
            print(f"✅ Batch {batch_num}: {len(events)} events processed")
            return events
            
        except json.JSONDecodeError as e:
            print(f"❌ Batch {batch_num}: JSON parsing failed - {e}")
            # Save for debugging
            with open(f'debug_batch_{batch_num}.txt', 'w') as f:
                f.write(f"Attempt {attempt + 1}\n")
                f.write(f"Error: {e}\n\n")
                f.write("Response text:\n")
                f.write(response_text)
            return []
            
        except Exception as e:
            error_str = str(e)
            
            # Check for quota exceeded error
            if "RESOURCE_EXHAUSTED" in error_str and "quota" in error_str.lower():
                print(f"❌ Batch {batch_num}: Daily quota exceeded")
                print("💡 Options:")
                print("   1. Wait until quota resets (usually midnight UTC)")
                print("   2. Upgrade to paid plan for higher limits")
                print("   3. Process remaining batches tomorrow")
                
                # Save unprocessed batch for later
                with open(f'unprocessed_batch_{batch_num}.csv', 'w') as f:
                    f.write(csv_batch)
                print(f"   📁 Batch saved as 'unprocessed_batch_{batch_num}.csv'")
                return []
                
            # Check for rate limiting (429 errors)
            elif "429" in error_str:
                wait_time = min(60 * (2 ** attempt), 300)  # Exponential backoff, max 5 minutes
                print(f"⏱️ Batch {batch_num}: Rate limited, waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
                time.sleep(wait_time)
                continue
                
            else:
                print(f"❌ Batch {batch_num}: API error - {e}")
                if attempt < max_retries - 1:
                    wait_time = 5 * (attempt + 1)  # Linear backoff for other errors
                    print(f"⏱️ Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    return []
    
    print(f"❌ Batch {batch_num}: Failed after {max_retries} attempts")
    return []

def main(csv_file_path, output_json="timetable_events.json"):
    csv_data = read_csv(csv_file_path)
    
    if csv_data is None:
        print("Failed to read CSV file. Exiting.")
        return
    
    # Parse the CSV structure first
    structure_info = parse_csv_structure(csv_data)
    
    # Split into weekly batches - IMPROVED LOGIC
    lines = csv_data.split('\n')
    batches = []
    current_batch = []
    found_first_week = False
    
    for line in lines:
        if is_week_header(line):
            found_first_week = True
            # If we have a current batch, save it before starting a new one
            if current_batch:
                batches.append('\n'.join(current_batch))
            # Start new batch with this week header
            current_batch = [line]
        elif found_first_week:  # Only add lines after we've found the first week header
            current_batch.append(line)
    
    # Don't forget the last batch
    if current_batch:
        batches.append('\n'.join(current_batch))
    
    print(f"Split timetable into {len(batches)} batches")
    
    # Debug: Print first few lines of each batch
    for i, batch in enumerate(batches, 1):
        first_line = batch.split('\n')[0]
        print(f"Batch {i}: Starts with '{first_line}'")
    
    # Process each batch
    all_events = []
    for i, batch in enumerate(batches, 1):
        print(f"\nProcessing batch {i}/{len(batches)}...")
        events = process_batch_with_retry(batch, i, structure_info)
        if events:
            print(f"📝 Adding {len(events)} events from batch {i} to collection")
            all_events.extend(events)
            print(f"📊 Total events so far: {len(all_events)}")
        else:
            print(f"⚠️ No events returned from batch {i}")
    
    print(f"\n📋 Final event count before saving: {len(all_events)}")
    
    # Save results
    with open(output_json, 'w') as f:
        json.dump(all_events, f, indent=2)
    
    print(f"\n🎉 Complete! Total events: {len(all_events)}")
    print(f"Results saved to: {output_json}")
    
    # Debug: Check what was actually saved
    try:
        with open(output_json, 'r') as f:
            saved_events = json.load(f)
        print(f"🔍 Verification: {len(saved_events)} events found in saved JSON file")
    except Exception as e:
        print(f"❌ Error reading back saved file: {e}")

# For testing the batching logic
def test_batching(csv_content):
    """Test function to see how the CSV gets split into batches"""
    lines = csv_content.split('\n')
    batches = []
    current_batch = []
    
    for line in lines:
        if is_week_header(line):
            if current_batch:
                batches.append('\n'.join(current_batch))
            current_batch = [line]
        elif current_batch:
            current_batch.append(line)
    
    if current_batch:
        batches.append('\n'.join(current_batch))
    
    print(f"Found {len(batches)} batches:")
    for i, batch in enumerate(batches, 1):
        lines_in_batch = len([l for l in batch.split('\n') if l.strip()])
        first_line = batch.split('\n')[0]
        print(f"  Batch {i}: {lines_in_batch} lines, starts with: '{first_line}'")
    
    return batches