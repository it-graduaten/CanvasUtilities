from typing import List

from canvasapi.assignment import Assignment


class CustomAssignmentGroup:
    id: int
    name: str
    assignments: List[Assignment]
    group_weight: int

    def __init__(self, group_id: int, name: str, group_weight: int):
        self.id = group_id
        self.name = name
        self.assignments = []
        self.group_weight = group_weight

    def calculate_total_points_possible(self):
        total = 0

        print("There are " + str(len(list(self.assignments))) + " assignments in group " + self.name)

        for assignment in self.assignments:
            print("Assignment " + assignment.name + " has " + str(assignment.points_possible) + " points")
            if assignment.omit_from_final_grade:
                print("Assignment " + assignment.name + " is omitted from final grade")
                continue
            total += assignment.points_possible

        print("Total for group " + self.name + ": " + str(total) + " points")

        return total
