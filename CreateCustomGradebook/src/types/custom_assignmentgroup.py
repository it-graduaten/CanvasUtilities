from typing import List

from canvasapi.assignment import Assignment


class CustomAssignmentGroup:
    id: int
    name: str
    assignments: List[Assignment]

    def __init__(self, group_id: int, name: str):
        self.id = group_id
        self.name = name
        self.assignments = []

    def calculate_total_points_possible(self):
        total = 0
        for assignment in self.assignments:
            if assignment.omit_from_final_grade:
                continue
            total += assignment.points_possible
        return total
