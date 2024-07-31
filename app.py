import streamlit as st
import pandas as pd
import plotly.express as px

# Function to load data
def load_data(uploaded_file):
    df = pd.read_csv(uploaded_file, low_memory=False)
    # Convert columns to datetime
    df['origin_arrival_time'] = pd.to_datetime(df['origin_arrival_time'], format='%H:%M:%S')
    df['dest_scheduled_time'] = pd.to_datetime(df['dest_scheduled_time'], format='%H:%M:%S')
    df['origin_depart_date'] = pd.to_datetime(df['origin_depart_date'], errors='coerce')
    df['dest_scheduled_time'] = df.apply(
        lambda row: row['origin_arrival_time'] + pd.Timedelta(hours=3) if pd.isnull(row['dest_scheduled_time']) and pd.notnull(row['origin_arrival_time']) else row['dest_scheduled_time'],
        axis=1
    )   
    df = df.dropna(subset=['origin_arrival_time', 'dest_scheduled_time']) 
    return df

# Sidebar for file upload
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    df_cleaned = load_data(uploaded_file)
    if 'miles_prime' in df_cleaned.columns:
        df_cleaned['color'] = df_cleaned['miles_prime'].apply(lambda x: 'High (Above 50)' if x > 50 else 'Low (Below 50)')

    available_dates = df_cleaned['origin_depart_date'].dt.date.unique()
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
        fig.update_yaxes(categoryorder="total ascending")
        fig.update_layout(xaxis_title="Time", yaxis_title="Shipment ID")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No data available for the selected option.")
else:
    st.write("Please upload a CSV file to begin.")

