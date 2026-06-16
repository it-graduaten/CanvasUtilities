import os
from collections import defaultdict
from datetime import datetime

from canvasapi import Canvas
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.styles.colors import RGB


CANVAS_URL = "https://thomasmore.instructure.com/"

def load_workbook_allowing_invalid_colors(filename):
    """
    Load an XLSX file even if it contains color/style values that openpyxl
    normally rejects with: 'Colors must be aRGB hex values'.

    This does not intentionally change the workbook layout.
    It only relaxes validation while loading the file.
    """

    old_rgb_set = RGB.__set__

    def safe_rgb_set(self, instance, value):
        try:
            old_rgb_set(self, instance, value)
        except ValueError:
            # Fallback to opaque black if openpyxl cannot parse the original color.
            # This is only to allow loading the workbook.
            old_rgb_set(self, instance, "FF000000")

    RGB.__set__ = safe_rgb_set

    try:
        return load_workbook(filename)
    finally:
        RGB.__set__ = old_rgb_set

def safe_float(value):
    """
    Convert Canvas values such as score, points_possible, or group_weight to float.
    Return None if conversion is not possible.
    """
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def is_missing_submission(submission):
    """
    Canvas marks assignments that were not submitted / not available as missing.

    In this script:
    - missing=True means the assignment counts as 0 in the grade calculation
    - missing=True does NOT count as an actual submitted assignment
    - missing=False means the student has a real/non-missing submission or grade
    """
    return getattr(submission, "missing", False) is True


def get_submission_score(submission):
    """
    Assignments always have a grade/score in Canvas.

    Missing submissions should already have score 0.
    If Canvas somehow returns None, we fallback to 0.
    """
    score = safe_float(getattr(submission, "score", None))

    if score is None:
        return 0.0

    return score

def save_results_to_xlsx(results, group_info, assignments_by_id, output_file):
    """
    Save final student totals and calculation metadata to an XLSX file.
    """
    print(f"[5/5] Saving XLSX file: {output_file}")

    workbook = Workbook()
    header_fill = PatternFill(fill_type="solid", fgColor="D9EAF7")

    # -------------------------
    # Sheet 1: student results
    # -------------------------
    ws_results = workbook.active
    ws_results.title = "Results"

    headers = [
        "Student ID",
        "Studnr",
        "Student Name",
        "Total / 20",
        "Total on 20 rounded",
        "Normalized %",
        "Used Weight Total",
        "Submission Status",
    ]

    ws_results.append(headers)

    for result in results:
        ws_results.append([
            result["student_id"],
            result["studnr"],
            result["student_name"],
            result["total_out_of_20"],
            result["total_out_of_20_rounded"],
            result["normalized_percent"],
            result["used_weight_total"],
            result["submission_status"],
        ])

    for cell in ws_results[1]:
        cell.font = Font(bold=True)
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")

    for row in range(2, ws_results.max_row + 1):
        ws_results[f"D{row}"].number_format = "0.00"
        ws_results[f"E{row}"].number_format = "0"
        ws_results[f"F{row}"].number_format = "0.00%"
        ws_results[f"G{row}"].number_format = "0.00"

    auto_size_columns(ws_results, max_width=45)
    ws_results.freeze_panes = "A2"

    # -------------------------------
    # Sheet 2: assignment group info
    # -------------------------------
    ws_groups = workbook.create_sheet("Assignment Groups")

    ws_groups.append([
        "Group ID",
        "Group Name",
        "Group Weight",
    ])

    for group_id, group in group_info.items():
        ws_groups.append([
            group_id,
            group["name"],
            group["weight"],
        ])

    for cell in ws_groups[1]:
        cell.font = Font(bold=True)
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")

    for row in range(2, ws_groups.max_row + 1):
        ws_groups[f"C{row}"].number_format = "0.00"

    auto_size_columns(ws_groups, max_width=45)
    ws_groups.freeze_panes = "A2"

    # -----------------------
    # Sheet 3: assignments
    # -----------------------
    ws_assignments = workbook.create_sheet("Assignments")

    ws_assignments.append([
        "Assignment ID",
        "Assignment Name",
        "Group ID",
        "Points Possible",
    ])

    for assignment_id, assignment in assignments_by_id.items():
        ws_assignments.append([
            assignment_id,
            assignment["name"],
            assignment["group_id"],
            assignment["points_possible"],
        ])

    for cell in ws_assignments[1]:
        cell.font = Font(bold=True)
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")

    for row in range(2, ws_assignments.max_row + 1):
        ws_assignments[f"D{row}"].number_format = "0.00"

    auto_size_columns(ws_assignments, max_width=55)
    ws_assignments.freeze_panes = "A2"

    workbook.save(output_file)

    print(f"Done. XLSX file saved successfully: {output_file}")


