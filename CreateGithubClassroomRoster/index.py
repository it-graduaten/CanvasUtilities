import os
from canvasapi import Canvas


def ask_yes_no(question, default="y"):
    """ Asks the user a yes/no question """
    if default == "y":
        question = "{} [Y/n]: ".format(question)
    elif default == "n":
        question = "{} [y/N]: ".format(question)
    else:
        raise ValueError("Default value should be 'y' or 'n'")
    while True:
        choice = input(question).lower()
        if choice in ["y", "yes"]:
            return True
        elif choice in ["n", "no"]:
            return False
        elif choice == "":
            return default == "y"
        else:
            print("Please enter yes or no")


def create_csv_file(all_sections, course_id):
    # Create the csv file
    with open(f"output/studenten-{course_id}.csv", "w") as f:
        # Add a student to the csv file on every line
        for section in all_sections:
            for student in section.students:
                student_number = student['sis_user_id'].replace("S_", "")
                line = f"({student_number}) {student['name']}\n"
                # Add the line to the file
                f.write(line)
    f.close()


def ask_sections_to_include(all_sections):
    """ Asks the user which sections to include """
    all_sections = list(all_sections)
    sections_to_include = []
    for i, section in enumerate(all_sections):
        print("{}. {}".format(i, section.name))
    while True:
        try:
            choice = int(input("Which sections do you want to include? "))
            if 0 <= choice < len(all_sections):
                sections_to_include.append(all_sections[choice])
            else:
                print("Please enter a number between 0 and {}".format(
                    len(all_sections) - 1))
        except ValueError:
            print("Please enter a number between 0 and {}".format(
                len(all_sections) - 1))
        if not ask_yes_no("Do you want to include another section?"):
            break
    # Remove the sections that the user doesn't want to include
    return sections_to_include


if __name__ == "__main__":
    # Get the canvas api key from the environment variables
    canvas_api_key = os.environ.get("CANVAS_API_KEY")
    # Login to canvas
    canvas = Canvas("https://thomasmore.instructure.com/", canvas_api_key)
    # Get the course
    canvas_course_id = input("Enter the Canvas course ID: ")
    course = canvas.get_course(canvas_course_id)
    # Get all students in the course
    sections = course.get_sections(include=['students'])
    # Ask the user which sections to include
    sections = ask_sections_to_include(sections)
    create_csv_file(sections, canvas_course_id)
    print("Done!")
