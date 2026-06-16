# Canvas Grade Exporter

This script retrieves grades from a Canvas course, calculates a weighted final score out of 20 for each student, exports the results to Excel, and optionally fills the rounded scores into a KULoket Excel file.

## What it does

The script:

- connects to Canvas using the Canvas API;
- loads students, assignment groups, assignments, and submissions;
- calculates the weighted total using the Canvas assignment group weights;
- exports the results to an Excel file;
- adds both an exact score out of 20 and a rounded score out of 20;
- uses the Canvas `sis_user_id` as `Studnr`;
- optionally updates a KULoket `.xlsx` file by writing the rounded score into column `L`.

## Requirements

Install the required Python packages:

```bash
pip install canvasapi openpyxl
```

Set the Canvas API key as an environment variable:

```bash
export CANVAS_API_KEY="your_canvas_api_key"
```

On Windows PowerShell:

```powershell
$env:CANVAS_API_KEY="your_canvas_api_key"
```

## Canvas gradebook requirements

Important assumptions:

- every assignment has a grade;
- students who did not submit, or were not available for an assignment, have grade 0;
- those missing submissions are marked with Canvas missing = True (should have red background in the Canvas gradebook);
- assignment group weights are configured in Canvas;
- assignments that should not count toward the final score are marked as omitted from the final grade.

## Usage

Run the script with the following command:

```bash
python index.py
```

You will be asked for:
1. the Canvas course ID;
2. the course Z-code used to find the KULoket file.

## Output
The script creates an Excel file like:
```
canvas_weighted_results_course_12345_20260616_143012.xlsx
```

The file contains:
- calculated results per student;
- assignment group weights;
- assignments included in the calculation.

If a matching KULoket file is found, the script also fills in the rounded scores there.