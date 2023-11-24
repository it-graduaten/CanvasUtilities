# Import packages
import dash_bootstrap_components as dbc
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.graph_objs as go
import random

# Read the data from 'gradebook.csv' file but skip the second and third row
DF = pd.read_csv('gradebook.csv', skiprows=[1, 2])

# Read the data from the 'canvas_data.xlsx' file
CANVAS_EXCEL = pd.ExcelFile('canvas_data.xlsx')
SECTIONS = pd.read_excel(CANVAS_EXCEL, 'Sections')
STUDENTS = pd.read_excel(CANVAS_EXCEL, 'Students')
ASSIGNMENTS = pd.read_excel(CANVAS_EXCEL, 'Assignments')
ASSIGNMENT_GROUPS = pd.read_excel(CANVAS_EXCEL, 'Assignment Groups')


@callback(Output(component_id='total-students-output', component_property='children'),
          Input(component_id='section-filter', component_property='value'))
def show_total_in_section(input_value):
    # If the input value is an empty array, return the total number of students
    if input_value == []:
        return f'Total number of students: {len(STUDENTS)}'
    # If the input value is not an empty array, return the total number of students in the selected sections
    else:
        # Get the total number of students in the selected sections
        total_students = 0
        for section in input_value:
            total_students += len(STUDENTS[STUDENTS['Section name'] == section])
        return f'Total number of students in selected sections: {total_students}'


def get_section_checklist():
    # Get all section names
    section_names = SECTIONS['Section name'].unique()
    # Create a checklist with all section names
    checklist = dcc.Checklist(
        section_names,
        [],
        id='section-filter'
    )
    return checklist


def get_final_score_pie_chart():
    labels = ['0-10', '11-20', '21-30', '31-40', '41-50', '51-60', '61-70', '71-80', '81-90', '91-100']
    values = []
    # Get all final scores
    final_scores = DF['Final Score']
    # Replace all ',' with '.'
    final_scores = final_scores.str.replace(',', '.')
    # Convert all final scores to decimals, as they are currently strings
    final_scores = final_scores.astype(float)
    # Get the number of students with a final score between 0 and 10
    values.append(len(final_scores[final_scores.between(0, 10)]))
    # Get the number of students with a final score between 11 and 20
    values.append(len(final_scores[final_scores.between(11, 20)]))
    # Get the number of students with a final score between 21 and 30
    values.append(len(final_scores[final_scores.between(21, 30)]))
    # Get the number of students with a final score between 31 and 40
    values.append(len(final_scores[final_scores.between(31, 40)]))
    # Get the number of students with a final score between 41 and 50
    values.append(len(final_scores[final_scores.between(41, 50)]))
    # Get the number of students with a final score between 51 and 60
    values.append(len(final_scores[final_scores.between(51, 60)]))
    # Get the number of students with a final score between 61 and 70
    values.append(len(final_scores[final_scores.between(61, 70)]))
    # Get the number of students with a final score between 71 and 80
    values.append(len(final_scores[final_scores.between(71, 80)]))
    # Get the number of students with a final score between 81 and 90
    values.append(len(final_scores[final_scores.between(81, 90)]))
    # Get the number of students with a final score between 91 and 100
    values.append(len(final_scores[final_scores.between(91, 100)]))
    return dcc.Graph(figure=go.Figure(data=[go.Pie(labels=labels, values=values)]))


def get_final_score_arrays():
    names = []
    scores = []

    for student in STUDENTS['Student name']:
        names.append(student)
        scores.append(random.randint(0, 10))

    return names, scores


# Initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

print(get_final_score_arrays())

fig = go.Figure(data=[go.Scatter(x=get_final_score_arrays()[0], y=get_final_score_arrays()[1], mode='markers')])

# App layout
app.layout = html.Div(className='container', children=[
    html.Div(className='row', children=[
        html.Div(className='col-4', children=[
            dcc.Markdown('# Section filter'),
            get_section_checklist()
        ]),
        html.Div(className='col-8', children=[
            dcc.Markdown(id='total-students-output')
        ])
    ]),
    html.Div(className='row', children=[
        html.Div(className='col-12', children=[
            dcc.Markdown('## Final score'),
        ]),
        html.Div(className='col-12', children=[
            dcc.Markdown(children='Alle studenten'),
            get_final_score_pie_chart()
        ])
    ])
])

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
