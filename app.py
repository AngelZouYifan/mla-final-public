import streamlit as st
import pandas as pd
import json
import plotly.express as px
from datetime import datetime

# Load data
csv_file_path = 'data/output0106.csv'  
json_file_path = 'data/category.json' 
data = pd.read_csv(csv_file_path)

# Load category mapping
with open(json_file_path, 'r') as f:
    categories = json.load(f)

# Data preprocessing
data['start_time'] = pd.to_datetime(data['start_time'], unit='s', errors='coerce').dt.tz_localize('UTC').dt.tz_convert(data['tz'].iloc[0])  # Ensure start_time is datetime, handle errors
data.dropna(subset=['start_time'], inplace=True)  # Drop rows with invalid datetime
data['date'] = data['start_time'].dt.date

# App category mapping
def get_category(app_name):
    for category, details in categories.items():
        if app_name in details['apps']:
            return details['name']
    return "Miscellaneous"

data['category'] = data['app'].apply(get_category)

# UI Layout
st.title("Self-Surveillance")
st.sidebar.header("Filters")

view_option = st.sidebar.radio("Select View", ["Overview View","App-Centered View", "Time-Centric View"])

# st.sidebar.write("Select filters to customize the view.")
# st.sidebar.markdown("---")

# Filter: Time Range
if not data.empty:
    min_date = data['date'].min()
    max_date = data['date'].max()
    date_range = st.sidebar.slider("Select Date Range", min_date, max_date, (min_date, max_date))
    filtered_data = data[(data['date'] >= date_range[0]) & (data['date'] <= date_range[1])]
else:
    st.sidebar.write("No data available for filtering.")
    filtered_data = data

# Filter: Device
devices = filtered_data['device_model'].unique()
selected_devices = st.sidebar.multiselect("Select Devices", devices, default=devices)
filtered_data = filtered_data[filtered_data['device_model'].isin(selected_devices)]

# Filter: Category
category_names = [details['name'] for details in categories.values()]
selected_categories = st.sidebar.multiselect("Select Categories", category_names, default=category_names)
filtered_data = filtered_data[filtered_data['category'].isin(selected_categories)]

# Views
# view_option = st.sidebar.radio("Select View", ["App-Centered View", "Time-Centric View"])

if view_option == "App-Centered View":
    app_names = filtered_data['app'].unique()
    selection_mode = st.radio("Selection Mode", ["Single Select", "Multi Select"])
    # unit_option = st.radio("Select Time Unit", ["Seconds", "Minutes", "Hours"], index=1)
    
    if selection_mode == "Single Select":
        selected_app = st.selectbox("Select App", app_names)
        app_data = filtered_data[filtered_data['app'] == selected_app]
        
        if max(app_data['usage']) > 300 * 60:
            app_data['usage'] = app_data['usage'] / 3600
            unit_label = 'Usage Time (hours)'
        if max(app_data['usage']) > 600:
            app_data['usage'] = app_data['usage'] / 60
            unit_label = 'Usage Time (minutes)'
        else:
            unit_label = 'Usage Time (seconds)'
        
        fig = px.line(app_data, x='start_time', y='usage', title=f"Usage Over Time for {selected_app}", labels={'usage': unit_label})
    else:
        selected_apps = st.multiselect("Select Apps", app_names, default=app_names[:1])
        app_data = filtered_data[filtered_data['app'].isin(selected_apps)]
        grouped_data = app_data.groupby('start_time')['usage'].sum().reset_index()
        
        if grouped_data: 
            if max(grouped_data['usage']) > 300 * 60:
                grouped_data['usage'] = grouped_data['usage'] / 3600
                unit_label = 'Usage Time (hours)'
            elif max(grouped_data['usage']) > 600:
                grouped_data['usage'] = grouped_data['usage'] / 60
                unit_label = 'Usage Time (minutes)'
            else:
                unit_label = 'Usage Time (seconds)'
        
        fig = px.line(grouped_data, x='start_time', y='usage', title=f"Aggregate Usage Over Time for Selected Apps", labels={'usage': unit_label})
    
    st.plotly_chart(fig)

elif view_option == "Time-Centric View":
    time_period = st.radio("Select Time Period", ["1 Day", "7 Days"])
    if time_period == "1 Day":
        grouped_data = filtered_data.groupby(filtered_data['start_time'].dt.hour)['usage'].sum().reset_index()
        fig = px.bar(grouped_data, x='start_time', y='usage', title="App Usage by Hour", labels={'usage': 'Usage Time (minutes)', 'start_time': 'Hour'})
    else:
        grouped_data = filtered_data.groupby(filtered_data['start_time'].dt.date)['usage'].sum().reset_index()
        fig = px.bar(grouped_data, x='start_time', y='usage', title="App Usage Over 7 Days", labels={'usage': 'Usage Time (minutes)', 'start_time': 'Date'})
    st.plotly_chart(fig)

# elif view_option == "Overview View":
#     category_usage = filtered_data.groupby('category')['usage'].sum().reset_index()
#     total_usage = category_usage['usage'].sum()
#     category_usage['percentage'] = (category_usage['usage'] / total_usage) * 100

#     fig = px.pie(category_usage, names='category', values='percentage', title="App Usage by Category")
#     st.plotly_chart(fig)

# Create 100% Stacked Area Chart for Overview View
if view_option == "Overview":
    # Treemap: Category Usage Proportion
    category_usage = filtered_data.groupby('category')['usage'].sum().reset_index()
    total_usage = category_usage['usage'].sum()
    category_usage['percentage'] = (category_usage['usage'] / total_usage) * 100

    treemap_fig = px.treemap(
        filtered_data.groupby(['category', 'app'])['usage'].sum().reset_index(),
        path=['category', 'app'], 
        values='usage', 
        title="App Usage by Category and App (Treemap)",
        hover_data={'usage': ':.2f'},
        color='category'
    )
    st.plotly_chart(treemap_fig)

    # Heatmap: Usage Over Time by Category
    heatmap_data = filtered_data.groupby([filtered_data['start_time'].dt.date, 'category'])['usage'].sum().unstack(fill_value=0)
    heatmap_fig = px.imshow(
        heatmap_data.T,
        labels=dict(x="Date", y="Category", color="Usage Time (s)"),
        title="App Usage Heatmap Over Time",
        aspect="auto",
        color_continuous_scale="Blues"
    )
    st.plotly_chart(heatmap_fig)