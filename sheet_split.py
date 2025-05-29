import pandas as pd



def split_sheets(input_file): 

    sheets = pd.read_excel(input_file, sheet_name=None)
    files = []

    for sheet_name, df in sheets.items():
        output_file = f"{sheet_name}.xlsx"

        df.to_excel(output_file, index = False)
        print(f"Saved {sheet_name} to {output_file}")

        files.append(output_file)

    filenames = files.copy()
    print(f"Now returning files: {filenames}")
    print()
    return filenames 

split_sheets("timetable_converted.xlsx")
