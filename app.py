import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
import numpy as np
from datetime import datetime
import flask
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
import os
from werkzeug.security import generate_password_hash, check_password_hash
import json
from io import StringIO

# Initialize the Dash app with Bootstrap theme and Poppins font
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap"
    ],
    suppress_callback_exceptions=True,
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}]
)


# Apply global CSS for Poppins font and background color
app.css.append_css({
    "external_url": "data:text/css;charset=UTF-8,body { font-family: 'Poppins', sans-serif; background-color: #F5F7FA; }"
})

server = app.server
server.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key')

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'

# Sample user database
class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

# Sample users
users = {
    'admin': User('admin', 'admin', generate_password_hash('password')),
    'user': User('user', 'user', generate_password_hash('password'))
}

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

# Load and preprocess data
def load_data():
    df = pd.read_csv("C:/Users/bida21-014/dash_project/assignment/web_server_data.csv")
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed', dayfirst=False, errors='coerce')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['month'] = df['date'].dt.month
    df['month_name'] = df['date'].dt.strftime('%b')
    df['year'] = df['date'].dt.year
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['date'].dt.day_name()
    return df

# Load the global DataFrame
df = pd.read_csv("C:/Users/bida21-014/dash_project/assignment/web_server_data.csv")

# Continent to country mapping
continent_to_countries = {
    'Europe': ['UK', 'Germany'],
    'North America': ['USA', 'Canada'],
    'Oceania': ['Australia'],
    'Asia': ['India']
}

# Define color scheme
colors = {
    'primary': '#4a6baf',
    'secondary': '#6c757d',
    'success': '#28a745',
    'danger': '#dc3545',
    'warning': '#ffc107',
    'info': '#17a2b8',
    'light': '#F5F7FA',
    'dark': '#343a40',
    'job_requests': '#4a6baf',
    'demo_requests': '#9c27b0',
    'ai_assistant': '#2196f3',
    'event_registrations': '#4caf50',
    'job_types': {
        'AI Specialist': '#4a6baf',
        'Software Developer': '#9c27b0',
        'Project Manager': '#2196f3',
        'System Admin': '#4caf50',
        'Data Analyst': '#ff9800',
        'Other': '#ff5722'
    },
    'gender': {
        'Male': '#1f77b4',
        'Female': '#ff7f0e',
        'Other': '#808080'
    }
}

# Navigation tabs
tabs = html.Div([
    dbc.Tabs([
        dbc.Tab(label="Overview", tab_id="overview", labelClassName="text-primary", activeLabelClassName="fw-bold"),
        dbc.Tab(label="Data Explorer", tab_id="dataset", labelClassName="text-primary", activeLabelClassName="fw-bold"),
        dbc.Tab(label="Geo-sales Insights", tab_id="geographic", labelClassName="text-primary", activeLabelClassName="fw-bold"),
        dbc.Tab(label="Sales Trend Over Time", tab_id="time", labelClassName="text-primary", activeLabelClassName="fw-bold"),
        dbc.Tab(label="Job Types Analysis", tab_id="job_types", labelClassName="text-primary", activeLabelClassName="fw-bold"),
        dbc.Tab(label="Feature Requests", tab_id="features", labelClassName="text-primary", activeLabelClassName="fw-bold"),
        dbc.Tab(label="Demographic Insights", tab_id="demographics", labelClassName="text-primary", activeLabelClassName="fw-bold"),
        dbc.Tab(label="Statistical Insights", tab_id="statistics", labelClassName="text-primary", activeLabelClassName="fw-bold"),
    ],
    id="tabs",
    active_tab="overview",
    className="mb-3"),
], style={"fontFamily": "Poppins"})

# Tooltips for filters
filter_tooltips = {
    'start-date': 'Select the start date for the data range to analyze',
    'end-date': 'Select the end date for the data range to analyze',
    'time-granularity-filter': 'Choose the time aggregation level (daily, weekly, monthly, yearly)',
    'continent-filter': 'Filter data by continent',
    'country-filter': 'Filter data by country',
    'job-type-filter': 'Filter data by job type',
    'interaction-type-filter': 'Filter data by interaction type (e.g., Demo Request, Job Placement)',
    'apply-filters': 'Apply all selected filters to update the dashboard',
    'reset-filters': 'Reset all filters to their default values'
}

# Filters sidebar with tooltips
filters = html.Div([
    html.H5("Filters", className="mb-3"),
    html.Div([
        html.Label([
            "Date Range:",
            dbc.Tooltip("Select the date range for data analysis", target="date-range-label"),
        ], id="date-range-label", className="fw-bold mb-2"),
        dbc.Row([
            dbc.Col([
                html.Label([
                    "Start Date",
                    dbc.Tooltip(filter_tooltips['start-date'], target="start-date-label"),
                ], id="start-date-label", className="mb-1"),
                dcc.DatePickerSingle(
                    id='start-date',
                    min_date_allowed=df['date'].min() if not pd.isna(df['date'].min()) else None,
                    max_date_allowed=df['date'].max() if not pd.isna(df['date'].max()) else None,
                    initial_visible_month=df['date'].min() if not pd.isna(df['date'].min()) else None,
                    date=df['date'].min() if not pd.isna(df['date'].min()) else None,
                    className="mb-3 w-100"
                ),
            ], width=6),
            dbc.Col([
                html.Label([
                    "End Date",
                    dbc.Tooltip(filter_tooltips['end-date'], target="end-date-label"),
                ], id="end-date-label", className="mb-1"),
                dcc.DatePickerSingle(
                    id='end-date',
                    min_date_allowed=df['date'].min() if not pd.isna(df['date'].min()) else None,
                    max_date_allowed=df['date'].max() if not pd.isna(df['date'].max()) else None,
                    initial_visible_month=df['date'].max() if not pd.isna(df['date'].max()) else None,
                    date=df['date'].max() if not pd.isna(df['date'].max()) else None,
                    className="mb-3 w-100"
                ),
            ], width=6),
        ]),
    ], className="mb-1"),
    html.Div([
        html.Label([
            "Time Granularity:",
            dbc.Tooltip(filter_tooltips['time-granularity-filter'], target="time-granularity-label"),
        ], id="time-granularity-label", className="fw-bold mb-2"),
        dcc.Dropdown(
            id='time-granularity-filter',
            options=[
                {'label': 'Daily', 'value': 'daily'},
                {'label': 'Weekly', 'value': 'weekly'},
                {'label': 'Monthly', 'value': 'monthly'},
                {'label': 'Yearly', 'value': 'yearly'}
            ],
            value='daily',
            clearable=False,
            className="mb-3"
        ),
    ]),
    html.Div([
        html.Label([
            "Continent:",
            dbc.Tooltip(filter_tooltips['continent-filter'], target="continent-filter-label"),
        ], id="continent-filter-label", className="fw-bold mb-2"),
        dcc.Dropdown(
            id='continent-filter',
            options=[{'label': 'All Continents', 'value': 'all'}] +
                    [{'label': continent, 'value': continent} for continent in sorted(df['continent'].unique())],
            value='all',
            clearable=False,
            className="mb-3"
        ),
    ]),
    html.Div([
        html.Label([
            "Country:",
            dbc.Tooltip(filter_tooltips['country-filter'], target="country-filter-label"),
        ], id="country-filter-label", className="fw-bold mb-2"),
        dcc.Dropdown(
            id='country-filter',
            options=[{'label': 'All Countries', 'value': 'all'}] +
                    [{'label': country, 'value': country} for country in sorted(df['country'].unique())],
            value='all',
            clearable=False,
            className="mb-3"
        ),
    ]),
    html.Div([
        html.Label([
            "Job Type:",
            dbc.Tooltip(filter_tooltips['job-type-filter'], target="job-type-filter-label"),
        ], id="job-type-filter-label", className="fw-bold mb-2"),
        dcc.Dropdown(
            id='job-type-filter',
            options=[{'label': 'All Job Types', 'value': 'all'}] +
                    [{'label': job_type, 'value': job_type} for job_type in sorted(df['job_type'].unique())],
            value='all',
            clearable=False,
            className="mb-3"
        ),
    ]),
    html.Div([
        html.Label([
            "Interaction Type:",
            dbc.Tooltip(filter_tooltips['interaction-type-filter'], target="interaction-type-filter-label"),
        ], id="interaction-type-filter-label", className="fw-bold mb-2"),
        dcc.Dropdown(
            id='interaction-type-filter',
            options=[{'label': 'All Interactions', 'value': 'all'}] +
                    [{'label': interaction, 'value': interaction} for interaction in sorted(df['interaction_type'].unique())],
            value='all',
            clearable=False,
            className="mb-3"
        ),
    ]),
    dbc.Row([
        dbc.Col(
            html.Button([
                'Apply Filters',
                dbc.Tooltip(filter_tooltips['apply-filters'], target="apply-filters"),
            ], id='apply-filters', className="btn btn-primary w-100 mt-2"),
            width=6
        ),
        dbc.Col(
            html.Button([
                'Reset Filters',
                dbc.Tooltip(filter_tooltips['reset-filters'], target="reset-filters"),
            ], id='reset-filters', className="btn btn-secondary w-100 mt-2"),
            width=6
        ),
    ]),
], className="p-3 border rounded", style={"backgroundColor": "#E9EDF4", "fontFamily": "Poppins"})

