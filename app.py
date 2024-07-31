import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objs as go

def load_data(uploaded_file):
    df = pd.read_csv(uploaded_file, low_memory=False)
    df['origin_arrival_time'] = pd.to_datetime(df['origin_arrival_time'], format='%H:%M:%S', errors='coerce')
    df['dest_scheduled_time'] = pd.to_datetime(df['dest_scheduled_time'], format='%H:%M:%S', errors='coerce')
    df['origin_depart_date'] = pd.to_datetime(df['origin_depart_date'], errors='coerce')
    df['dest_scheduled_time'] = df.apply(
        lambda row: row['origin_arrival_time'] + pd.Timedelta(hours=3) if pd.isnull(row['dest_scheduled_time']) and pd.notnull(row['origin_arrival_time']) else row['dest_scheduled_time'],
        axis=1
    )
    
    df['driving_duration'] = (df['dest_scheduled_time'] - df['origin_arrival_time']).dt.total_seconds() / 3600
    df['time_of_day'] = df['origin_arrival_time'].dt.hour.apply(lambda x: 'Morning' if x < 12 else 'Afternoon')
    if 'miles_prime' in df.columns:
        df['color'] = df['miles_prime'].apply(lambda x: 'High (Above 50)' if x > 50 else 'Low (Below 50)')
    
    df = df.dropna(subset=['origin_arrival_time', 'dest_scheduled_time', 'origin_depart_date'])
    return df

uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    df_cleaned = load_data(uploaded_file)
    available_dates = df_cleaned['origin_depart_date'].dt.date.dropna().unique()
    available_dates.sort()
    date_options = ["Select All"] + list(available_dates)
    selected_date_option = st.sidebar.selectbox("Select a date to display the Gantt chart:", date_options)

    if selected_date_option == "Select All":
        filtered_data = df_cleaned
    else:
        filtered_data = df_cleaned[df_cleaned['origin_depart_date'].dt.date == selected_date_option]

    if not filtered_data.empty:
        fig = px.timeline(
            filtered_data,
            x_start="origin_arrival_time",
            x_end="dest_scheduled_time",
            y="Shipment ID",
            color='color',
            labels={"origin_arrival_time": "Start Time", "dest_scheduled_time": "End Time"},
            title="Gantt Chart of Shipments",
            color_discrete_map={'High (Above 50)': 'blue', 'Low (Below 50)': 'red'}
        )
        fig.update_layout(height=800, width=1000)
        fig.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig, use_container_width=True)
        fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'pie'}, {'type': 'pie'}]])
        
        pie_time_data = filtered_data['time_of_day'].value_counts().reset_index()
        pie_time_data.columns = ['TimeOfDay', 'Count']  # Explicitly naming the columns
        pie_time = go.Pie(labels=pie_time_data['TimeOfDay'], values=pie_time_data['Count'], name="Time of Day", title="Time of Day")
        
        pie_color_data = filtered_data['color'].value_counts().reset_index()
        pie_color_data.columns = ['Color', 'Count']  # Explicitly naming the columns
        pie_color = go.Pie(labels=pie_color_data['Color'], values=pie_color_data['Count'], name="Miles Prime Category", title="Miles Prime Category")

        fig.add_trace(pie_time, 1, 1)
        fig.add_trace(pie_color, 1, 2)
        
        fig.update_layout(title_text="Analysis of Shipments: Time of Day and Miles Prime Category")
        st.plotly_chart(fig, use_container_width=True)

        duration_fig = px.histogram(filtered_data, x='driving_duration', nbins=20, title='Distribution of Driving Durations (in hours)')
        st.plotly_chart(duration_fig, use_container_width=True)
    else:
        st.write("No data available for the selected option.")
else:
    st.write("Please upload a CSV file to begin.")
