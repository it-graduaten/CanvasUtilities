from typing import List

from canvasapi.assignment import Assignment

from .custom_submission import CustomSubmission


class CustomStudent:
    canvas_id: int
    first_name: str
    last_name: str
    email: str
    number: str
    submissions: List[CustomSubmission]
    row_in_excel_file: int

    def __init__(self, canvas_id, first_name, last_name, email, number):
        self.canvas_id = canvas_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.number = number
        self.submissions = []
        self.row_in_excel_file = 0

    def add_submission(self, submission: CustomSubmission):
        self.submissions.append(submission)
        pass

    def to_dict(self):
        return {
            'canvas_id': self.canvas_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'submissions': [submission.to_dict() for submission in self.submissions],
            'row_in_excel_file': self.row_in_excel_file
        }

    def get_grade_for_assignment(self, assignment: Assignment):
        for submission in self.submissions:
            if submission.assignment_id == assignment.id:
                if submission.missing:
                    return "NA"
                return submission.points_scored
        return None

    def get_total_for_assignment_group(self, group):
        # If all submissions are missing, return "NA"
        all_missing = True
        total = 0
        for submission in self.submissions:
            if submission.omit_from_final_grade:
                continue
            if submission.points_scored is None:
                continue
            if submission.assignment_group_id == group.id:
                all_missing = False
                total += submission.points_scored
        if all_missing:
            return "NA"
        return total