# Login form
login_layout = html.Div([
    html.Div([
        html.H2("SALES INSIGHTS DASHBOARD", className="text-center mb-4 text-primary", style={"fontFamily": "Poppins"}),
        html.H4("Login", className="text-center mb-4", style={"fontFamily": "Poppins"}),
        dbc.Alert(
            "Invalid username or password",
            id="login-alert",
            dismissable=True,
            is_open=False,
            color="danger",
        ),
        dbc.Form([
            dbc.Row([
                dbc.Label("Username", html_for="username", width=3),
                dbc.Col(
                    dbc.Input(type="text", id="username", placeholder="Enter username"),
                    width=9
                )
            ], className="mb-3"),
            dbc.Row([
                dbc.Label("Password", html_for="password"),
                dbc.Col(
                    dbc.Input(type="password", id="password", placeholder="Enter password"),
                    width=9
                )
            ], className="mb-3"),
            dbc.Button("Login", color="primary", id="login-button", className="w-100 mt-3"),
        ]),
    ], className="p-4 border rounded shadow", style={"maxWidth": "400px", "backgroundColor": "#F5F7FA"}),
], className="d-flex justify-content-center align-items-center", style={"height": "100vh", "backgroundColor": "#F5F7FA"})

# Main layout for the dashboard
dashboard_layout = html.Div([
    # Header
    dbc.Navbar(
        dbc.Container([
            html.A(
                dbc.Row([
                    dbc.Col(html.H3("SALES INSIGHTS DASHBOARD", className="text-white mb-0 text-center", style={"fontFamily": "Poppins"}), width=12),
                ], align="center", justify="center"),
                href="#",
            ),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Span("Admin User", className="me-2 text-white", style={"fontFamily": "Poppins"}),
                        html.Div(
                            "A",
                            style={
                                "backgroundColor": "#fff",
                                "color": "#4a6baf",
                                "borderRadius": "50%",
                                "width": "32px",
                                "height": "32px",
                                "display": "flex",
                                "alignItems": "center",
                                "justifyContent": "center",
                                "fontWeight": "bold",
                                "fontFamily": "Poppins"
                            }
                        ),
                    ], className="d-flex align-items-center"),
                ], className="mt-3 mt-md-0"),
                dbc.Col([
                    dbc.Button("Logout", id="logout-button", color="light", size="sm", className="ms-2"),
                ], className="mt-3 mt-md-0"),
            ], className="ms-auto flex-nowrap mt-3 mt-md-0", align="center"),
        ]),
        style={"background": "linear-gradient(90deg, #4a6baf, #2a4b8f)"},
        dark=True,
        className="mb-4",
    ),
    # Main content
    dbc.Container([
        dbc.Row([
            # Navigation tabs
            dbc.Col([
                tabs,
            ], width=12),
        ]),
        dbc.Row([
            # Filters sidebar
            dbc.Col([
                filters,
            ], width=12, lg=3, className="mb-4"),
            # Content area
            dbc.Col([
                html.Div(id="tab-content"),
            ], width=12, lg=9),
        ]),
    ], fluid=True, style={"backgroundColor": "#F5F7FA"}),
])

# App layout with conditional rendering based on authentication
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    dcc.Store(id='filtered-data-store'),
], style={"backgroundColor": "#F5F7FA"})

# Callback to update page content based on URL
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/login':
        return login_layout
    else:
        if current_user.is_authenticated:
            return dashboard_layout
        else:
            return login_layout

# Login callback
@app.callback(
    [Output('url', 'pathname'),
     Output('login-alert', 'is_open')],
    [Input('login-button', 'n_clicks')],
    [State('username', 'value'),
     State('password', 'value')]
)
def login(n_clicks, username, password):
    if n_clicks is None:
        raise PreventUpdate
    user = users.get(username)
    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        return '/', False
    else:
        return '/login', True

# Logout callback
@app.callback(
    Output('url', 'pathname', allow_duplicate=True),
    [Input('logout-button', 'n_clicks')],
    prevent_initial_call=True
)
def logout(n_clicks):
    if n_clicks:
        logout_user()
        return '/login'
    raise PreventUpdate

# Callback to update country filter based on continent selection
@app.callback(
    Output('country-filter', 'options'),
    [Input('continent-filter', 'value')]
)
def update_country_options(selected_continent):
    if selected_continent == 'all':
        return [{'label': 'All Countries', 'value': 'all'}] + \
               [{'label': country, 'value': country} for country in sorted(df['country'].unique())]
    else:
        countries = continent_to_countries.get(selected_continent, [])
        return [{'label': 'All Countries', 'value': 'all'}] + \
               [{'label': country, 'value': country} for country in sorted(countries)]

# Filter data callback
@app.callback(
    Output('filtered-data-store', 'data'),
    [Input('apply-filters', 'n_clicks')],
    [State('start-date', 'date'),
     State('end-date', 'date'),
     State('time-granularity-filter', 'value'),
     State('continent-filter', 'value'),
     State('country-filter', 'value'),
     State('job-type-filter', 'value'),
     State('interaction-type-filter', 'value')]
)
def filter_data(n_clicks, start_date, end_date, time_granularity, continent, country, job_type, interaction_type):
    if n_clicks is None:
        filtered_df = df.copy()
    else:
        filtered_df = df.copy()
        try:
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            filtered_df = filtered_df[(filtered_df['date'] >= start_date) & (filtered_df['date'] <= end_date)]
            if continent != 'all':
                filtered_df = filtered_df[filtered_df['continent'] == continent]
            if country != 'all':
                filtered_df = filtered_df[filtered_df['country'] == country]
            if job_type != 'all':
                filtered_df = filtered_df[filtered_df['job_type'] == job_type]
            if interaction_type != 'all':
                filtered_df = filtered_df[filtered_df['interaction_type'] == interaction_type]
        except Exception as e:
            print(f"Filter error: {str(e)}")
            filtered_df = df.copy()
    return filtered_df.to_json(date_format='iso', orient='split')

