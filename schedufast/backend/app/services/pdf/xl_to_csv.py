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

def main():
    # Default file names - you can change these
    excel_file = "Table_1.xlsx"
    csv_file = "timetable.csv"
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        excel_file = sys.argv[1]
        if len(sys.argv) > 2:
            csv_file = sys.argv[2]
        else:
            # Auto-generate CSV name from Excel name
            base_name = os.path.splitext(excel_file)[0]
            csv_file = f"{base_name}.csv"
    
    print("🔄 Excel to CSV Converter")
    print(f"Input:  {excel_file}")
    print(f"Output: {csv_file}")
    print("-" * 40)
    
    # DEBUG: Show current working directory and files
    print(f"🔍 Current directory: {os.getcwd()}")
    print("📁 Files in current directory:")
    try:
        files = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.xls', '.csv'))]
        for file in sorted(files):
            size = os.path.getsize(file)
            print(f"   {file} ({size} bytes)")
        
        if not files:
            print("   No Excel or CSV files found")
    except Exception as e:
        print(f"   Error listing files: {e}")
    
    print(f"🔍 Looking for: {os.path.abspath(excel_file)}")
    print(f"📂 File exists: {os.path.exists(excel_file)}")
    print(f"📂 Is file: {os.path.isfile(excel_file) if os.path.exists(excel_file) else 'N/A'}")
    print("-" * 40)
    
    result = convert_excel_to_csv(excel_file, csv_file)
    
    if result:
        print("\n✅ Conversion successful!")
    else:
        print("\n❌ Conversion failed!")

if __name__ == "__main__":
    main()