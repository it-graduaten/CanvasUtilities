from canvasapi.assignment import Assignment
from canvasapi.submission import Submission


class CustomSubmission:
    assignment_group_id: int
    assignment_id: int
    assignment_name: str
    points_possible: int
    points_scored: int
    missing: bool
    omit_from_final_grade: bool

    def __init__(self, assignment_group_id: int, assignment: Assignment, submission: Submission):
        self.assignment_group_id = assignment_group_id
        self.assignment_id = assignment.id
        self.assignment_name = assignment.name
        self.points_possible = assignment.points_possible
        self.points_scored = submission.score
        self.missing = (submission.missing
                        or submission.workflow_state == "unsubmitted")
        self.omit_from_final_grade = assignment.omit_from_final_grade

    def to_dict(self):
        return {
            'assignment_group_id': self.assignment_group_id,
            'assignment_id': self.assignment_id,
            'assignment_name': self.assignment_name,
            'points_possible': self.points_possible,
            'points_scored': self.points_scored,
            'missing': self.missing,
            'omit_from_final_grade': self.omit_from_final_grade
        }
