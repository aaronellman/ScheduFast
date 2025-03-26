while row < n:
    if (session * 6) == (n * 6):
        break
    if row == n:
        col += 1
        row = 0
    if (session % 9 == 0) and (session > 0):
        date_dict[date].append(subjects.copy())
        subjects.clear()
        count += 1
    
    session += 1
    
    subject = rows_list[row][col]
    subjects.append(subject)
    day_name = calendar.day_abbr[col]
    if day_name in dates_on_days:
        if count >= len(dates_on_days):
            count = 0
        date = dates_on_days[day_name][count]
    row += 1