# Reset filters callback
@app.callback(
    [Output('start-date', 'date'),
     Output('end-date', 'date'),
     Output('time-granularity-filter', 'value'),
     Output('continent-filter', 'value'),
     Output('country-filter', 'value'),
     Output('job-type-filter', 'value'),
     Output('interaction-type-filter', 'value'),
     Output('filtered-data-store', 'data', allow_duplicate=True)],
    [Input('reset-filters', 'n_clicks')],
    prevent_initial_call=True
)
def reset_filters(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    return (
        df['date'].min() if not pd.isna(df['date'].min()) else None,
        df['date'].max() if not pd.isna(df['date'].max()) else None,
        'daily',
        'all',
        'all',
        'all',
        'all',
        df.to_json(date_format='iso', orient='split')
    )

# Render tab content callback
@app.callback(
    Output('tab-content', 'children'),
    [Input('tabs', 'active_tab'),
     Input('filtered-data-store', 'data'),
     Input('start-date', 'date'),
     Input('end-date', 'date'),
     Input('time-granularity-filter', 'value'),
     Input('continent-filter', 'value'),
     Input('country-filter', 'value'),
     Input('job-type-filter', 'value'),
     Input('interaction-type-filter', 'value')]
)
def render_tab_content(active_tab, filtered_data_json, start_date, end_date, time_granularity, continent, country, job_type, interaction_type):
    if filtered_data_json is None:
        filtered_df = df.copy()
    else:
        filtered_df = pd.read_json(StringIO(filtered_data_json), orient='split')
        filtered_df['timestamp'] = pd.to_datetime(filtered_df['timestamp'], format='mixed', dayfirst=False, errors='coerce')
        filtered_df['date'] = pd.to_datetime(filtered_df['date'], errors='coerce')
        filtered_df['month'] = filtered_df['date'].dt.month
        filtered_df['month_name'] = filtered_df['date'].dt.strftime('%b') if not filtered_df['date'].isna().all() else ''
        filtered_df['year'] = filtered_df['date'].dt.year
        filtered_df['hour'] = filtered_df['timestamp'].dt.hour
        filtered_df['day_of_week'] = filtered_df['date'].dt.day_name()
    if filtered_df.empty or pd.isna(filtered_df['timestamp'].max()):
        last_updated = "No valid timestamp available"
    else:
        last_updated = filtered_df['timestamp'].max().strftime('%b %d, %Y %H:%M %p')
    if filtered_df.empty:
        return html.Div("No data available for the selected filters", className="text-center mt-4", style={"fontFamily": "Poppins"})
    if active_tab == 'overview':
        return render_overview_tab(filtered_df, last_updated)
    elif active_tab == 'dataset':
        return render_dataset_tab(filtered_df)
    elif active_tab == 'geographic':
        return render_geographic_tab(filtered_df)
    elif active_tab == 'time':
        return render_time_tab(filtered_df, time_granularity)
    elif active_tab == 'job_types':
        return render_job_types_tab(filtered_df)
    elif active_tab == 'features':
        return render_features_tab(filtered_df)
    elif active_tab == 'demographics':
        return render_demographics_tab(filtered_df)
    elif active_tab == 'statistics':
        return render_statistics_tab(filtered_df)
    else:
        return html.Div("Tab content not implemented yet", style={"fontFamily": "Poppins"})

# Overview tab content
def render_overview_tab(filtered_df, last_updated):
    if filtered_df.empty:
        return html.Div("No data available for the selected filters", className="text-center mt-4", style={"fontFamily": "Poppins"})
    total_job_requests = len(filtered_df)
    demo_requests = len(filtered_df[filtered_df['interaction_type'] == 'Demo Request'])
    ai_assistant_requests = len(filtered_df[filtered_df['interaction_type'] == 'AI Assistant Request'])
    event_registrations = len(filtered_df[filtered_df['interaction_type'] == 'Event Request'])
    job_requests_change = "+15.4%"
    demo_requests_change = "+8.7%"
    ai_assistant_change = "+25.3%"
    event_registrations_change = "-2.7%"
    time_data = filtered_df.groupby(['year', 'month', 'month_name']).size().reset_index(name='count')
    time_data = time_data.sort_values(['year', 'month'])
    job_requests_fig = px.line(
        time_data,
        x='month_name',
        y='count',
        markers=True,
        labels={'count': 'Interactions', 'month_name': 'Month'},
        color_discrete_sequence=[colors['primary']],
        title=""
    )
    trend_line = go.Scatter(
        x=time_data['month_name'],
        y=time_data['count'] * 0.9,
        mode='lines',
        name='Trend Line',
        line=dict(color='orange', dash='dash')
    )
    prev_year_line = go.Scatter(
        x=time_data['month_name'],
        y=time_data['count'] * 0.7,
        mode='lines',
        name='Previous Year',
        line=dict(color='gray', dash='dot')
    )
    job_requests_fig.add_trace(trend_line)
    job_requests_fig.add_trace(prev_year_line)
    job_requests_fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_title="Month",
        yaxis_title="Number of Interactions",
        height=350,
        width=500,
        autosize=True,
        paper_bgcolor='#F5F7FA',
        plot_bgcolor='#F5F7FA',
        xaxis=dict(showgrid=False, title_font=dict(family="Poppins", size=14)),
        yaxis=dict(showgrid=True, gridcolor='lightgray', title_font=dict(family="Poppins", size=14)),
        showlegend=False,
        title_font=dict(family="Poppins", size=16, color="#4a6baf"),
        font=dict(family="Poppins")
    )
    job_types = filtered_df['job_type'].value_counts().reset_index()
    job_types.columns = ['job_type', 'count']
    job_types_fig = px.treemap(
        job_types,
        path=['job_type'],
        values='count',
        color='job_type',
        color_discrete_map=colors['job_types'],
        title=""
    )
    job_types_fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        height=350,
        width=500,
        autosize=True,
        paper_bgcolor='#F5F7FA',
        plot_bgcolor='#F5F7FA',
        showlegend=False,
        title_font=dict(family="Poppins", size=16, color="#4a6baf"),
        font=dict(family="Poppins")
    )
    last_updated = datetime(2025, 5, 23, 0, 11).strftime('%b %d, %Y %H:%M %p CAT')
    return html.Div([
        html.Div([
            html.H4("Overview", className="mb-0", style={"fontFamily": "Poppins"}),
            html.Small(f"Last updated: {last_updated}", className="text-muted", style={"fontFamily": "Poppins"}),
        ], className="d-flex justify-content-between align-items-center mb-4"),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6([
                            "📊 Total Interactions",
                            dbc.Tooltip("Total number of all interactions recorded", target="total-interactions"),
                        ], id="total-interactions", className="card-subtitle text-white mb-1", style={"fontFamily": "Poppins"}),
                        html.H3(f"{total_job_requests:,}", className="card-title mb-2 text-white", style={"fontFamily": "Poppins"}),
                        html.Div([
                            html.Span("↑", className="text-white me-1"),
                            html.Small(job_requests_change, className="text-white", style={"fontFamily": "Poppins"}),
                        ], className="d-flex align-items-center"),
                    ], className="bg-primary text-white")
                ], className="h-100 shadow-sm rounded-3", style={"minHeight": "120px"})
            ], width=12, sm=6, md=3, className="mb-4"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6([
                            "🎥 Demo Requests",
                            dbc.Tooltip("Number of demo requests received", target="demo-requests"),
                        ], id="demo-requests", className="card-subtitle text-white mb-1", style={"fontFamily": "Poppins"}),
                        html.H3(f"{demo_requests:,}", className="card-title mb-2 text-white", style={"fontFamily": "Poppins"}),
                        html.Div([
                            html.Span("↑", className="text-white me-1"),
                            html.Small(demo_requests_change, className="text-white", style={"fontFamily": "Poppins"}),
                        ], className="d-flex align-items-center"),
                    ], className="bg-success text-white")
                ], className="h-100 shadow-sm rounded-3", style={"minHeight": "120px"})
            ], width=12, sm=6, md=3, className="mb-4"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6([
                            "🤖 AI Assistant Requests",
                            dbc.Tooltip("Number of AI assistant requests received", target="ai-assistant-requests"),
                        ], id="ai-assistant-requests", className="card-subtitle text-white mb-1", style={"fontFamily": "Poppins"}),
                        html.H3(f"{ai_assistant_requests:,}", className="card-title mb-2 text-white", style={"fontFamily": "Poppins"}),
                        html.Div([
                            html.Span("↑", className="text-white me-1"),
                            html.Small(ai_assistant_change, className="text-white", style={"fontFamily": "Poppins"}),
                        ], className="d-flex align-items-center"),
                    ], className="bg-info text-white")
                ], className="h-100 shadow-sm rounded-3", style={"minHeight": "120px"})
            ], width=12, sm=6, md=3, className="mb-4"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6([
                            "🎉 Event Registrations",
                            dbc.Tooltip("Number of event registrations recorded", target="event-registrations"),
                        ], id="event-registrations", className="card-subtitle text-white mb-1", style={"fontFamily": "Poppins"}),
                        html.H3(f"{event_registrations:,}", className="card-title mb-2 text-white", style={"fontFamily": "Poppins"}),
                        html.Div([
                            html.Span("↓", className="text-white me-1"),
                            html.Small(event_registrations_change, className="text-white", style={"fontFamily": "Poppins"}),
                        ], className="d-flex align-items-center"),
                    ], className="bg-warning text-white")
                ], className="h-100 shadow-sm rounded-3", style={"minHeight": "120px"})
            ], width=12, sm=6, md=3, className="mb-4"),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            "Interactions Over Time",
                            dbc.Tooltip("Monthly trend of total interactions with trend line and previous year comparison", target="interactions-over-time"),
                        ], id="interactions-over-time", className="card-title mb-2", style={"fontFamily": "Poppins"}),
                        dcc.Graph(
                            id="overview-interactions-graph",
                            figure=job_requests_fig,
                            config={
                                'displayModeBar': True,
                                'modeBarButtonsToAdd': [
                                    'downloadImage',
                                    'pan2d',
                                    'select2d',
                                    'lasso2d',
                                    'zoomIn2d',
                                    'zoomOut2d'
                                ]
                            }
                        ),
                    ])
                ], className="h-100 shadow-sm rounded-3", style={'overflow': 'auto'})
            ], width=12, md=6, className="mb-4"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            "Job Types Distribution",
                            dbc.Tooltip("Treemap showing distribution of different job types", target="job-types-distribution"),
                        ], id="job-types-distribution", className="card-title mb-2", style={"fontFamily": "Poppins"}),
                        dcc.Graph(
                            id="overview-job-types-graph",
                            figure=job_types_fig,
                            config={
                                'displayModeBar': True,
                                'modeBarButtonsToAdd': [
                                    'downloadImage',
                                    'pan2d',
                                    'select2d',
                                    'lasso2d',
                                    'zoomIn2d',
                                    'zoomOut2d'
                                ]
                            }
                        ),
                    ])
                ], className="h-100 shadow-sm rounded-3", style={'overflow': 'auto'})
            ], width=12, md=6, className="mb-4"),
        ]),
    ], style={"fontFamily": "Poppins"})

