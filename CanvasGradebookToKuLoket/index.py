import os
import math
import xlsxwriter
import pandas as pd
import openpyxl

def get_csv_filename():
    """
    Get the name of the 'csv' file in the input folder, throws an exception if no csv file is found
    """
    csv_file = None
    for file in os.listdir("input"):
        if file.endswith(".csv"):
            csv_file = file
            break
    if csv_file is None:
        raise Exception("No csv file found in the input folder")
    return csv_file


def get_xlsx_filename():
    """
    Get the name of the 'xlsx' file in the input folder, throws an exception if no xlsx file is found
    """
    xlsx_file = None
    for file in os.listdir("input"):
        if file.endswith(".xlsx"):
            xlsx_file = file
            break
    if xlsx_file is None:
        raise Exception("No xlsx file found in the input folder")
    return xlsx_file


def get_student_array_from_xlsx(xlsx_filename):
    students = []
    # Open the xlsx file using openpyxl
    wb = openpyxl.load_workbook(f"input/{xlsx_filename}")
    # Get the first sheet
    sheet = wb.active
    # Iterate all rows, skipping the first 2 rows
    for row in sheet.iter_rows(min_row=3):
        student = {
            "first_name": row[1].value,
            "last_name": row[0].value,
            "number": row[2].value,
            "score": None
        }
        students.append(student)
    wb.close()
    return students


def fill_student_points_using_csv(csv_filename, students):
    # Read the csv file using pandas
    df = pd.read_csv(f"input/{csv_filename}")
    # Find the column index of the column that starts with 'Unposted Current Score'
    score_column_index = None
    for column in df.columns:
        if column.startswith("Unposted Current Score"):
            score_column_index = df.columns.get_loc(column)
            break
    # Find the column index of the column that starts with 'SIS User ID'
    stud_id_column_index = None
    for column in df.columns:
        if column.startswith("SIS User ID"):
            stud_id_column_index = df.columns.get_loc(column)
            break
    # For every student, find the score in the csv file. A student can be matched when the student number is in the 'SIS User ID' column
    for index, row in df.iterrows():
        if (index == 0 or index == 1 or index == 2):
            continue
        score = None
        stud_id = None

        # Get the score
        score = row.iloc[score_column_index]
        # Get the student id
        stud_id = row.iloc[stud_id_column_index]

        print(f"Found score: {score} for student: {stud_id}")
        try:
            for student in students:
                if student["number"] in stud_id:
                    student["score"] = score
        except Exception as e:
            print(e)
                    
    return students




if __name__ == "__main__":
    csv_filename = get_csv_filename()
    xlsx_filename = get_xlsx_filename()
    students = get_student_array_from_xlsx(xlsx_filename)
    print(students)
    students = fill_student_points_using_csv(csv_filename, students)
    print(students)










# # Read the the csv into a pandas dataframe
# df = pd.read_csv(f"input/{csv_file}")
# # Find the column index of the column that starts with 'Unposted Current Score'
# score_column_index = None
# for column in df.columns:
#     if column.startswith("Unposted Current Score"):
#         score_column_index = df.columns.get_loc(column)
#         break
# # Find the column index of the column that starts with 'SIS User ID'
# stud_id_column_index = None
# for column in df.columns:
#     if column.startswith("SIS User ID"):
#         stud_id_column_index = df.columns.get_loc(column)
#         break

# print(f"Found score column index: {score_column_index}")
# print(f"Found student id column index: {stud_id_column_index}")

# scores = []

# # For every row in the csv file skipping the header row, save the 'SIS User ID' and the column that starts with 'Unposted Current Score'
# for index, row in df.iterrows():
#     if (index == 0 or index == 1 or index == 2):
#         continue
#     score = None
#     stud_id = None

#     # Get the score
#     score = row.iloc[score_column_index]
#     # Get the student id
#     stud_id = row.iloc[stud_id_column_index]

#     print(f"Found score: {score} for student: {stud_id}")

#     if score is not None and stud_id is not None:
#         try:
#             # Remove the 'S_' from the student id
#             stud_id = stud_id.replace("S_", "")
#             # Append to the scores list
#             scores.append({"id": stud_id, "score": score})
#         except Exception as e:
#             print(e)

# print(scores)

# # Open the xlsx file
# excel_df = pd.read_excel(f"input/{xlsx_file}")