def auto_size_columns(worksheet, max_width=50):
    """
    Auto-size all columns in a worksheet.
    """
    for column_cells in worksheet.columns:
        max_length = 0
        column_letter = get_column_letter(column_cells[0].column)

        for cell in column_cells:
            value = cell.value
            if value is not None:
                max_length = max(max_length, len(str(value)))

        worksheet.column_dimensions[column_letter].width = min(max_length + 2, max_width)


def normalize_studnr(value):
    """
    Normalize student numbers for matching.

    Canvas sis_user_id can look like:
        S_r1234567

    KULoket column C contains:
        1234567

    This function:
    - converts values to string
    - strips whitespace
    - removes leading S_r or S_ if present
    - handles Excel numeric values like 1234567.0
    """
    if value is None:
        return ""

    # Handle Excel numeric values such as 1234567.0
    if isinstance(value, float) and value.is_integer():
        value = int(value)

    value = str(value).strip()

    if value.upper().startswith("S_R"):
        value = value[3:]
    elif value.upper().startswith("S_"):
        value = value[2:]
    elif value.upper().startswith("R"):
        value = value[1:]

    return value.strip()


def update_kuloket_xlsx(kuloket_file, results):
    """
    Update the KULoket XLSX file with the calculated rounded scores.

    Requirements:
    - Match students by Studnr.
    - KULoket Studnr is in column C.
    - Generated Studnr may contain prefix "S_r" or "S_", which must be stripped.
    - Write rounded score on 20 to column L.
    - KULoket has 2 header rows, so students start on row 3.
    - Do not change layout or workbook metadata intentionally.
      Only cell values in column L are updated.
    """

    print("[6/6] Updating KULoket XLSX file...")

    # Build lookup table:
    # normalized studnr -> rounded score on 20
    scores_by_studnr = {}

    skipped_no_studnr = 0
    skipped_no_score = 0

    for result in results:
        studnr = normalize_studnr(result.get("studnr"))
        print(f"Studnr '{studnr}'")
        score = result.get("total_out_of_20_rounded")

        if not studnr:
            skipped_no_studnr += 1
            continue

        if score in {None, ""}:
            skipped_no_score += 1
            continue

        scores_by_studnr[studnr] = score

    print(f"Scores available for matching: {len(scores_by_studnr)}")
    print(f"Results skipped because Studnr was missing: {skipped_no_studnr}")
    print(f"Results skipped because rounded score was missing: {skipped_no_score}")

    # Load the existing KULoket workbook.
    # We only write values into column L.
    workbook = load_workbook_allowing_invalid_colors(kuloket_file)
    worksheet = workbook.active

    matched_students = 0
    unmatched_kuloket_students = 0
    empty_studnr_rows = 0

    # KULoket has 2 header rows; students start on row 3.
    for row in range(3, worksheet.max_row + 1):
        kuloket_studnr = normalize_studnr(worksheet.cell(row=row, column=3).value)
        print(f"Processing KULoket row {row}: Studnr '{kuloket_studnr}'")

        if not kuloket_studnr:
            empty_studnr_rows += 1
            continue

        if kuloket_studnr not in scores_by_studnr:
            unmatched_kuloket_students += 1
            continue

        rounded_score = scores_by_studnr[kuloket_studnr]

        # Column L = 12.
        # Only set the value; do not touch styles, dimensions, formulas elsewhere,
        # workbook properties, sheet names, or other metadata.
        worksheet.cell(row=row, column=12).value = rounded_score

        matched_students += 1

    workbook.save(kuloket_file)

    print(f"KULoket rows updated with scores: {matched_students}")
    print(f"KULoket student rows without matching generated score: {unmatched_kuloket_students}")
    print(f"KULoket rows skipped because column C was empty: {empty_studnr_rows}")
    print(f"KULoket file saved: {kuloket_file}")

