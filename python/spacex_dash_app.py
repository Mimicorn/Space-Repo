# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
launch_sites = spacex_df['Launch Site'].unique()

# Add an option for 'All Sites'
Launch_site_options = [{'label': 'All Sites', 'value': 'All'}]
# Create a list of dictonaries for dropdown options
for site in launch_sites:
    Launch_site_options.append({'label': site, 'value': site})

min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()

marks = {i: str(i) for i in range(0, 10001, 1000)}

app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(id='site-dropdown', 
                                             options=Launch_site_options,
                                             value='All',
                                             placeholder="Select a Launch Site",
                                             searchable=True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                marks=marks,
                                                value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'All':
        # If 'All' is selected, group by Launch site and calculate success counts
        success_counts = spacex_df.groupby('Launch Site')['class'].value_counts().unstack().fillna(0)
        fig = px.pie(success_counts, values=success_counts[1], names=success_counts.index, title=f'Total Success Launches for {entered_site} Site')
    else:
        # If a specific site is slected, filter the DataFrame
        site_data = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_counts = site_data['class'].value_counts().rename({0: 'Failure', 1: 'Success'})
        fig = px.pie(success_counts, values=success_counts.values, names=success_counts.index, title=f"Success vs Failure for {entered_site}")
    fig.update_traces(textinfo='label+percent', textposition='inside')
    fig.update_layout()
    return fig
        
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
                     Input(component_id='site-dropdown', component_property='value'),
                     Input(component_id='payload-slider', component_property='value'))
def get_scatter_chart(entered_site, payload_range):
    # Filter the dataframe based on the Payload range
    filtered_df = spacex_df[spacex_df['Payload Mass (kg)'].between(payload_range[0], payload_range[1])]
    if entered_site != 'All':
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category')    
    fig.update_layout(title=f'Correlation between Payload Mass and Success for {entered_site} Site')
    fig.update_xaxes(title_text='Payload Mass (kg)')
    fig.update_yaxes(title_text='Success (1) / Failure (0)')
    return fig

# Run the app
if __name__ == '__main__':
    app.run()
