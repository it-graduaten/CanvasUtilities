from canvasapi import Canvas
import os
import xlsxwriter

OUTPUT_FILE = 'canvas_data.xlsx'


def create_excel_file(canvas_assignment_groups, sections_with_students):
    workbook = xlsxwriter.Workbook(OUTPUT_FILE)
    worksheet = workbook.add_worksheet("Assignment Groups")
    worksheet.write_row(0, 0, ["Assignment group name"])
    for index, assignment_group in enumerate(canvas_assignment_groups):
        print(f"Writing assignment group {assignment_group.name} to excel file")
        worksheet.write_row(index + 1, 0, [assignment_group.name])
    # Create a worksheet for the assignments
    worksheet = workbook.add_worksheet("Assignments")
    worksheet.write_row(0, 0, ["Assignment name", "Assignment group name"])
    for assignment_group in canvas_assignment_groups:
        for index, assignment in enumerate(assignment_group.assignments):
            print(f"Writing assignment {assignment['name']} to excel file")
            worksheet.write_row(index + 1, 0, [assignment['name'], assignment_group.name])
    # Create a worksheet for the sections
    worksheet = workbook.add_worksheet("Sections")
    worksheet.write_row(0, 0, ["Section name"])
    for index, section in enumerate(sections_with_students):
        # If the name contains a '|', skip it
        if '|' in section.name:
            continue
        worksheet.write_row(index + 1, 0, [section.name])
    # Create a worksheet for the students
    worksheet = workbook.add_worksheet("Students")
    worksheet.write_row(0, 0, ["Student name", "Section name"])
    student_counter = 0
    for section in sections_with_students:
        print("Writing section " + section.name + " to excel file")
        # If the name contains a '|', skip it
        if '|' in section.name:
            continue
        # If the section has no students, skip it
        if not section.students:
            continue
        for index, student in enumerate(section.students):
            print(f"Writing student {student['name']} to excel file")
            worksheet.write_row(student_counter + 1, 0, [student['name'], section.name])
            student_counter += 1
    workbook.close()


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

    def collect_data(self):
        canvas_assignment_groups = self.get_assignments_with_groups()
        sections_with_students = self.get_sections()
        create_excel_file(canvas_assignment_groups, sections_with_students)

    def get_assignments_with_groups(self):
        # Get all assignment groups in the course with their assignments
        canvas_assignment_groups = self.course_obj.get_assignment_groups(include=['assignments'])
        return canvas_assignment_groups

    def get_sections(self):
        # Get all sections in the course with their students
        canvas_sections = self.course_obj.get_sections(include=['students'])
        return canvas_sections