def main():
    print("Starting Canvas weighted grade calculation.")

    canvas_course_id = input("Enter the Canvas course ID: ").strip()

    # -----------------------
    # Step 1: connect
    # -----------------------
    print()
    print("[1/5] Connecting to Canvas...")

    canvas_api_key = os.environ.get("CANVAS_API_KEY")

    if not canvas_api_key:
        raise RuntimeError("CANVAS_API_KEY environment variable is not set.")

    canvas = Canvas(CANVAS_URL, canvas_api_key)
    course = canvas.get_course(canvas_course_id)

    course_name = getattr(course, "name", "Unknown course name")

    print(f"Connected.")
    print(f"Course ID: {canvas_course_id}")
    print(f"Course name: {course_name}")

    # -----------------------
    # Step 2: load course data
    # -----------------------
    print()
    print("[2/5] Loading students, assignment groups, and assignments...")

    students = list(course.get_users(enrollment_type=["student"]))
    assignment_groups = list(course.get_assignment_groups(include=["assignments"]))

    assignments_by_id = {}
    group_info = {}

    skipped_assignments_no_points = 0
    skipped_assignments_unpublished = 0
    skipped_assignments_omitted_from_final_grade = 0

    for group in assignment_groups:
        group_id = int(group.id)
        group_name = getattr(group, "name", f"Assignment group {group_id}")
        group_weight = safe_float(getattr(group, "group_weight", None))

        group_info[group_id] = {
            "name": group_name,
            "weight": group_weight,
        }

        for assignment in getattr(group, "assignments", []):
            assignment_id = int(assignment["id"])
            assignment_name = assignment.get("name", f"Assignment {assignment_id}")
            points_possible = safe_float(assignment.get("points_possible"))
            published = assignment.get("published")
            omit_from_final_grade = assignment.get("omit_from_final_grade", False)

            if points_possible is None or points_possible <= 0:
                skipped_assignments_no_points += 1
                continue

            if published is False:
                skipped_assignments_unpublished += 1
                continue

            if omit_from_final_grade is True:
                skipped_assignments_omitted_from_final_grade += 1
                continue

            assignments_by_id[assignment_id] = {
                "id": assignment_id,
                "name": assignment_name,
                "group_id": group_id,
                "points_possible": points_possible,
            }

    total_group_weight = sum(
        info["weight"] or 0
        for info in group_info.values()
    )

    print(f"Students loaded: {len(students)}")
    print(f"Assignment groups loaded: {len(assignment_groups)}")
    print(f"Gradable assignments included: {len(assignments_by_id)}")
    print(f"Assignments skipped because of no/zero points: {skipped_assignments_no_points}")
    print(f"Assignments skipped because unpublished: {skipped_assignments_unpublished}")
    print(f"Assignments skipped because omitted from final grade: {skipped_assignments_omitted_from_final_grade}")
    print(f"Total assignment group weight: {total_group_weight}")

    if not assignments_by_id:
        raise RuntimeError("No gradable assignments with points_possible were found.")

    if total_group_weight <= 0:
        raise RuntimeError(
            "No assignment group weights were found. "
            "Enable weighted assignment groups in Canvas or set group weights first."
        )

        # -----------------------
    # Step 3: load submissions
    # -----------------------
    print()
    print("[3/5] Fetching and processing submissions...")

    submissions = course.get_multiple_submissions(student_ids=["all"])

    student_scores = defaultdict(dict)

    # This tracks students who have at least one assignment that is NOT missing.
    # If a student only has missing=True submissions, they will get NA.
    students_with_any_non_missing_submission = set()

    submission_count = 0
    included_submission_count = 0
    skipped_submission_count = 0

    missing_submission_count = 0
    non_missing_submission_count = 0
    submissions_for_unknown_assignment = 0

    for submission in submissions:
        submission_count += 1

        user_id = int(submission.user_id)
        assignment_id = int(submission.assignment_id)

        if assignment_id not in assignments_by_id:
            skipped_submission_count += 1
            submissions_for_unknown_assignment += 1
            continue

        missing = is_missing_submission(submission)
        score = get_submission_score(submission)

        # Always store the score.
        # If missing=True, Canvas should give score 0.
        # This 0 must be included in the total calculation.
        student_scores[user_id][assignment_id] = score
        included_submission_count += 1

        if missing:
            missing_submission_count += 1
        else:
            non_missing_submission_count += 1
            students_with_any_non_missing_submission.add(user_id)

    print(f"Submissions processed: {submission_count}")
    print(f"Submissions included in calculation: {included_submission_count}")
    print(f"Missing submissions included as 0: {missing_submission_count}")
    print(f"Non-missing submissions found: {non_missing_submission_count}")
    print(f"Submissions skipped: {skipped_submission_count}")
    print(f"  - Skipped because assignment was not included: {submissions_for_unknown_assignment}")
    print(f"Students with at least one non-missing submission: {len(students_with_any_non_missing_submission)}")
    
    
    # -----------------------
    # Step 4: calculate totals
    # -----------------------
    print()
    print("[4/5] Calculating final weighted totals...")

    results = []

    students_without_submissions = 0
    students_with_calculated_total = 0
    students_without_usable_weighted_groups = 0

    for student in students:
        student_id = int(student.id)
        student_name = getattr(student, "sortable_name", None) or getattr(student, "name", "")
        studnr = getattr(student, "sis_user_id", None) or ""

        if student_id not in students_with_any_non_missing_submission:
            students_without_submissions += 1

            results.append({
                "student_id": student_id,
                "studnr": studnr,
                "student_name": student_name,
                "total_out_of_20": "NA",
                "total_out_of_20_rounded": "NA",
                "normalized_percent": "NA",
                "used_weight_total": "NA",
                "submission_status": "No submissions",
            })

            continue

        weighted_total_percent = 0.0
        used_weight_total = 0.0

        for group_id, group in group_info.items():
            group_weight = group["weight"]

            if group_weight is None or group_weight <= 0:
                continue

            group_points_earned = 0.0
            group_points_possible = 0.0
            group_assignment_count = 0

            for assignment_id, assignment in assignments_by_id.items():
                if assignment["group_id"] != group_id:
                    continue

                group_assignment_count += 1

                points_possible = assignment["points_possible"]
                score = student_scores[student_id].get(assignment_id)

                if score is None:
                    score = 0.0

                group_points_earned += score
                group_points_possible += points_possible

            if group_assignment_count == 0:
                continue

            if group_points_possible <= 0:
                continue

            group_percent = group_points_earned / group_points_possible
            group_weighted_contribution = group_percent * group_weight

            weighted_total_percent += group_weighted_contribution
            used_weight_total += group_weight

        if used_weight_total <= 0:
            students_without_usable_weighted_groups += 1

            total_out_of_20 = "NA"
            total_out_of_20_rounded = "NA"
            normalized_percent = "NA"
            submission_status = "Has submission, but no usable weighted groups"
        else:
            students_with_calculated_total += 1

            normalized_percent = weighted_total_percent / used_weight_total
            total_out_of_20 = round(normalized_percent * 20, 2)
            total_out_of_20_rounded = round(total_out_of_20)
            submission_status = "Has submission"

        results.append({
            "student_id": student_id,
            "studnr": studnr,
            "student_name": student_name,
            "total_out_of_20": total_out_of_20,
            "total_out_of_20_rounded": total_out_of_20_rounded,
            "normalized_percent": normalized_percent,
            "used_weight_total": used_weight_total,
            "submission_status": submission_status,
        })

    print(f"Students processed: {len(students)}")
    print(f"Students with calculated total: {students_with_calculated_total}")
    print(f"Students with no non-missing submissions: {students_without_submissions}")
    print(f"Students with submission but no usable weighted groups: {students_without_usable_weighted_groups}")

    # -----------------------
    # Step 5: save XLSX
    # -----------------------
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"canvas_weighted_results_course_{canvas_course_id}_{timestamp}.xlsx"

    save_results_to_xlsx(
        results=results,
        group_info=group_info,
        assignments_by_id=assignments_by_id,
        output_file=output_file,
    )
    
    # -----------------------
    # Step 6: update KULoket generated XLSX file with calculated scores
    # -----------------------
    course_z_code = input("Enter the course Z-code (e.g. Z12345): ").strip()
    # Find the file in the current directory that has the course Z-code in its name and ends with .xlsx
    kuloket_file = None
    for filename in os.listdir("."):
        if filename.endswith(".xlsx") and course_z_code in filename:
            kuloket_file = filename
            break
    if kuloket_file is None:
        print(f"No XLSX file found in the current directory with Z-code {course_z_code}. Skipping KULoket update.")
    else:
        print(f"Found KULoket XLSX file: {kuloket_file}. Updating it with calculated scores...")
        update_kuloket_xlsx(kuloket_file, results)
        print(f"KULoket XLSX file updated successfully: {kuloket_file}")

    print()
    print("Finished Canvas weighted grade calculation.")


if __name__ == "__main__":
    main()