# Data Explorer tab content
def render_dataset_tab(filtered_df):
    if filtered_df.empty:
        return html.Div("No data available for the selected filters", className="text-center mt-4", style={"fontFamily": "Poppins"})
    date_min = filtered_df['date'].min()
    date_max = filtered_df['date'].max()
    date_range_str = (
        f"{date_min.strftime('%Y-%m-%d')} to {date_max.strftime('%Y-%m-%d')}"
        if not pd.isna(date_min) and not pd.isna(date_max)
        else "Date range not available"
    )
    return html.Div([
        html.H4("Data Explorer", className="mb-4", style={"fontFamily": "Poppins"}),
        dbc.Card([
            dbc.CardBody([
                html.H5([
                    "Data Preview",
                    dbc.Tooltip("Preview of the first 10 records of the filtered dataset", target="data-preview"),
                ], id="data-preview", className="card-title mb-2", style={"fontFamily": "Poppins"}),
                html.Div([
                    html.Button("↑", id="scroll-up-btn", className="btn btn-outline-primary me-2"),
                    html.Button("↓", id="scroll-down-btn", className="btn btn-outline-primary"),
                    dash.dash_table.DataTable(
                        id='data-table',
                        data=filtered_df.head(10).to_dict('records'),
                        columns=[{'name': col, 'id': col} for col in filtered_df.columns],
                        page_size=10,
                        style_table={
                            'overflowX': 'auto',
                            'maxHeight': '400px',
                            'overflowY': 'auto'
                        },
                        style_cell={
                            'textAlign': 'left',
                            'padding': '8px',
                            'minWidth': '100px',
                            'maxWidth': '300px',
                            'whiteSpace': 'normal',
                            'overflow': 'hidden',
                            'textOverflow': 'ellipsis',
                            'fontFamily': 'Poppins'
                        },
                        style_header={
                            'backgroundColor': '#E9EDF4',
                            'fontWeight': 'bold',
                            'border': '1px solid #ddd',
                            'fontFamily': 'Poppins'
                        },
                        style_data={
                            'border': '1px solid #ddd',
                        },
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': '#F5F7FA',
                            }
                        ],
                    ),
                ]),
                html.Div([
                    dbc.Button([
                        "Download Dataset as CSV",
                        dbc.Tooltip("Download the filtered dataset as a CSV file", target="download-dataset-btn"),
                    ], id="download-dataset-btn", color="primary", className="mt-3"),
                    dcc.Download(id="download-dataset-csv"),
                ], className="mt-3 text-center"),
            ])
        ], className="mb-4 shadow-sm rounded-3"),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            "Dataset Statistics",
                            dbc.Tooltip("Key statistics about the filtered dataset", target="dataset-statistics"),
                        ], id="dataset-statistics", className="card-title mb-2", style={"fontFamily": "Poppins"}),
                        html.Div([
                            html.P(f"Total Records: {len(filtered_df):,}", className="mb-2", style={"fontFamily": "Poppins"}),
                            html.P(f"Date Range: {date_range_str}", className="mb-2", style={"fontFamily": "Poppins"}),
                            html.P(f"Number of Countries: {filtered_df['country'].nunique()}", className="mb-2", style={"fontFamily": "Poppins"}),
                            html.P(f"Number of Job Types: {filtered_df['job_type'].nunique()}", className="mb-2", style={"fontFamily": "Poppins"}),
                            html.P(f"Number of Interaction Types: {filtered_df['interaction_type'].nunique()}", className="mb-0", style={"fontFamily": "Poppins"}),
                        ]),
                    ])
                ], className="h-100 shadow-sm rounded-3")
            ], width=12, md=6, className="mb-4"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            "Column Information",
                            dbc.Tooltip("Description of each column in the dataset", target="column-information"),
                        ], id="column-information", className="card-title mb-2", style={"fontFamily": "Poppins"}),
                        html.Div([
                            dash.dash_table.DataTable(
                                data=[
                                    {'Column': 'timestamp', 'Description': 'Date and time of the interaction'},
                                    {'Column': 'ip_address', 'Description': 'IP address of the user'},
                                    {'Column': 'request_method', 'Description': 'HTTP method used (GET, POST, etc.)'},
                                    {'Column': 'date', 'Description': 'Date of the interaction'},
                                    {'Column': 'time', 'Description': 'Time of the interaction'},
                                    {'Column': 'country', 'Description': 'Country of the user'},
                                    {'Column': 'continent', 'Description': 'Continent of the user'},
                                    {'Column': 'interaction_type', 'Description': 'Type of interaction'},
                                    {'Column': 'job_type', 'Description': 'Type of job requested'},
                                    {'Column': 'feature_requested', 'Description': 'Feature requested by the user'},
                                    {'Column': 'age_group', 'Description': 'Age group of the user'},
                                    {'Column': 'gender', 'Description': 'Gender of the user'},
                                ],
                                columns=[
                                    {'name': 'Column', 'id': 'Column'},
                                    {'name': 'Description', 'id': 'Description'},
                                ],
                                style_table={'overflowX': 'auto'},
                                style_cell={
                                    'textAlign': 'left',
                                    'padding': '8px',
                                    'whiteSpace': 'normal',
                                    'overflow': 'hidden',
                                    'textOverflow': 'ellipsis',
                                    'fontFamily': 'Poppins'
                                },
                                style_header={
                                    'backgroundColor': '#E9EDF4',
                                    'fontWeight': 'bold',
                                    'border': '1px solid #ddd',
                                    'fontFamily': 'Poppins'
                                },
                                style_data={
                                    'border': '1px solid #ddd',
                                },
                                style_data_conditional=[
                                    {
                                        'if': {'row_index': 'odd'},
                                        'backgroundColor': '#F5F7FA',
                                    }
                                ],
                            ),
                        ], style={'overflowX': 'auto'}),
                    ])
                ], className="h-100 shadow-sm rounded-3")
            ], width=12, md=6, className="mb-4"),
        ]),
    ], style={"fontFamily": "Poppins"})

