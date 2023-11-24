# Import packages
import dash_bootstrap_components as dbc
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.graph_objs as go
from src import data_collector

data_collector = data_collector.DataCollector()
# Get all canvas data
data_collector.collect_data()
#
# # Read the data from 'data.csv' file but skip the second and third row
# DF = pd.read_csv('data.csv', skiprows=[1, 2])
#
#
# def get_section_dropdown():
#     sections = DF['Section'].unique()
#     labels = []
#     values = []
#     for section in sections:
#         # If the section is not a string, skip it
#         if type(section) != str:
#             continue
#         labels.append(section)
#         values.append(section)
#     print(labels)
#     print(values)
#     return dcc.Dropdown(options=labels, value=values)
#
#
# def get_assignment_dropdown():
#     assignments = DF['Assignment'].unique()
#     labels = []
#     values = []
#     for assignment in assignments:
#         # If the assignment is not a string, skip it
#         if type(assignment) != str:
#             continue
#         labels.append(assignment)
#         values.append(assignment)
#     return dcc.Dropdown(options=labels, value=values)
#
#
# def get_amount_of_students():
#     return len(DF.index)
#
#
# # Initialize the app
# app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
#
# fig = go.Figure(data=[go.Scatter(x=['Joren', 'Siebe', 'Jente'], y=[4, 1, 2])])
#
# # App layout
# app.layout = html.Div(className='container', children=[
#     html.Div(className='row', children=[
#         html.Div(className='col-4', children=[
#             get_section_dropdown()
#         ]),
#         html.Div(className='col-8', children=f'There is a total of {get_amount_of_students()} students'),
#     ]),
#     html.Div(className='row', children=[
#         html.Div(className='col-12', children=[
#             dash_table.DataTable(DF.to_dict('records'), [{"name": i, "id": i} for i in DF.columns],
#                                  filter_action='native',
#                                  filter_options={"placeholder_text": "Filter column..."},
#                                  page_size=200)
#         ])
#     ]),
#     dcc.Graph(figure=fig)
# ])
#
# # Run the app
# if __name__ == '__main__':
#     app.run(debug=True)
