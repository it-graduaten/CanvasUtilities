import pandas as pd
import openpyxl
import os
from openpyxl.styles.colors import WHITE, RGB

__old_rgb_set__ = RGB.__set__


def __rgb_set_fixed__(self, instance, value):
    try:
        __old_rgb_set__(self, instance, value)
    except ValueError as e:
        if e.args[0] == 'Colors must be aRGB hex values':
            __old_rgb_set__(self, instance, WHITE)  # Change default color here
            
RGB.__set__ = __rgb_set_fixed__

# Get the name of files in the files directory
for file in os.listdir('input_files'):
    if file.endswith('.csv'):
        csv_file = file
    if file.endswith('.xlsx'):
        xlsx_file = file
        
# Read the csv file to a dataframe
csv_data = pd.read_csv(f'input_files/{csv_file}')
    
# Print all columns in the csv file with a number
for i, column in enumerate(csv_data.columns):
    print(f'{i+1}. {column}')    
# Ask the user for the column to be written to the xlsx file
column_number = int(input('Enter the number of the column you want to write to the xlsx file: '))
# Ask for confirmation
column_name = csv_data.columns[column_number-1]
print(f'You chose column {column_number}: {column_name}')
confirmation = input(f'Are you sure you want to write column {column_number} to the xlsx file? (y/n): ')
if confirmation.lower() == 'y':
    # Iterate the rows of the xlsx file in the "Beoordelingen" sheet (which already exists)
    workbook = openpyxl.load_workbook(f'input_files/{xlsx_file}')
    worksheet = workbook.active
    # For every row in the xlsx file, starting from row 3
    for i, row in enumerate(worksheet.iter_rows()):
        if i >= 2:
            # Get the studnr from the 'C' column
            studnr = row[2].value
            # Find the row in the csv file where 'SIS Login ID' contains the studnr
            csv_row = csv_data[csv_data['SIS Login ID'].astype(str).str.contains(str(studnr))]
            print("csv_row", csv_row)
            # If the row is not found, skip to the next row
            if csv_row.empty:
                continue
            # Get the value from the column the user chose
            column_value = csv_row[column_name].values[0]
            # Replace ',' with '.' so we can convert the value to a decimal number
            column_value = column_value.replace(',', '.')
            # Column value will be a decimal number (max 100), convert it to a decimal number
            column_value = float(column_value)
            # Divide the number by 5 so we get a score between 0 and 20
            column_value = column_value / 5
            # Round it to have no decimal places
            column_value = round(column_value)            
            print("column_value", column_value)
            # Write the random number to the xlsx file in the 'L' column
            worksheet[f'L{i+1}'] = column_value
    # Save the xlsx file
    workbook.save(f'output_files/{xlsx_file}')
    print('The column has been written to the xlsx file.')
else:
    print("Stopping")
    
