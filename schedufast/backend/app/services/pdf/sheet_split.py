import pandas as pd
from pathlib import Path

def split_sheets(input_file, output_dir="."): 
    sheets = pd.read_excel(input_file, sheet_name=None)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)  # ensure folder exists
    files = []

    for sheet_name, df in sheets.items():
        output_file = output_dir / f"{sheet_name}.xlsx"
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        print(f"Saved {sheet_name} to {output_file}")
        files.append(output_file)

    print(f"Now returning files: {files}\n")
    return files