# Geo-sales Insights tab content
def render_geographic_tab(filtered_df):
    if filtered_df.empty:
        return html.Div("No data available for the selected filters", className="text-center mt-4", style={"fontFamily": "Poppins"})
    top_countries = filtered_df['country'].value_counts().head(10).index.tolist()
    feature_country = filtered_df[filtered_df['country'].isin(top_countries)].groupby(['country', 'feature_requested']).size().reset_index(name='count')
    feature_country = feature_country.sort_values('count', ascending=False)
    feature_country_fig = px.bar(
        feature_country,
        x='country',
        y='count',
        color='feature_requested',
        barmode='group',
        labels={'count': 'Number of Requests', 'country': 'Country', 'feature_requested': 'Feature'},
        color_discrete_map={
            'dashboard': colors['ai_assistant'],
            'promo_event': colors['event_registrations'],
            'job_posting': colors['job_requests'],
            'scheduled_demo': colors['demo_requests'],
            'report_generator': colors['job_types']['Data Analyst'],
            'ai_virtual_assistant': colors['ai_assistant']
        },
        title=""
    )
    feature_country_fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_title="Country",
        yaxis_title="Number of Requests",
        height=350,
        width=500,
        autosize=True,
        paper_bgcolor='#F5F7FA',
        plot_bgcolor='#F5F7FA',
        xaxis=dict(showgrid=False, title_font=dict(family="Poppins", size=14)),
        yaxis=dict(showgrid=True, gridcolor='lightgray', title_font=dict(family="Poppins", size=14)),
        showlegend=True,
        title_font=dict(family="Poppins", size=16, color="#4a6baf"),
        font=dict(family="Poppins")
    )
    job_counts = filtered_df[filtered_df['interaction_type'] == 'Job Placement'].groupby('country').size().reset_index(name='count')
    choropleth_fig = px.choropleth(
        job_counts,
        locations='country',
        locationmode='country names',
        color='count',
        color_continuous_scale='Blues',
        labels={'count': 'Number of Jobs Placed'},
        title=""
    )
    choropleth_fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        height=350,
        width=500,
        autosize=True,
        paper_bgcolor='#F5F7FA',
        plot_bgcolor='#F5F7FA',
        geo=dict(showframe=False, showcoastlines=True, projection_type='equirectangular'),
        showlegend=True,
        title_font=dict(family="Poppins", size=16, color="#4a6baf"),
        font=dict(family="Poppins")
    )
    return html.Div([
        html.H4("Geo-sales Insights", className="mb-4", style={"fontFamily": "Poppins"}),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            "Feature Requests of Top 10 Countries",
                            dbc.Tooltip("Bar chart showing feature requests by top 10 countries", target="geo-feature-country"),
                        ], id="geo-feature-country", className="card-title mb-2", style={"fontFamily": "Poppins"}),
                        dcc.Graph(
                            id="geo-feature-country-graph",
                            figure=feature_country_fig,
                            config={
                                'displayModeBar': True,
                                'modeBarButtonsToAdd': [
                                    'downloadImage',
                                    'pan2d',
                                    'select2d',
                                    'lasso2d',
                                    'zoomIn2d',
                                    'zoomOut2d'
                                ]
                            }
                        ),
                    ])
                ], className="h-100 shadow-sm rounded-3", style={'overflow': 'auto'})
            ], width=12, md=6, className="mb-4"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            "Jobs Placed by Country",
                            dbc.Tooltip("Choropleth map showing job placements by country", target="geo-jobs-country"),
                        ], id="geo-jobs-country", className="card-title mb-2", style={"fontFamily": "Poppins"}),
                        dcc.Graph(
                            id="geo-jobs-country-graph",
                            figure=choropleth_fig,
                            config={
                                'displayModeBar': True,
                                'modeBarButtonsToAdd': [
                                    'downloadImage',
                                    'pan2d',
                                    'select2d',
                                    'lasso2d',
                                    'zoomIn2d',
                                    'zoomOut2d'
                                ]
                            }
                        ),
                    ])
                ], className="h-100 shadow-sm rounded-3", style={'overflow': 'auto'})
            ], width=12, md=6, className="mb-4"),
        ]),
    ], style={"fontFamily": "Poppins"})

