import pandas as pd
import re
from datetime import datetime

def reformat_timetable(csv_file_path, output_file_path=None):
    """
    Reformat the IIE timetable CSV into a clean Day,Time,Subject format with actual dates
    
    Args:
        csv_file_path: Path to the input CSV file
        output_file_path: Path for output CSV (optional, defaults to 'reformatted_timetable.csv')
    """
    
    # Read the CSV file
    df = pd.read_csv(csv_file_path, header=None)
    
    # Initialize list to store reformatted data
    reformatted_data = []
    
    # Define day columns (skip the first column which contains time slots)
    day_columns = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    
    # Variables to track current week's dates
    current_week_dates = {}
    
    # Process each row in the dataframe
    for index, row in df.iterrows():
        # Check if this row contains week header with dates
        first_cell = str(row.iloc[0])
        
        # Look for week headers like "Academic Week 3 FP1" in first column
        if 'Academic Week' in first_cell or 'Assess Week' in first_cell:
            # Extract dates from the row - they should be in columns 1-6
            for i, day in enumerate(day_columns):
                if i + 1 < len(row):
                    date_info = str(row.iloc[i + 1]).strip()
                    
                    # Parse dates like "Mon 4 Aug", "Tue 5 Aug", etc.
                    date_pattern = r'(\w{3})\s+(\d{1,2})\s+(\w{3})'
                    date_match = re.search(date_pattern, date_info)
                    
                    if date_match:
                        day_name = date_match.group(1)
                        day_num = date_match.group(2)
                        month_name = date_match.group(3)
                        
                        # Format as "Day DD Mon" (e.g., "Wed 6 Aug")
                        formatted_date = f"{day_name} {day_num} {month_name}"
                        current_week_dates[day] = formatted_date
            
            continue  # Skip to next row
        
        # Check if this row contains a time slot (format: XXH00 - XXH50)
        time_pattern = r'(\d{2}H\d{2})\s*-\s*(\d{2}H\d{2})'
        time_match = re.search(time_pattern, first_cell)
        
        if time_match:
            # Extract start and end times
            start_time_raw = time_match.group(1)
            end_time_raw = time_match.group(2)
            
            # Convert time format from XXH00 to XX:00
            start_time = start_time_raw.replace('H', ':')
            end_time = end_time_raw.replace('H', ':')
            
            # Format as start-end time
            time_formatted = f"{start_time}-{end_time}"
            
            # Check each day column for classes
            for i, day in enumerate(day_columns):
                if i + 1 < len(row):  # Make sure column exists
                    class_info = str(row.iloc[i + 1]).strip()

                    # Skip empty cells, NaN, or special entries
                    if (class_info and 
                        class_info != 'nan' and 
                        class_info != '' and
                        'SOCIAL MERIDIAN' not in class_info and
                        'WOMENS DAY' not in class_info and
                        'HERITAGE DAY' not in class_info and
                        'ASSESSMENT WEEK' not in class_info):

                        # Extract module code + optional WKSP + room - use search instead of match
                        subject_match = re.search(r'([A-Z]{4}\d{4}(?:\s+WKSP)?)\s+([A-Z0-9]+)', class_info)
                        
                        if subject_match:
                            module_code = subject_match.group(1).strip()
                            room_code = subject_match.group(2).strip()
                            subject = f"{module_code} {room_code}"

                            # Use actual date if available, otherwise fall back to day name
                            date_to_use = current_week_dates.get(day, day)

                            # Add to reformatted data
                            reformatted_data.append({
                                'Day': date_to_use,
                                'Time': time_formatted,
                                'Subject': subject
                            })
    
    # Create DataFrame from reformatted data
    result_df = pd.DataFrame(reformatted_data)
    
    # Sort by chronological order (parse dates for sorting)
    def parse_date_for_sorting(date_str):
        """Convert date strings like 'Mon 4 Aug' to sortable format"""
        if len(date_str.split()) == 3:
            try:
                day_name, day_num, month_name = date_str.split()
                
                # Map month abbreviations to numbers
                month_map = {
                    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
                }
                
                month_num = month_map.get(month_name, 8)  # Default to Aug if not found
                return (month_num, int(day_num))
            except:
                return (8, 1)  # Default fallback
        else:
            # Fallback for day names without dates
            day_order = {'Mon': (8, 1), 'Tue': (8, 2), 'Wed': (8, 3), 'Thu': (8, 4), 'Fri': (8, 5), 'Sat': (8, 6)}
            return day_order.get(date_str, (8, 7))
    
    if not result_df.empty:
        result_df['sort_key'] = result_df['Day'].apply(parse_date_for_sorting)
        result_df = result_df.sort_values(['sort_key', 'Time']).drop('sort_key', axis=1)
    
    # Remove duplicates
    result_df = result_df.drop_duplicates()
    
    # Save to file
    if output_file_path is None:
        output_file_path = 'reformatted_timetable.csv'
    
    result_df.to_csv(output_file_path, index=False)
    print(f"Reformatted timetable saved to: {output_file_path}")
    
    return result_df