import pandas as pd
import numpy as np
import math
import re
import calendar
from datetime import datetime, timezone, time, timedelta

class Event():
    summary = ""
    start_time = ""
    end_time = ""
    time_zone = ""

    def __init__(summary, start_time, end_time, time_zone):
        self.summary = summary
        self.start_time = start_time
        self.end_time = end_time
        self.time_zone = time_zone



# Path to the Excel file
file_path = "timetable.xlsx"

# Load the Excel file
df = pd.read_excel(file_path, header=14)  # Set the correct row as headers
df = df.dropna(how="all")
df.rename(columns={df.columns[0]: "Time"}, inplace=True)
#print(df.head(10))  # Check the new format

cols = list(df.head(10))

#print(cols)
raw_dates = []
rows_list = []

for row in df.values:
    row_list = row.tolist()  # Convert the row to a list
    if re.search("H00",row_list[0]):
        rows_list.append(row_list)
        #print(row_list)
    else:
        raw_dates.append(row_list)
#print(rows_list[0][0])

day_pattern = "Mon|Tue|Wed|Thu|Fri|Sat"
refined_dates = []

for week in raw_dates:
    for day in week:
        if re.search(day_pattern,day):
            refined_dates.append(day)

#print(refined_dates)
 

dates_on_days = {
    "Mon" : [],
    "Tue" : [],
    "Wed" : [],
    "Thu" : [],
    "Fri" : [],
    "Sat" : []
}

#date_dict = {date: [] for date in refined_dates}
date_dict = {}
for date in refined_dates:
    if re.search("Mon",date):
        #print(date)
        pass
    date_dict[date] = []

days_list = []
subjects = []

for key in dates_on_days:  # Just iterate over keys (no enumerate)
    for date in refined_dates:  # Loop through each string in the list
        matches = re.findall(fr"{key} \d{{1,2}} \w{{3}}", date)  
        dates_on_days[key].extend(matches)  # Store matched results


for x in range(len(rows_list)):
    rows_list[x] = rows_list[x][1:]

col = 0 #column
row = 0
day_name = "" #represents integer version of day of the week
count = 0 #how many times we have iterated over a day
session = 0 #number of sessions iterated over
date = ""
n = len(rows_list)

while col < len(rows_list[0]):  # Loop through columns
    row = 0  # Reset row for each column
    while row < n:  # Loop through rows
        if (session * 6) == (n * 6):
            break
        subject = rows_list[row][col]
        subjects.append(subject)
        subject = ""
        day_name = calendar.day_abbr[col]
        
        if (len(subjects) == 10) and (session > 0):
            #print(subjects)
            #print(date)
            date_dict[date] = subjects.copy()
            subjects.clear()  
            count += 1 
        
        # Ensure count does not exceed the length of dates_on_days[day_name]
        if day_name in dates_on_days:
            if count >= len(dates_on_days[day_name]):
                count = 0
            date = dates_on_days[day_name][count]
        
        row += 1  # Increment row to avoid  infinite loop
        session += 1
    col += 1      



def create_event(date_dict, dates_on_days):
    for i in range(len(dates_on_days["Mon"])):
        date = dates_on_days["Mon"]
        for j in range(len(date_dict)):
            if date_dict[i] == date:
                schedule = date_dict[i]
                for x in range(len(schedule)):
                    if not math.isnan(schedule[x]):
                        start_time = 8 + x
                        event = Event(schedule[x], start_time)

    
    
        
    event = {"summary": "", #TODO add value to this
            "start":{
                "dateTime": "",
                "timeZone": "Africa/Johannesburg"} ,
            "end":{
                "dateTime" : "", 
                "timeZone" : "Africa/Johannesburg"},
            "reminders": {
                "useDefault": False,  
                "overrides": [] }
            }
    return event

def get_date():
   pass 

def format_datetime(dt,date):
    current_year = str(datetime.now().year)
    date_obj = datetime.strptime(date + " " + current_year, "%a %d %b %Y")

    start_time = datetime.combine(date_obj, start_time(start_time, 0))
    end_time = start_time + timedelta(minutes=50)
    start_time = start_time.isoformat()
    return start_time, end_time
    

print()
create_event(date_dict,dates_on_days) 