# Sales Trend Over Time tab content
def render_time_tab(filtered_df, time_granularity):
    if filtered_df.empty:
        return html.Div("No data available for the selected filters", className="text-center mt-4", style={"fontFamily": "Poppins"})
    if time_granularity == 'daily':
        feature_time = filtered_df.groupby(['date', 'feature_requested']).size().reset_index(name='count')
        feature_time['date'] = pd.to_datetime(feature_time['date'])
        x_label = 'Date'
    elif time_granularity == 'weekly':
        feature_time = filtered_df.groupby([pd.Grouper(key='date', freq='W'), 'feature_requested']).size().reset_index(name='count')
        feature_time['date'] = pd.to_datetime(feature_time['date'])
        x_label = 'Week'
    elif time_granularity == 'monthly':
        feature_time = filtered_df.groupby([pd.Grouper(key='date', freq='M'), 'feature_requested']).size().reset_index(name='count')
        feature_time['date'] = pd.to_datetime(feature_time['date']).dt.strftime('%Y-%m')
        x_label = 'Month'
    elif time_granularity == 'yearly':
        feature_time = filtered_df.groupby([pd.Grouper(key='date', freq='Y'), 'feature_requested']).size().reset_index(name='count')
        feature_time['date'] = pd.to_datetime(feature_time['date']).dt.year
        x_label = 'Year'
    feature_time = feature_time.sort_values('date')
    daily_fig = px.line(
        feature_time,
        x='date',
        y='count',
        color='feature_requested',
        labels={'count': 'Number of Requests', 'date': x_label, 'feature_requested': 'Feature'},
        color_discrete_map={
            'dashboard': colors['ai_assistant'],
            'promo_event': colors['event_registrations'],
            'job_posting': colors['job_requests'],
            'scheduled_demo': colors['demo_requests'],
            'report_generator': colors['job_types']['Data Analyst'],
            'ai_virtual_assistant': colors['ai_assistant']
        },
        title=""
    )
    daily_fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_title=x_label,
        yaxis_title="Number of Requests",
        height=350,
        width=500,
        autosize=True,
        paper_bgcolor='#F5F7FA',
        plot_bgcolor='#F5F7FA',
        xaxis=dict(showgrid=False, title_font=dict(family="Poppins", size=14)),
        yaxis=dict(showgrid=True, gridcolor='lightgray', title_font=dict(family="Poppins", size=14)),
        showlegend=True,
        title_font=dict(family="Poppins", size=16, color="#4a6baf"),
        font=dict(family="Poppins")
    )
    hourly_dist = filtered_df.groupby(['day_of_week', 'hour']).size().reset_index(name='count')
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    hourly_dist['day_of_week'] = pd.Categorical(hourly_dist['day_of_week'], categories=day_order, ordered=True)
    hourly_dist = hourly_dist.pivot(index='day_of_week', columns='hour', values='count').fillna(0)
    heatmap_fig = px.imshow(
        hourly_dist,
        labels=dict(x='Hour of Day', y='Day of Week', color='Interaction Count'),
        color_continuous_scale='Blues',
        title=""
    )
    heatmap_fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_title="Hour of Day",
        yaxis_title="Day of Week",
        height=350,
        width=500,
        autosize=True,
        paper_bgcolor='#F5F7FA',
        plot_bgcolor='#F5F7FA',
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(24)),
            ticktext=[f"{i}:00" for i in range(24)],
            tickfont=dict(size=10, color='black', family="Poppins"),
            tickangle=45,
            title_font=dict(family="Poppins", size=14)
        ),
        yaxis=dict(
            autorange='reversed',
            tickfont=dict(size=10, color='black', family="Poppins"),
            title_font=dict(family="Poppins", size=14)
        ),
        showlegend=True,
        title_font=dict(family="Poppins", size=16, color="#4a6baf"),
        font=dict(family="Poppins")
    )
    return html.Div([
        html.H4("Sales Trend Over Time", className="mb-4", style={"fontFamily": "Poppins"}),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            f"{time_granularity.capitalize()} Feature Trends",
                            dbc.Tooltip(f"Line chart showing feature request trends over {time_granularity} periods", target="time-feature-trends"),
                        ], id="time-feature-trends", className="card-title mb-2", style={"fontFamily": "Poppins"}),
                        dcc.Graph(
                            id="time-feature-trends-graph",
                            figure=daily_fig,
                            config={
                                'displayModeBar': True,
                                'modeBarButtonsToAdd': [
                                    'downloadImage',
                                    'pan2d',
                                    'select2d',
                                    'lasso2d',
                                    'zoomIn2d',
                                    'zoomOut2d'
                                ]
                            }
                        ),
                    ])
                ], className="h-100 shadow-sm rounded-3", style={'overflow': 'auto'})
            ], width=12, md=6, className="mb-4"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            "Hourly Interaction Distribution",
                            dbc.Tooltip("Heatmap showing interaction distribution by day and hour", target="time-hourly-dist"),
                        ], id="time-hourly-dist", className="card-title mb-2", style={"fontFamily": "Poppins"}),
                        dcc.Graph(
                            id="time-hourly-dist-graph",
                            figure=heatmap_fig,
                            config={
                                'displayModeBar': True,
                                'modeBarButtonsToAdd': [
                                    'downloadImage',
                                    'pan2d',
                                    'select2d',
                                    'lasso2d',
                                    'zoomIn2d',
                                    'zoomOut2d'
                                ]
                            }
                        ),
                    ])
                ], className="h-100 shadow-sm rounded-3", style={'overflow': 'auto'})
            ], width=12, md=6, className="mb-4"),
        ]),
    ], style={"fontFamily": "Poppins"})

# Job Types Analysis tab content
def render_job_types_tab(filtered_df):
    if filtered_df.empty:
        return html.Div("No data available for the selected filters", className="text-center mt-4", style={"fontFamily": "Poppins"})
    job_country = filtered_df.groupby(['country', 'job_type']).size().reset_index(name='count')
    top_countries = filtered_df['country'].value_counts().head(10).index.tolist()
    job_country_filtered = job_country[job_country['country'].isin(top_countries)]
    job_country_fig = px.area(
        job_country_filtered,
        x='country',
        y='count',
        color='job_type',
        labels={'count': 'Number of Requests', 'country': 'Country', 'job_type': 'Job Type'},
        color_discrete_map=colors['job_types'],
        title=""
    )
    job_country_fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_title="Country",
        yaxis_title="Number of Requests",
        height=350,
        width=500,
        autosize=True,
        paper_bgcolor='#F5F7FA',
        plot_bgcolor='#F5F7FA',
        xaxis=dict(showgrid=False, tickangle=45, title_font=dict(family="Poppins", size=14)),
        yaxis=dict(showgrid=True, gridcolor='lightgray', title_font=dict(family="Poppins", size=14)),
        showlegend=True,
        title_font=dict(family="Poppins", size=16, color="#4a6baf"),
        font=dict(family="Poppins")
    )
    job_age = filtered_df.groupby(['age_group', 'job_type']).size().reset_index(name='count')
    job_age_fig = px.pie(
        job_age,
        values='count',
        names='job_type',
        color='job_type',
        color_discrete_map=colors['job_types'],
        title="",
        category_orders={'age_group': sorted(job_age['age_group'].unique())}
    )
    job_age_fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        height=350,
        width=500,
        autosize=True,
        paper_bgcolor='#F5F7FA',
        plot_bgcolor='#F5F7FA',
        showlegend=True,
        title_font=dict(family="Poppins", size=16, color="#4a6baf"),
        font=dict(family="Poppins")
    )
    return html.Div([
        html.H4("Job Types Analysis", className="mb-4", style={"fontFamily": "Poppins"}),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            "Job Types by Country",
                            dbc.Tooltip("Area chart showing job type distribution across top countries", target="job-types-country"),
                        ], id="job-types-country", className="card-title mb-2", style={"fontFamily": "Poppins"}),
                        dcc.Graph(
                            id="job-types-country-graph",
                            figure=job_country_fig,
                            config={
                                'displayModeBar': True,
                                'modeBarButtonsToAdd': [
                                    'downloadImage',
                                    'pan2d',
                                    'select2d',
                                    'lasso2d',
                                    'zoomIn2d',
                                    'zoomOut2d'
                                ]
                            }
                        ),
                    ])
                ], className="h-100 shadow-sm rounded-3", style={'overflow': 'auto'})
            ], width=12, md=6, className="mb-4"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            "Job Types by Age Group",
                            dbc.Tooltip("Pie chart showing job type distribution by age group", target="job-types-age"),
                        ], id="job-types-age", className="card-title mb-2", style={"fontFamily": "Poppins"}),
                        dcc.Graph(
                            id="job-types-age-graph",
                            figure=job_age_fig,
                            config={
                                'displayModeBar': True,
                                'modeBarButtonsToAdd': [
                                    'downloadImage',
                                    'pan2d',
                                    'select2d',
                                    'lasso2d',
                                    'zoomIn2d',
                                    'zoomOut2d'
                                ]
                            }
                        ),
                    ])
                ], className="h-100 shadow-sm rounded-3", style={'overflow': 'auto'})
            ], width=12, md=6, className="mb-4"),
        ]),
    ], style={"fontFamily": "Poppins"})

