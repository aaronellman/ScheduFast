# cd backend
from google import genai
from google.genai import types
import json
import re
import csv
from datetime import datetime, timedelta

client = genai.Client(api_key="AIzaSyBTv7nMb5J21Vjj0fLNiRiw5NelQvV5x4I")

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
        if 'Academic Week' in line or 'Assess Week' in line:
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
        if cells[0]:  # If first cell has a time
            time_slots.append(cells[0])
    
    return {
        'header': header,
        'day_headers': day_headers,
        'time_slots': time_slots,
        'schedule_lines': lines[schedule_start:]
    }

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

CSV DATA:
{csv_batch}
"""
    return prompt

def process_batch_with_retry(csv_batch, batch_num, structure_info):
    """Process a batch with improved error handling"""
    prompt = create_structured_prompt(csv_batch, structure_info)
    
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
            f.write(f"Error: {e}\n\n")
            f.write("Response text:\n")
            f.write(response_text)
        return []
    except Exception as e:
        print(f"❌ Batch {batch_num}: API error - {e}")
        return []

def main(csv_file_path):
    csv_data = read_csv(csv_file_path)
    
    if csv_data is None:
        print("Failed to read CSV file. Exiting.")
        return
    
    # Parse the CSV structure first
    structure_info = parse_csv_structure(csv_data)
    
    # Split into weekly batches
    lines = csv_data.split('\n')
    batches = []
    current_batch = []
    in_schedule = False
    
    for line in lines:
        if 'Academic Week' in line or 'Assess Week' in line:
            in_schedule = True
            if current_batch:
                batches.append('\n'.join(current_batch))
                current_batch = []
        elif not in_schedule:
            continue
            
        current_batch.append(line)
        
        # If we hit a new week, create a batch
        if line.startswith('Week ') and len(current_batch) > 1:
            batches.append('\n'.join(current_batch))
            current_batch = [current_batch[0]]  # Keep the header
    
    if current_batch:
        batches.append('\n'.join(current_batch))
    
    print(f"Split timetable into {len(batches)} batches")
    
    # Process each batch
    all_events = []
    for i, batch in enumerate(batches, 1):
        print(f"\nProcessing batch {i}/{len(batches)}...")
        events = process_batch_with_retry(batch, i, structure_info)
        if events:
            all_events.extend(events)
    
    # Save results
    with open('timetable_events.json', 'w') as f:
        json.dump(all_events, f, indent=2)
    
    print(f"\n🎉 Complete! Total events: {len(all_events)}")
    print(f"Results saved to: timetable_events.json")

main()