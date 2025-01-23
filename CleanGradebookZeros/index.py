import os
from canvasapi import Canvas
import datetime

if __name__ == "__main__":
    # Get the canvas api key from the environment variables
    canvas_api_key = os.environ.get("CANVAS_API_KEY")
    # Login to canvas
    canvas = Canvas("https://thomasmore.instructure.com/", canvas_api_key)
    # Get the course
    canvas_course_id = input("Enter the Canvas course ID: ")
    course = canvas.get_course(canvas_course_id)
    # Get all assignments in the course
    assignments = course.get_assignments()
    # Loop all assignments
    for assignment in assignments:
        # Get the deadline of the assignment
        deadline = assignment.due_at # This is a string
        print(f"Working on assignment: {assignment.name} which is due at {deadline}")
        # Check if the assignment will be omitted from the final grade
        if assignment.omit_from_final_grade:
            continue
        # Check if the assignment is published
        if not assignment.published:
            continue
        # If no deadline is set, skip the assignment
        if deadline is None:
            continue
        # Check the deadline being in the past
        if deadline > datetime.datetime.now().isoformat():
            continue
        # Get all submissions for the assignment
        submissions = assignment.get_submissions()
        # Loop all submissions
        for submission in submissions:
            # Skip if the submission has been graded
            if submission.workflow_state == "graded":
                continue
            # Set the grade to zero and late_policy_status to "missing"
            submission.edit(submission={"posted_grade": 0, "late_policy_status": "missing"})
            
    
    
    
    print("Done!")
