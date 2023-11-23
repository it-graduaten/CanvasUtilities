from canvasapi import Canvas
import os
import xlsxwriter

OUTPUT_FILE = 'canvas_data.xlsx'


class DataCollector:
    course_obj = None

    def __init__(self):
        # Ask the user for a Canvas Course ID
        course_id = input("Enter the Canvas Course ID: ")

        # Ask the user for a canvas api key, if not set as environment variable
        api_key = input("Geef de Canvas API key (laat leeg voor environment variable te gebruiken): ")
        if api_key == "":
            api_key = os.environ.get("CANVAS_API_KEY")

        # Create a canvas object
        canvas_obj = Canvas("https://thomasmore.instructure.com/", api_key)
        self.course_obj = canvas_obj.get_course(course_id)

    def get_assignments(self):
        # Get all assignment groups in the course with their assignments
        canvas_assignment_groups = self.course_obj.get_assignment_groups(include=['assignments'])
        # Write the assignment groups to the output file
        workbook = xlsxwriter.Workbook(OUTPUT_FILE)
        worksheet = workbook.add_worksheet("Assignment Groups")
        worksheet.write_row(0, 0, ["Assignment group name"])
        for index, assignment_group in enumerate(canvas_assignment_groups):
            worksheet.write_row(index + 1, 0, [assignment_group.name])
        # Create a worksheet for the assignments
        worksheet = workbook.add_worksheet("Assignments")
        worksheet.write_row(0, 0, ["Assignment name", "Assignment group name"])
        for index, assignment_group in enumerate(canvas_assignment_groups):
            for assignment in assignment_group.assignments:
                worksheet.write_row(index + 1, 0, [assignment['name'], assignment_group.name])
        workbook.close()

    def get_sections(self):
        # Get all sections in the course with their students
        canvas_sections = self.course_obj.get_sections(include=['students'])
        # Write the sections to the output file
        workbook = xlsxwriter.Workbook(OUTPUT_FILE)
        worksheet = workbook.add_worksheet("Sections")
        worksheet.write_row(0, 0, ["Section name"])
        for index, section in enumerate(canvas_sections):
            # If the name contains a '|', skip it
            if '|' in section.name:
                continue
            worksheet.write_row(index + 1, 0, [section.name])
        # Create a worksheet for the students
        worksheet = workbook.add_worksheet("Students")
        worksheet.write_row(0, 0, ["Student name", "Section name"])
        for index, section in enumerate(canvas_sections):
            # If the name contains a '|', skip it
            if '|' in section.name:
                continue
            # If the section has no students, skip it
            if not section.students:
                continue
            for student in section.students:
                worksheet.write_row(index + 1, 0, [student['name'], section.name])
        workbook.close()
