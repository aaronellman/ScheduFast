import pandas as pd
#possible solutions: delete sheets that dont contain that files name
def split_sheets(input_file): 
    sheets = pd.read_excel(input_file, sheet_name=None)
    files = []

    for sheet_name, df in sheets.items():
        output_file = f"{sheet_name}.xlsx"
        # Write only this DataFrame to a new file, with the correct sheet name
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        print(f"Saved {sheet_name} to {output_file}")
        files.append(output_file)

    print(f"Now returning files: {files}")
    print()
    return files

split_sheets("timetable_converted.xlsx")
