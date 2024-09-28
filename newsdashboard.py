import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Set the theme of the app
st.set_page_config(page_title="Israel-Palestine Conflict Dashboard", layout="wide")

# Customize app appearance
st.markdown("""
    <style>
    body {
        background-color: #f0f2f6;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .css-1d391kg {
        background-color: #f8f9fa !important;
    }
    .reportview-container .main .block-container {
        padding-top: 1rem;
        padding-right: 2rem;
        padding-left: 2rem;
    }
    .stDataFrame {
        margin: 10px;
    }
    .block-container {
        padding: 1rem 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Title and Subtitle
st.title("📊 Israel-Palestine Conflict Data Dashboard")
st.subheader("An interactive dashboard to analyze conflict-related data")

# Sidebar for file upload
st.sidebar.title("Upload Your Dataset")
upload_file = st.sidebar.file_uploader("Choose a CSV file", type='csv')

if upload_file is not None:
    # Load the dataset
    df = pd.read_csv(upload_file)

    # Ensure 'date_of_event' exists and parse dates
    if 'date_of_event' in df.columns:
        df['date_of_event'] = pd.to_datetime(df['date_of_event'], errors='coerce')
        df['year'] = df['date_of_event'].dt.year
    else:
        st.error("The uploaded file must contain a 'date_of_event' column.")

    # Sidebar filters
    st.sidebar.header("Filter Options")
    region_filter = st.sidebar.multiselect("Select Regions", options=df['event_location_region'].unique(), default=df['event_location_region'].unique())
    citizenship_filter = st.sidebar.multiselect("Select Citizenship", options=df['citizenship'].unique(), default=df['citizenship'].unique())
    gender_filter = st.sidebar.radio("Select Gender", options=['All', 'Male', 'Female'], index=0)

    # Filter the dataset based on sidebar inputs
    df_filtered = df[df['event_location_region'].isin(region_filter) & df['citizenship'].isin(citizenship_filter)]

    if gender_filter != 'All':
        df_filtered = df_filtered[df_filtered['gender'] == gender_filter]

    # Display filtered dataset
    st.write(f"Filtered Dataset ({len(df_filtered)} rows):", df_filtered.head())

    # Download filtered data
    st.download_button(label="Download Filtered Data", data=df_filtered.to_csv(index=False), file_name="filtered_data.csv")

    # Data Visualization: Interactive Charts
    st.markdown("---")
    st.header("📊 Data Visualizations")

    # Year Range Slider
    if 'year' in df.columns:
        selected_year = st.slider("Select Year Range", int(df['year'].min()), int(df['year'].max()), (2010, 2020))
        df_filtered = df_filtered[(df_filtered['year'] >= selected_year[0]) & (df_filtered['year'] <= selected_year[1])]

        # Time-based line chart
        df_filtered['month'] = df_filtered['date_of_event'].dt.month_name()
        time_events = df_filtered.groupby(['year', 'month']).size().reset_index(name='incident_count')
        time_events['year_month'] = time_events['month'] + ' ' + time_events['year'].astype(str)

        if not time_events.empty:
            st.subheader("Incident Count Over Time")
            fig = px.line(time_events, x='year_month', y='incident_count', title="Incident Count Over Time")
            fig.update_layout(xaxis_title='Year-Month', yaxis_title='Incident Count')
            st.plotly_chart(fig)
        else:
            st.warning("No data available for the selected year range.")

    # Gender Distribution
    st.subheader("Gender Distribution")
    gender_counts = df_filtered['gender'].value_counts().reset_index()
    gender_counts.columns = ['Gender', 'Count']
    fig = px.pie(gender_counts, names='Gender', values='Count', title="Gender Distribution")
    st.plotly_chart(fig)

    # Citizenship Distribution
    st.subheader("Citizenship Breakdown")
    citizenship_counts = df_filtered['citizenship'].value_counts().reset_index()
    citizenship_counts.columns = ['Citizenship', 'Count']
    fig = px.bar(citizenship_counts, x='Citizenship', y='Count', title="Citizenship Distribution", labels={"Citizenship": "Citizenship", "Count": "Count"})
    st.plotly_chart(fig)

    # Ammunition Analysis
    st.subheader("Ammunition Usage")
    ammunition_counts = df_filtered['ammunition'].value_counts().reset_index()
    ammunition_counts.columns = ['Ammunition', 'Count']
    if not ammunition_counts.empty:
        fig = px.bar(ammunition_counts, x='Ammunition', y='Count', title="Ammunition Distribution", labels={"Ammunition": "Ammunition", "Count": "Count"})
        st.plotly_chart(fig)

    # Region-Based Analysis: Incident Count per Region
    st.subheader("Incidents per Region")
    region_counts = df_filtered['event_location_region'].value_counts().reset_index()
    region_counts.columns = ['Region', 'Count']
    if not region_counts.empty:
        fig = px.bar(region_counts, x='Region', y='Count', title="Incidents per Region", labels={"Region": "Region", "Count": "Incident Count"})
        st.plotly_chart(fig)

    # Age Distribution
    st.subheader("Age Distribution")
    if 'age' in df_filtered.columns and not df_filtered['age'].isnull().all():
        fig = plt.figure()
        sns.histplot(df_filtered['age'].dropna(), bins=20, kde=True)
        plt.title('Age Distribution of Individuals Involved')
        plt.xlabel('Age')
        plt.ylabel('Frequency')
        st.pyplot(fig)
    else:
        st.warning("Age data is not available.")

    # Heatmap for injury types
    st.subheader("Injury Types Heatmap")
    injury_type_counts = df_filtered['type_of_injury'].value_counts().reset_index()
    injury_type_counts.columns = ['Type of Injury', 'Count']
    if not injury_type_counts.empty:
        fig = plt.figure()
        sns.heatmap(injury_type_counts.set_index('Type of Injury'), annot=True, cmap='Blues', cbar=False)
        plt.title("Injury Types Count")
        plt.xlabel('Count')
        st.pyplot(fig)
    else:
        st.warning("No injury type data available.")

    # Average Age by Region Heatmap
    st.subheader("Average Age by Region")
    if 'age' in df_filtered.columns:
        age_distribution = df_filtered.groupby('event_location_region')['age'].mean().reset_index()
        if not age_distribution.empty:
            fig, ax = plt.subplots()
            sns.heatmap(age_distribution.set_index('event_location_region'), annot=True, cmap="coolwarm", ax=ax)
            plt.title("Average Age by Region")
            st.pyplot(fig)
        else:
            st.warning("No average age data available for regions.")

    # Summary Statistics
    st.subheader("Summary Statistics")
    st.write(df_filtered.describe())
else:
    st.write("Please upload a CSV file to analyze the data.")
# Footer
st.sidebar.text("Data analysis dashboard by Devesh Rai")
