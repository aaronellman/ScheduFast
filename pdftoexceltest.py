import fitz  # PyMuPDF
import pandas as pd
import re
import sys

def clean_and_combine_timetable(pdf_path, excel_path):
    try:
        doc = fitz.open(pdf_path)
        all_tables = []
        
        # Process each page
        for page in doc:
            tables = page.find_tables()
            if tables.tables:
                # Get the first table (assuming one main table per page)
                df = tables[0].to_pandas()
                
                # Clean the dataframe - remove completely empty rows and columns
                df = df.dropna(how='all').dropna(axis=1, how='all')
                
                # Reset the index after dropping rows
                df.reset_index(drop=True, inplace=True)
                
                all_tables.append(df)
        
        doc.close()
        
        if not all_tables:
            print("No tables found in the PDF")
            return
        
        # Combine tables vertically
        if len(all_tables) > 1:
            # For second page, we want to align with first page's structure
            time_pattern = r'\d{2}H\d{2}\s*-\s*\d{2}H\d{2}'  # More flexible time pattern
            
            # Process first page
            first_page = all_tables[0]
            first_page_data = first_page[first_page.iloc[:, 0].str.contains(time_pattern, na=False, regex=True)]
            
            # Process second page
            second_page = all_tables[1]
            second_page_data = second_page[second_page.iloc[:, 0].str.contains(time_pattern, na=False, regex=True)]
            
            # Combine data
            combined_df = pd.concat([first_page_data, second_page_data], ignore_index=True)
            
            # Try to preserve headers from first page
            header_rows = first_page[~first_page.iloc[:, 0].str.contains(time_pattern, na=False, regex=True)]
            if not header_rows.empty:
                combined_df = pd.concat([header_rows, combined_df], ignore_index=True)
        else:
            combined_df = all_tables[0]
        
        # Try to use xlsxwriter for formatting, fall back to basic Excel writer
        try:
            # Save with formatting if xlsxwriter is available
            with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
                combined_df.to_excel(writer, index=False, sheet_name='Timetable')
                
                workbook = writer.book
                worksheet = writer.sheets['Timetable']
                
                # Format header
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#D7E4BC',
                    'border': 1
                })
                
                # Apply header format
                for col_num, value in enumerate(combined_df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                
                # Auto-adjust columns' width
                for i, col in enumerate(combined_df.columns):
                    column_len = max(
                        combined_df[col].astype(str).map(len).max(),
                        len(str(col))
                    )
                    worksheet.set_column(i, i, min(column_len + 2, 50))  # Cap at 50 width
                
                print(f"Successfully saved formatted timetable to {excel_path}")
        
        except ImportError:
            # Fall back to basic Excel writer if xlsxwriter not available
            combined_df.to_excel(excel_path, index=False)
            print(f"Saved basic timetable to {excel_path} (install xlsxwriter for formatting)")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}", file=sys.stderr)

if __name__ == "__main__":
    pdf_path = "timetable.pdf"  # Replace with your PDF file path
    excel_path = "aligned_timetable.xlsx"  # Output Excel file path
    clean_and_combine_timetable(pdf_path, excel_path)