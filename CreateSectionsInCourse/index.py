import os
import pandas as pd
from canvasapi import Canvas

# Ask the user for a Canvas Course ID
course_id = input("Enter the Canvas Course ID: ")

# Ask the user for a canvas api key, if not set as environment variable
api_key = input("Geef de Canvas API key (laat leeg voor environment variable te gebruiken): ")
if api_key == "":
    api_key = os.environ.get("CANVAS_API_KEY")

# Create a canvas object
canvas_obj = Canvas("https://thomasmore.instructure.com/", api_key)
course_obj = canvas_obj.get_course(course_id)

# Get all users in the course
canvas_students = course_obj.get_users()
# Get all sections in the course
canvas_sections = course_obj.get_sections()

# Print all sections
print("Existing sections: ")
for section in canvas_sections:
    print(section.name)

# Get all xlsx files
files = [f for f in os.listdir('.') if os.path.isfile(f)]
files = [f for f in files if f.endswith(".xlsx")]

for f in files:
    print("Working on file: " + f)
    section_to_use = None
    # Get the name without the extension
    section_name = f[:-5]
    # Check if the section already exists
    if section_name in [s.name for s in canvas_sections]:
        # If it exists, ask the user if he wants to use it
        answer = input("Section " + section_name + " already exists, do you want to use it? (y/n): ")
        if answer == "y":
            # If yes, get the section object
            section_to_use = [s for s in canvas_sections if s.name == section_name][0]
        else:
            # Create a new section
            print("Creating section: " + section_name)
            section_to_use = course_obj.create_course_section(course_section={'name': section_name})
            print("Section with name " + section_to_use.name + " created")
    else:
        # Create a new section
        print("Creating section: " + section_name)
        section_to_use = course_obj.create_course_section(course_section={'name': section_name})
        print("Section with name " + section_to_use.name + " created")
  
    # Read the excel file 
    df = pd.read_excel(f)
    # Get the column names
    columns = df.columns
    # Loop over the rows
    for index, row in df.iterrows():
        r_number = row['Inlognummer']
        print("Working on student with number: " + r_number)
        # Find the canvas student with the same r_number
        canvas_student = [s for s in canvas_students if r_number in s.sis_user_id]
        # If more than 1 student is found, print an error
        if len(canvas_student) > 1:
            print("Error: More than 1 student found for r_number: " + r_number)
            continue
        # If no student is found, print an error
        if canvas_student is None or len(canvas_student) == 0:
            print("Error: No student found for r_number: " + r_number)
            continue
        print(canvas_student)
        print(section_to_use)
        # Add the student to the new section
        print("Enrolling student " + canvas_student[0].name + " in section " + section_to_use.name)
        section_to_use.enroll_user(canvas_student[0].id, enrollment={'enrollment_state': 'active', 'notify': 'false'})







# # Create a new course section
# section_name = input("Enter the name of the new section: ")
# new_section = course_obj.create_course_section(section={'name': section_name})

# Read the excel file with the same name as the newly created section

