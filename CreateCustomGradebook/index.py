import os
from canvasapi import Canvas
import xlsxwriter

from src.canvas_manager import CanvasManager
from src.excel_manager import ExcelManager

if __name__ == "__main__":
    course_id = input("Geef het course id: ")
    api_key = input("Geef de Canvas API key (laat leeg voor environment variable te gebruiken): ")

    if api_key == "":
        api_key = os.environ.get("CANVAS_API_KEY")

    canvas_manager = CanvasManager("https://thomasmore.instructure.com/", api_key)
    canvas_manager.get_course(course_id)

    students = canvas_manager.get_students_in_course()
    assignment_groups = canvas_manager.get_assignment_groups()

    for assignment_group in assignment_groups:
        assignments = canvas_manager.get_assignments_for_group(assignment_group.id)
        assignment_group.assignments = assignments
        for assignment in assignments:
            submissions = canvas_manager.get_submissions_for_assignment(assignment)
            canvas_manager.match_submissions_to_students(assignment_group.id, assignment, submissions, students)

    excel_manager = ExcelManager("gradebook.xlsx")
    excel_manager.write_students_to_excel(students)
    excel_manager.create_gradebook(assignment_groups, students)
    excel_manager.save_workbook()
