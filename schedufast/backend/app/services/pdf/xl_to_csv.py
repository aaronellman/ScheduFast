import pandas as pd
import os
import sys

def convert_excel_to_csv(excel_file_path, csv_file_path=None):
    """Convert Excel file to CSV format"""
    
    if csv_file_path is None:
        # Auto-generate CSV filename
        base_name = os.path.splitext(excel_file_path)[0]
        csv_file_path = f"{base_name}.csv"
    
    try:
        # Check if Excel file exists
        if not os.path.exists(excel_file_path):
            print(f"❌ Error: Excel file '{excel_file_path}' not found")
            return None
        
        # Read Excel file
        print(f"📖 Reading Excel file: {excel_file_path}")
        
        # Try to read the first sheet
        df = pd.read_excel(excel_file_path, sheet_name=0)
        
        print(f"✅ Excel loaded: {df.shape[0]} rows, {df.shape[1]} columns")
        
        # Save as CSV
        df.to_csv(csv_file_path, index=False, encoding='utf-8')
        
        print(f"💾 CSV saved: {csv_file_path}")
        return csv_file_path
        
    except ImportError:
        print("❌ Error: pandas library not installed")
        print("Install with: pip install pandas openpyxl")
        return None
    except Exception as e:
        print(f"❌ Error converting Excel to CSV: {e}")
        return None

def main(excel_file, csv_file=None):
    print("🔄 Excel to CSV Converter")
    print(f"Input:  {excel_file}")
    
    if csv_file is None:
        # Auto-generate CSV name
        base_name = os.path.splitext(excel_file)[0]
        csv_file = f"{base_name}.csv"

    print(f"Output: {csv_file}")
    print("-" * 40)

    result = convert_excel_to_csv(excel_file, csv_file)

    if result:
        print("\n✅ Conversion successful!")
    else:
        print("\n❌ Conversion failed!")
    
    return result

if __name__ == "__main__":
    main()