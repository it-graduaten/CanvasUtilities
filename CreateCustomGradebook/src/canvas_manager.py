from canvasapi import Canvas
from typing import List

from canvasapi.assignment import Assignment
from canvasapi.submission import Submission
from .types.custom_submission import CustomSubmission
from .types.custom_student import CustomStudent
from .types.custom_assignmentgroup import CustomAssignmentGroup


class CanvasManager:
    def __init__(self, api_url, api_key):
        self.canvas = Canvas(api_url, api_key)
        self.course = None

    def get_course(self, course_id):
        self.course = self.canvas.get_course(course_id)

    def get_students_in_course(self) -> List[CustomStudent]:
        students = self.course.get_users(enrollment_type=['student'])
        # Split the name of the student in first and last name
        student_list = []
        for student in students:
            parts = student.sortable_name.split(",")
            first_name = parts[1].strip()
            last_name = parts[0].strip()
            student_list.append(CustomStudent(student.id, first_name, last_name, student.email, student.sis_user_id))
        return student_list

    def get_assignment_groups(self) -> List[CustomAssignmentGroup]:
        assignment_groups = self.course.get_assignment_groups()
        assignment_group_list = []
        for assignment_group in assignment_groups:
            assignment_group_list.append(
                CustomAssignmentGroup(assignment_group.id, assignment_group.name, assignment_group.group_weight))
        return assignment_group_list

    @staticmethod
    def get_submissions_for_assignment(assignment):
        submissions = assignment.get_submissions()
        return submissions

    def get_assignments_for_group(self, assignment_group_id):
        assignments = self.course.get_assignments_for_group(assignment_group_id)
        return assignments

    @staticmethod
    def match_submissions_to_students(assignment_group_id: int, assignment: Assignment, submissions: List[Submission],
                                      students: List[CustomStudent]):
        for submission in submissions:
            for student in students:
                if submission.user_id == student.canvas_id:
                    student.add_submission(CustomSubmission(assignment_group_id, assignment, submission))