# Feature Requests tab content
def render_features_tab(filtered_df):
    if filtered_df.empty:
        return html.Div("No data available for the selected filters", className="text-center mt-4", style={"fontFamily": "Poppins"})
    features = filtered_df['feature_requested'].value_counts().reset_index()
    features.columns = ['feature', 'count']
    features_fig = px.pie(
        features,
        values='count',
        names='feature',
        hole=0.4,
        color='feature',
        color_discrete_map={
            'dashboard': colors['ai_assistant'],
            'promo_event': colors['event_registrations'],
            'job_posting': colors['job_requests'],
            'scheduled_demo': colors['demo_requests'],
            'report_generator': colors['job_types']['Data Analyst'],
            'ai_virtual_assistant': colors['ai_assistant']
        },
        title=""
    )
    features_fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        height=350,
        width=500,
        autosize=True,
        paper_bgcolor='#F5F7FA',
        plot_bgcolor='#F5F7FA',
        showlegend=True,
        title_font=dict(family="Poppins", size=16, color="#4a6baf"),
        font=dict(family="Poppins")
    )
    feature_pivot = filtered_df.pivot_table(index='ip_address', columns='feature_requested', aggfunc='size', fill_value=0)
    feature_corr = feature_pivot.corr()
    feature_corr_fig = px.imshow(
        feature_corr,
        labels=dict(x='Feature', y='Feature', color='Correlation'),
        color_continuous_scale='Blues',
        title=""
    )
    feature_corr_fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_title="Feature",
        yaxis_title="Feature",
        height=350,
        width=500,
        autosize=True,
        paper_bgcolor='#F5F7FA',
        plot_bgcolor='#F5F7FA',
        xaxis=dict(tickfont=dict(size=10, family="Poppins"), tickangle=45, title_font=dict(family="Poppins", size=14)),
        yaxis=dict(tickfont=dict(size=10, family="Poppins"), title_font=dict(family="Poppins", size=14)),
        showlegend=True,
        title_font=dict(family="Poppins", size=16, color="#4a6baf"),
        font=dict(family="Poppins")
    )
    return html.Div([
        html.H4("Feature Requests Analysis", className="mb-4", style={"fontFamily": "Poppins"}),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            "Feature Requests by Type",
                            dbc.Tooltip("Pie chart showing distribution of feature requests", target="features-type"),
                        ], id="features-type", className="card-title mb-2", style={"fontFamily": "Poppins"}),
                        dcc.Graph(
                            id="features-type-graph",
                            figure=features_fig,
                            config={
                                'displayModeBar': True,
                                'modeBarButtonsToAdd': [
                                    'downloadImage',
                                    'pan2d',
                                    'select2d',
                                    'lasso2d',
                                    'zoomIn2d',
                                    'zoomOut2d'
                                ]
                            }
                        ),
                    ])
                ], className="h-100 shadow-sm rounded-3", style={'overflow': 'auto'})
            ], width=12, md=6, className="mb-4"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            "Feature Request Correlations",
                            dbc.Tooltip("Heatmap showing correlations between feature requests", target="features-corr"),
                        ], id="features-corr", className="card-title mb-2", style={"fontFamily": "Poppins"}),
                        dcc.Graph(
                            id="features-corr-graph",
                            figure=feature_corr_fig,
                            config={
                                'displayModeBar': True,
                                'modeBarButtonsToAdd': [
                                    'downloadImage',
                                    'pan2d',
                                    'select2d',
                                    'lasso2d',
                                    'zoomIn2d',
                                    'zoomOut2d'
                                ]
                            }
                        ),
                    ])
                ], className="h-100 shadow-sm rounded-3", style={'overflow': 'auto'})
            ], width=12, md=6, className="mb-4"),
        ]),
    ], style={"fontFamily": "Poppins"})

# Demographic Insights tab content
def render_demographics_tab(filtered_df):
    if filtered_df.empty:
        return html.Div("No data available for the selected filters", className="text-center mt-4", style={"fontFamily": "Poppins"})
    age_gender = filtered_df.groupby(['age_group', 'gender']).size().reset_index(name='count')
    age_gender_fig = px.bar(
        age_gender,
        x='age_group',
        y='count',
        color='gender',
        barmode='group',
        labels={'count': 'Number of Interactions', 'age_group': 'Age Group', 'gender': 'Gender'},
        color_discrete_map=colors['gender'],
        title=""
    )
    age_gender_fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_title="Age Group",
        yaxis_title="Number of Interactions",
        height=350,
        width=500,
        autosize=True,
        paper_bgcolor='#F5F7FA',
        plot_bgcolor='#F5F7FA',
        xaxis=dict(showgrid=False, title_font=dict(family="Poppins", size=14)),
        yaxis=dict(showgrid=True, gridcolor='lightgray', title_font=dict(family="Poppins", size=14)),
        showlegend=True,
        title_font=dict(family="Poppins", size=16, color="#4a6baf"),
        font=dict(family="Poppins")
    )
    gender_job = filtered_df.groupby(['gender', 'job_type']).size().reset_index(name='count')
    gender_job_fig = px.bar(
        gender_job,
        x='gender',
        y='count',
        color='job_type',
        barmode='stack',
        labels={'count': 'Number of Requests', 'gender': 'Gender', 'job_type': 'Job Type'},
        color_discrete_map=colors['job_types'],
        title=""
    )
    gender_job_fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_title="Gender",
        yaxis_title="Number of Requests",
        height=350,
        width=500,
        autosize=True,
        paper_bgcolor='#F5F7FA',
        plot_bgcolor='#F5F7FA',
        xaxis=dict(showgrid=False, title_font=dict(family="Poppins", size=14)),
        yaxis=dict(showgrid=True, gridcolor='lightgray', title_font=dict(family="Poppins", size=14)),
        showlegend=True,
        title_font=dict(family="Poppins", size=16, color="#4a6baf"),
        font=dict(family="Poppins")
    )
    return html.Div([
        html.H4("Demographic Insights", className="mb-4", style={"fontFamily": "Poppins"}),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            "Interactions by Age Group and Gender",
                            dbc.Tooltip("Bar chart showing interaction distribution by age group and gender", target="demo-age-gender"),
                        ], id="demo-age-gender", className="card-title mb-2", style={"fontFamily": "Poppins"}),
                        dcc.Graph(
                            id="demo-age-gender-graph",
                            figure=age_gender_fig,
                            config={
                                'displayModeBar': True,
                                'modeBarButtonsToAdd': [
                                    'downloadImage',
                                    'pan2d',
                                    'select2d',
                                    'lasso2d',
                                    'zoomIn2d',
                                    'zoomOut2d'
                                ]
                            }
                        ),
                    ])
                ], className="h-100 shadow-sm rounded-3", style={'overflow': 'auto'})
            ], width=12, md=6, className="mb-4"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            "Job Types by Gender",
                            dbc.Tooltip("Stacked bar chart showing job type distribution by gender", target="demo-gender-job"),
                        ], id="demo-gender-job", className="card-title mb-2", style={"fontFamily": "Poppins"}),
                        dcc.Graph(
                            id="demo-gender-job-graph",
                            figure=gender_job_fig,
                            config={
                                'displayModeBar': True,
                                'modeBarButtonsToAdd': [
                                    'downloadImage',
                                    'pan2d',
                                    'select2d',
                                    'lasso2d',
                                    'zoomIn2d',
                                    'zoomOut2d'
                                ]
                            }
                        ),
                    ])
                ], className="h-100 shadow-sm rounded-3", style={'overflow': 'auto'})
            ], width=12, md=6, className="mb-4"),
        ]),
    ], style={"fontFamily": "Poppins"})

