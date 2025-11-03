import os
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

CSV_LOCAL = "spacex_launch_dash.csv"
CSV_URL = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv"

if os.path.exists(CSV_LOCAL):
    spacex_df = pd.read_csv(CSV_LOCAL)
else:
    try:
        spacex_df = pd.read_csv(CSV_URL)
    except Exception as e:
        raise RuntimeError("Could not load spacex_launch_dash.csv. Place it next to this script or ensure internet access.") from e

# TASK 1

min_payload = int(spacex_df['Payload Mass (kg)'].min())
max_payload = int(spacex_df['Payload Mass (kg)'].max())

# Launch sites for dropdown options
sites = sorted(spacex_df['Launch Site'].unique().tolist())
site_options = [{'label': 'All Sites', 'value': 'ALL'}] + [{'label': s, 'value': s} for s in sites]

# -------------------------------------------------------------------
# App
# -------------------------------------------------------------------
app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard', style={'textAlign': 'center'}),

    # TASK 1: Launch Site dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=site_options,
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True,
        style={'width': '80%', 'margin': '0 auto'}
    ),

    html.Br(),

    # TASK 2: Pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),

    html.Br(),

    html.P("Payload range (Kg):"),
    # TASK 3: Range slider
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        value=[min_payload, max_payload],
        marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
        allowCross=False
    ),

    html.Br(),

    # TASK 4: Scatter plot
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# -------------------------------------------------------------------
# TASK 2: Callback for pie chart
# -------------------------------------------------------------------
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie(selected_site):
    if selected_site == 'ALL':
        # Success counts per site (sum of class where 1 indicates success)
        df_success_by_site = (spacex_df.groupby('Launch Site', as_index=False)['class']
                              .sum()
                              .rename(columns={'class': 'Successes'}))
        fig = px.pie(df_success_by_site, values='Successes', names='Launch Site',
                     title='Total Successful Launches by Site')
    else:
        df_site = spacex_df[spacex_df['Launch Site'] == selected_site]
        # Count success vs failure for the selected site
        df_counts = df_site['class'].value_counts().rename_axis('Outcome').reset_index(name='Count')
        # Map 1->Success, 0->Failure for labels
        df_counts['Outcome'] = df_counts['Outcome'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(df_counts, values='Count', names='Outcome',
                     title=f'Launch Outcomes for {selected_site}')
    return fig

# -------------------------------------------------------------------
# TASK 4: Callback for scatter plot vs payload, colored by Booster Version Category
# -------------------------------------------------------------------
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    Input('site-dropdown', 'value'),
    Input('payload-slider', 'value')
)
def update_scatter(selected_site, payload_range):
    low, high = payload_range
    df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)]
    if selected_site != 'ALL':
        df = df[df['Launch Site'] == selected_site]

    fig = px.scatter(
        df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=('Payload vs. Outcome for All Sites'
               if selected_site == 'ALL' else f'Payload vs. Outcome for {selected_site}'),
        hover_data=['Launch Site']
    )
    return fig


if __name__ == '__main__':
    app.run(debug=False)
