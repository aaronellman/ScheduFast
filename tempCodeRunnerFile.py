import pandas as pd
import numpy as np
import math
import re
import calendar
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
        print(date)
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
        if row == n:
            col += 1
            row = 0
        if (len(subjects) == 10) and (session > 0):
            #print(subjects)
            #print(date)
            date_dict[date] = subjects.copy()
            subjects.clear()  # Clear subjects after appending
            count = (session // 9) 
        
        # Ensure count does not exceed the length of dates_on_days[day_name]
        if day_name in dates_on_days:
            if count >= len(dates_on_days[day_name]):
                count = 0
            date = dates_on_days[day_name][count]
        
        row += 1  # Increment row to avoid  infinite loop
        session += 1

    col += 1  # Increment column to move to the next column

print(date_dict)  

"""count = 0
n = len(rows_list[0])
#print(date_dict)
#print()
for col in range(n):
    for row in range(len(rows_list)):
        subject = rows_list[row][col]
        #print(subject)
        #print()
        if count % 9 == 0 and count != 0:
            tot = (count // 9) 
            if tot < len(refined_dates):  # Prevent out-of-range errors
                date = dates_on_days[days_list[tot]][tot]
                date_dict[date] = temp_string.split("#")
                temp_string = ""
            
        count += 1
        if pd.isna(subject):
            temp_string += "#NaN" if temp_string else "NaN"
        else:
            temp_string += f"#{subject}" if temp_string else subject

print(date_dict)            




# Print the dictionary
for date, values in date_dict.items():
    #print(f"{date}: {values}")
    pass


        
class Lectures:
    
    def __init__(self,date,time,module,location):
        self.date = date
        self.time = time
        self.module = module
        self.location = location"""