# Statistical Insights tab content
def render_statistics_tab(filtered_df):
    if filtered_df.empty:
        return html.Div("No data available for the selected filters", className="text-center mt-4", style={"fontFamily": "Poppins"})
    
    # Interaction Type Distribution
    stats = filtered_df.groupby(['interaction_type']).size().reset_index(name='count')
    stats_fig = px.histogram(
        stats,
        x='interaction_type',
        y='count',
        labels={'count': 'Number of Interactions', 'interaction_type': 'Interaction Type'},
        color_discrete_sequence=[colors['primary']],
        title=""
    )
    stats_fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_title="Interaction Type",
        yaxis_title="Number of Interactions",
        height=350,
        width=500,
        autosize=True,
        paper_bgcolor='#F5F7FA',
        plot_bgcolor='#F5F7FA',
        xaxis=dict(showgrid=False, tickangle=45, title_font=dict(family="Poppins", size=14)),
        yaxis=dict(showgrid=True, gridcolor='lightgray', title_font=dict(family="Poppins", size=14)),
        showlegend=False,
        title_font=dict(family="Poppins", size=16, color="#4a6baf"),
        font=dict(family="Poppins")
    )
    
    # Feature Request Distribution
    feature_stats = filtered_df.groupby(['feature_requested']).size().reset_index(name='count')
    feature_box_fig = px.box(
        filtered_df,
        x='feature_requested',
        y=filtered_df.index,
        labels={'feature_requested': 'Feature Requested'},
        color='feature_requested',
        color_discrete_map={
            'dashboard': colors['ai_assistant'],
            'promo_event': colors['event_registrations'],
            'job_posting': colors['job_requests'],
            'scheduled_demo': colors['demo_requests'],
            'report_generator': colors['job_types']['Data Analyst'],
            'ai_virtual_assistant': colors['ai_assistant']
        },
        title=""
    )
    feature_box_fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_title="Feature Requested",
        yaxis_title="Index",
        height=350,
        width=500,
        autosize=True,
        paper_bgcolor='#F5F7FA',
        plot_bgcolor='#F5F7FA',
        xaxis=dict(showgrid=False, tickangle=45, title_font=dict(family="Poppins", size=14)),
        yaxis=dict(showgrid=True, gridcolor='lightgray', title_font=dict(family="Poppins", size=14)),
        showlegend=True,
        title_font=dict(family="Poppins", size=16, color="#4a6baf"),
        font=dict(family="Poppins")
    )
    
    # Feature Request Statistics Table
    feature_stats_table = filtered_df.groupby('feature_requested').size().reset_index(name='count')
    feature_stats_table['Mean Requests'] = feature_stats_table['count'].mean()
    feature_stats_table['Std Dev Requests'] = feature_stats_table['count'].std()
    feature_stats_table = feature_stats_table[['feature_requested', 'count', 'Mean Requests', 'Std Dev Requests']]
    feature_stats_table.columns = ['Feature', 'Total Requests', 'Mean Requests', 'Std Dev Requests']
    feature_stats_table['Mean Requests'] = feature_stats_table['Mean Requests'].round(2)
    feature_stats_table['Std Dev Requests'] = feature_stats_table['Std Dev Requests'].round(2)
    
    return html.Div([
        html.H4("Statistical Insights", className="mb-4", style={"fontFamily": "Poppins"}),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            "Interaction Type Distribution",
                            dbc.Tooltip("Histogram showing distribution of interaction types", target="stats-interaction-dist"),
                        ], id="stats-interaction-dist", className="card-title mb-2", style={"fontFamily": "Poppins"}),
                        dcc.Graph(
                            id="stats-interaction-dist-graph",
                            figure=stats_fig,
                            config={
                                'displayModeBar': True,
                                'modeBarButtonsToAdd': [
                                    'downloadImage',
                                    'pan2d',
                                    'select2d',
                                    'lasso2d',
                                    'zoomIn2d',
                                    'zoomOut2d'
                                ]
                            }
                        ),
                    ])
                ], className="h-100 shadow-sm rounded-3", style={'overflow': 'auto'})
            ], width=12, md=6, className="mb-4"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            "Feature Request Distribution",
                            dbc.Tooltip("Box plot showing distribution of feature requests", target="stats-feature-box"),
                        ], id="stats-feature-box", className="card-title mb-2", style={"fontFamily": "Poppins"}),
                        dcc.Graph(
                            id="stats-feature-box-graph",
                            figure=feature_box_fig,
                            config={
                                'displayModeBar': True,
                                'modeBarButtonsToAdd': [
                                    'downloadImage',
                                    'pan2d',
                                    'select2d',
                                    'lasso2d',
                                    'zoomIn2d',
                                    'zoomOut2d'
                                ]
                            }
                        ),
                    ])
                ], className="h-100 shadow-sm rounded-3", style={'overflow': 'auto'})
            ], width=12, md=6, className="mb-4"),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            "Feature Request Statistics",
                            dbc.Tooltip("Table showing mean and standard deviation of requests per feature", target="stats-feature-table"),
                        ], id="stats-feature-table", className="card-title mb-2", style={"fontFamily": "Poppins"}),
                        dash.dash_table.DataTable(
                            id='stats-feature-table-data',
                            data=feature_stats_table.to_dict('records'),
                            columns=[
                                {'name': 'Feature', 'id': 'Feature'},
                                {'name': 'Total Requests', 'id': 'Total Requests'},
                                {'name': 'Mean Requests', 'id': 'Mean Requests'},
                                {'name': 'Std Dev Requests', 'id': 'Std Dev Requests'},
                            ],
                            style_table={
                                'overflowX': 'auto',
                                'maxHeight': '350px',
                                'overflowY': 'auto'
                            },
                            style_cell={
                                'textAlign': 'left',
                                'padding': '8px',
                                'minWidth': '100px',
                                'maxWidth': '300px',
                                'whiteSpace': 'normal',
                                'overflow': 'hidden',
                                'textOverflow': 'ellipsis',
                                'fontFamily': 'Poppins'
                            },
                            style_header={
                                'backgroundColor': '#E9EDF4',
                                'fontWeight': 'bold',
                                'border': '1px solid #ddd',
                                'fontFamily': 'Poppins'
                            },
                            style_data={
                                'border': '1px solid #ddd',
                            },
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': '#F5F7FA',
                                }
                            ],
                        ),
                        html.Div([
                            dbc.Button([
                                "Download Report as CSV",
                                dbc.Tooltip("Download the statistical report as a CSV file", target="download-report-btn"),
                            ], id="download-report-btn", color="primary", className="mt-3"),
                            dcc.Download(id="download-report-csv"),
                        ], className="mt-3 text-center"),
                    ])
                ], className="h-100 shadow-sm rounded-3", style={'overflow': 'auto'})
            ], width=12, className="mb-4"),
        ]),
    ], style={"fontFamily": "Poppins"})

# Download dataset callback
@app.callback(
    Output("download-dataset-csv", "data"),
    [Input("download-dataset-btn", "n_clicks")],
    [State('filtered-data-store', 'data')],
    prevent_initial_call=True
)
def download_dataset(n_clicks, filtered_data_json):
    if filtered_data_json is None:
        filtered_df = df.copy()
    else:
        filtered_df = pd.read_json(StringIO(filtered_data_json), orient='split')
    return dcc.send_data_frame(filtered_df.to_csv, "filtered_dataset.csv")

# Download report callback
@app.callback(
    Output("download-report-csv", "data"),
    [Input("download-report-btn", "n_clicks")],
    [State('filtered-data-store', 'data')],
    prevent_initial_call=True
)
def download_report(n_clicks, filtered_data_json):
    if filtered_data_json is None:
        filtered_df = df.copy()
    else:
        filtered_df = pd.read_json(StringIO(filtered_data_json), orient='split')
    feature_stats_table = filtered_df.groupby('feature_requested').size().reset_index(name='count')
    feature_stats_table['Mean Requests'] = feature_stats_table['count'].mean()
    feature_stats_table['Std Dev Requests'] = feature_stats_table['count'].std()
    feature_stats_table = feature_stats_table[['feature_requested', 'count', 'Mean Requests', 'Std Dev Requests']]
    feature_stats_table.columns = ['Feature', 'Total Requests', 'Mean Requests', 'Std Dev Requests']
    feature_stats_table['Mean Requests'] = feature_stats_table['Mean Requests'].round(2)
    feature_stats_table['Std Dev Requests'] = feature_stats_table['Std Dev Requests'].round(2)
    return dcc.send_data_frame(feature_stats_table.to_csv, "statistical_report.csv")

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
server = app.server