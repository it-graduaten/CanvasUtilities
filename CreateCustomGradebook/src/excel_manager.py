import xlsxwriter
from typing import List
from .types.custom_assignmentgroup import CustomAssignmentGroup
from .types.custom_student import CustomStudent


class ExcelManager:
    color_na: str = '#FFC7CE'
    color_empty_cell = '#FFF'

    def __init__(self, filename):
        self.workbook = xlsxwriter.Workbook(filename)
        self.worksheet = self.workbook.add_worksheet()
        self.column_counter = 0
        self.na_format = self.workbook.add_format({'bg_color': '#FFC7CE'})
        self.student_dict = {}
        self.assignment_group_dict = {}

    def write_students_to_excel(self, students):
        self.worksheet.write(0, 0, "Voornaam")
        self.worksheet.write(0, 1, "Achternaam")
        self.worksheet.write(0, 2, "Email")
        self.worksheet.write(0, 3, "Studentennummer")

        for index, student in enumerate(students):
            self.worksheet.write(index + 2, 0, student.first_name)
            self.worksheet.write(index + 2, 1, student.last_name)
            self.worksheet.write(index + 2, 2, student.email)
            self.worksheet.write(index + 2, 3, student.number)

            student.row_in_excel_file = index + 2

        self.column_counter = 4

    def write_submissions_to_excel(self, assignment_group, assignment, submissions):
        self.worksheet.write(0, self.column_counter, assignment.name)
        self.worksheet.write(1, self.column_counter, assignment.points_possible)

        # Check if the assignment is mandatory and thus should be
        assignment_mandatory = assignment.omit_from_final_grade is False

        # Create a points_possible_assignment_group_{assignment_group.id} key in the assignemnt group dict if it doesn't exist yet
        if f'points_possible_assignment_group_{assignment_group.id}' not in self.assignment_group_dict:
            self.assignment_group_dict[f'points_possible_assignment_group_{assignment_group.id}'] = 0

        # Add the points possible for this assignment to the total for this assignment_group in the assignment_group_dict if the assignment is mandatory
        if assignment_mandatory:
            self.assignment_group_dict[
                f'points_possible_assignment_group_{assignment_group.id}'] += assignment.points_possible

        for submission in submissions:
            if submission.user_id not in self.student_dict:
                continue

            # Get the row number for this student
            row_number = self.student_dict[submission.user_id]['excel_row']
            # Create a total_assignment_group_{assignment_group.id} key in the student_dict if it doesn't exist yet
            if f'total_assignment_group_{assignment_group.id}' not in self.student_dict[submission.user_id]:
                self.student_dict[submission.user_id][f'total_assignment_group_{assignment_group.id}'] = 0

            value_to_write = submission.score
            format_to_write = None
            if submission.missing:
                value_to_write = "NA"
                format_to_write = self.na_format

            self.worksheet.write(row_number, self.column_counter, value_to_write, format_to_write)

            # Add the score to the total for this assignment_group in the total_dict if score is not None and 
            if assignment_mandatory and submission.score is not None:
                self.student_dict[submission.user_id][
                    f'total_assignment_group_{assignment_group.id}'] += submission.score

        self.column_counter += 1

    def write_totals_for_assignment_groups(self, assignment_groups):
        for assignment_group in assignment_groups:
            self.worksheet.write(0, self.column_counter, f'Total {assignment_group.name}')
            # Format as percentage
            self.worksheet.write(1, self.column_counter, assignment_group.group_weight / 100,
                                 self.workbook.add_format({'num_format': '0%'}))

            for student_id, student in self.student_dict.items():
                if f'total_assignment_group_{assignment_group.id}' not in student:
                    continue

                row_number = student['excel_row']
                # Get the total for this assignment_group for this student
                total = student[f'total_assignment_group_{assignment_group.id}']
                # Get the points possible for this assignment_group
                points_possible = self.assignment_group_dict[f'points_possible_assignment_group_{assignment_group.id}']
                # Get the percentage for this assignment_group for this student
                percentage = total / points_possible
                # Write the percentage to the Excel sheet
                self.worksheet.write(row_number, self.column_counter, percentage,
                                     self.workbook.add_format({'num_format': '0%'}))

            self.column_counter += 1

    def save_workbook(self):
        self.workbook.close()

    def create_gradebook(self, assignment_groups: List[CustomAssignmentGroup], students: List[CustomStudent]):
        for group in assignment_groups:
            for assignment in group.assignments:
                self.worksheet.write(0, self.column_counter, assignment.name)
                self.worksheet.write(1, self.column_counter, assignment.points_possible)

                for student in students:
                    grade = student.get_grade_for_assignment(assignment)
                    self.worksheet.write(student.row_in_excel_file, self.column_counter,
                                         grade)

                self.column_counter += 1

        for group in assignment_groups:
            self.worksheet.write(0, self.column_counter, f'Groepstotaal - {group.name}')
            self.worksheet.write(1, self.column_counter, group.calculate_total_points_possible())

            for student in students:
                self.worksheet.write(student.row_in_excel_file, self.column_counter,
                                     student.get_total_for_assignment_group(group))

            self.column_counter += 1
        pass
