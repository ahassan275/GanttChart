import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
from datetime import datetime, timedelta
import numpy as np
import io
import base64
import os

# Import the data_converter if it exists
try:
    from data_converter import convert_ups_data
    has_converter = True
except ImportError:
    has_converter = False

st.set_page_config(layout="wide", page_title="UPS Installation Project Gantt Chart")

st.title("UPS Installation Project Gantt Chart")

# Initialize session state for storing tasks data
if 'tasks_data' not in st.session_state:
    # Check if we have a CSV file already
    if os.path.exists('gantt_data.csv'):
        try:
            st.session_state.tasks_data = pd.read_csv('gantt_data.csv')
            # Convert date strings to datetime
            for date_col in ['Start', 'Finish']:
                st.session_state.tasks_data[date_col] = pd.to_datetime(st.session_state.tasks_data[date_col])
        except Exception as e:
            # Fall back to default data if there's an error
            use_default = True
    else:
        use_default = True
        
    # Use default data if needed
    if 'use_default' in locals() and use_default:
        # Initialize with default data
        default_data = {
            'Task': [
                'Planning & Preparation',
                'Data Closet Assessment',
                'Team Assignments',
                'Zone 1 - School A: Delivery',
                'Zone 1 - School A: Installation',
                'Zone 1 - School B: Delivery',
                'Zone 1 - School B: Installation',
                'Zone 2 - School C: Delivery',
                'Zone 2 - School C: Installation',
                'School with Issues - Arch St. PS',
                'School for Revisit - Dunlop PS',
                'Final Documentation'
            ],
            'Resource': [
                'Project Manager',
                'Technical Team',
                'Project Manager',
                'Delivery Team',
                'Installation Team',
                'Delivery Team',
                'Installation Team',
                'Delivery Team',
                'Installation Team',
                'Specialized Team',
                'Maintenance Team',
                'Project Manager'
            ],
            'Start': [
                datetime.now(),
                datetime.now() + timedelta(days=1),
                datetime.now() + timedelta(days=2),
                datetime.now() + timedelta(days=3),
                datetime.now() + timedelta(days=4),
                datetime.now() + timedelta(days=5),
                datetime.now() + timedelta(days=6),
                datetime.now() + timedelta(days=7),
                datetime.now() + timedelta(days=8),
                datetime.now() + timedelta(days=9),
                datetime.now() + timedelta(days=10),
                datetime.now() + timedelta(days=15)
            ],
            'Duration': [2, 3, 1, 1, 1, 1, 1, 1, 1, 2, 1, 3],
            'Finish': [
                datetime.now() + timedelta(days=2),
                datetime.now() + timedelta(days=4),
                datetime.now() + timedelta(days=3),
                datetime.now() + timedelta(days=4),
                datetime.now() + timedelta(days=5),
                datetime.now() + timedelta(days=6),
                datetime.now() + timedelta(days=7),
                datetime.now() + timedelta(days=8),
                datetime.now() + timedelta(days=9),
                datetime.now() + timedelta(days=11),
                datetime.now() + timedelta(days=11),
                datetime.now() + timedelta(days=18)
            ],
            'Completion_pct': [100, 80, 50, 0, 0, 0, 0, 0, 0, 30, 0, 0],
            'Trustee_Zone': [0, 0, 0, 1, 1, 1, 1, 2, 2, 1, 3, 0],
            'Category': [
                'Planning', 'Planning', 'Planning', 
                'Delivery', 'Installation', 
                'Delivery', 'Installation', 
                'Delivery', 'Installation', 
                'Issue Resolution', 'Revisit', 'Closeout'
            ],
            'Notes': [
                '', '', '', '', '', '', '', '', '', 
                'Wall mounted rack issue', 
                'Faulty UPS replacement', 
                ''
            ]
        }
        
        st.session_state.tasks_data = pd.DataFrame(default_data)

# Function to display and edit the data
def display_and_edit_data():
    st.subheader("Task Data")
    
    # Tab layout for different operations
    tab1, tab2, tab3, tab4 = st.tabs(["Edit Data", "Add Task", "Delete Task", "Upload/Download"])
    
    with tab1:
        # Edit existing data
        edited_df = st.data_editor(
            st.session_state.tasks_data,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "Start": st.column_config.DatetimeColumn(
                    "Start Date",
                    format="MM/DD/YYYY",
                ),
                "Finish": st.column_config.DatetimeColumn(
                    "Finish Date",
                    format="MM/DD/YYYY",
                ),
                "Completion_pct": st.column_config.ProgressColumn(
                    "Completion %",
                    min_value=0,
                    max_value=100,
                    format="%d%%",
                ),
                "Trustee_Zone": st.column_config.SelectboxColumn(
                    "Trustee Zone",
                    options=[0, 1, 2, 3, 4, 5, 6, 7],
                    help="0 for non-zone tasks"
                ),
                "Category": st.column_config.SelectboxColumn(
                    "Category",
                    options=[
                        "Planning", "Delivery", "Installation", 
                        "Issue Resolution", "Revisit", "Closeout"
                    ]
                )
            }
        )
        
        if st.button("Update Data"):
            st.session_state.tasks_data = edited_df
            # Save to CSV for persistence
            edited_df.to_csv('gantt_data.csv', index=False)
            st.success("Data updated successfully!")
    
    with tab2:
        # Add new task
        st.subheader("Add New Task")
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_task = st.text_input("Task Name")
            new_resource = st.text_input("Resource")
            new_start = st.date_input("Start Date")
            new_duration = st.number_input("Duration (Days)", min_value=1, value=1)
            
        with col2:
            new_completion = st.slider("Completion %", 0, 100, 0)
            new_zone = st.selectbox("Trustee Zone", options=[0, 1, 2, 3, 4, 5, 6, 7])
            new_category = st.selectbox("Category", options=[
                "Planning", "Delivery", "Installation", 
                "Issue Resolution", "Revisit", "Closeout"
            ])
            new_notes = st.text_input("Notes")
        
        if st.button("Add Task"):
            if new_task:
                new_start_datetime = datetime.combine(new_start, datetime.min.time())
                new_finish = new_start_datetime + timedelta(days=new_duration)
                
                new_row = pd.DataFrame({
                    'Task': [new_task],
                    'Resource': [new_resource],
                    'Start': [new_start_datetime],
                    'Duration': [new_duration],
                    'Finish': [new_finish],
                    'Completion_pct': [new_completion],
                    'Trustee_Zone': [new_zone],
                    'Category': [new_category],
                    'Notes': [new_notes]
                })
                
                st.session_state.tasks_data = pd.concat([st.session_state.tasks_data, new_row], ignore_index=True)
                # Save to CSV for persistence
                st.session_state.tasks_data.to_csv('gantt_data.csv', index=False)
                st.success(f"Task '{new_task}' added successfully!")
            else:
                st.error("Task name is required!")
    
    with tab3:
        # Delete task
        st.subheader("Delete Task")
        
        task_to_delete = st.selectbox(
            "Select Task to Delete",
            options=st.session_state.tasks_data['Task'].tolist()
        )
        
        if st.button("Delete Selected Task"):
            st.session_state.tasks_data = st.session_state.tasks_data[
                st.session_state.tasks_data['Task'] != task_to_delete
            ]
            # Save to CSV for persistence
            st.session_state.tasks_data.to_csv('gantt_data.csv', index=False)
            st.success(f"Task '{task_to_delete}' deleted successfully!")
    
    with tab4:
        # File upload/download
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Upload Data")
            
            # Excel converter (if available)
            if has_converter:
                st.write("### Convert UPS Project Excel File")
                uploaded_excel = st.file_uploader("Upload Excel Spreadsheet", type=["xlsx"])
                
                if uploaded_excel is not None:
                    # Save the uploaded file temporarily
                    with open("temp_upload.xlsx", "wb") as f:
                        f.write(uploaded_excel.getvalue())
                    
                    if st.button("Convert Excel Data"):
                        try:
                            with st.spinner("Converting Excel data..."):
                                df = convert_ups_data("temp_upload.xlsx", "gantt_data.csv")
                                st.session_state.tasks_data = df
                                st.success(f"Excel data converted successfully! Generated {len(df)} tasks.")
                        except Exception as e:
                            st.error(f"Error converting Excel data: {e}")
            
            # CSV upload
            st.write("### Upload CSV directly")
            uploaded_csv = st.file_uploader("Upload CSV", type="csv")
            
            if uploaded_csv is not None:
                try:
                    df = pd.read_csv(uploaded_csv)
                    
                    # Convert date strings to datetime
                    df['Start'] = pd.to_datetime(df['Start'])
                    df['Finish'] = pd.to_datetime(df['Finish'])
                    
                    st.session_state.tasks_data = df
                    # Save to CSV for persistence
                    df.to_csv('gantt_data.csv', index=False)
                    st.success("Data uploaded successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        with col2:
            st.subheader("Download Data")
            
            def get_csv_download_link(df):
                csv = df.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="gantt_tasks.csv">Download CSV File</a>'
                return href
            
            st.markdown(get_csv_download_link(st.session_state.tasks_data), unsafe_allow_html=True)

# Function to create Gantt chart with enhanced filtering
def create_gantt_chart():
    df = st.session_state.tasks_data
    
    # Create a copy of the dataframe for visualization
    chart_data = df.copy()
    
    # Extract school names from tasks for filtering
    # First look for task format like "School Name: Action"
    chart_data['School'] = chart_data['Task'].str.extract(r'^([^:]+):', expand=False)
    # For tasks without colon, use the whole task name
    chart_data.loc[chart_data['School'].isna(), 'School'] = chart_data.loc[chart_data['School'].isna(), 'Task']
    
    # Convert Trustee_Zone to string to ensure consistent handling of mixed types
    chart_data['Trustee_Zone'] = chart_data['Trustee_Zone'].astype(str)
    
    # ADVANCED FILTERING OPTIONS
    with st.sidebar:
        st.subheader("Filter Options")
        
        # Filter by time period
        st.write("### Time Period")
        date_filter_option = st.radio(
            "Select date range:",
            ["All Dates", "Next 30 Days", "Next 90 Days", "Custom Range"]
        )
        
        if date_filter_option == "Custom Range":
            min_date = chart_data['Start'].min().date()
            max_date = chart_data['Finish'].max().date()
            
            date_range = st.date_input(
                "Select date range:",
                value=(min_date, min_date + timedelta(days=30)),
                min_value=min_date,
                max_value=max_date
            )
            
            if len(date_range) == 2:
                start_date, end_date = date_range
                chart_data = chart_data[
                    (chart_data['Start'].dt.date <= end_date) & 
                    (chart_data['Finish'].dt.date >= start_date)
                ]
        elif date_filter_option == "Next 30 Days":
            today = datetime.now().date()
            chart_data = chart_data[
                (chart_data['Start'].dt.date <= today + timedelta(days=30)) & 
                (chart_data['Finish'].dt.date >= today)
            ]
        elif date_filter_option == "Next 90 Days":
            today = datetime.now().date()
            chart_data = chart_data[
                (chart_data['Start'].dt.date <= today + timedelta(days=90)) & 
                (chart_data['Finish'].dt.date >= today)
            ]
        
        # Filter by category
        st.write("### Categories")
        all_categories = sorted(chart_data['Category'].unique())
        selected_categories = st.multiselect(
            "Filter by Category",
            options=all_categories,
            default=all_categories
        )
        
        # Filter by zone
        st.write("### Trustee Zones")
        available_zones = sorted([str(zone) for zone in chart_data['Trustee_Zone'].unique()])
        selected_zones = st.multiselect(
            "Filter by Trustee Zone",
            options=available_zones,
            default=available_zones
        )
        
        # Filter by school name using search
        st.write("### Schools")
        all_schools = sorted(chart_data['School'].unique())
        school_search = st.text_input("Search for specific school:")
        
        if school_search:
            matching_schools = [school for school in all_schools if school_search.lower() in school.lower()]
            selected_schools = st.multiselect(
                "Select schools:",
                options=all_schools,
                default=matching_schools
            )
        else:
            # Limit the default selection to a manageable number of schools
            default_schools = all_schools[:5] if len(all_schools) > 5 else all_schools
            selected_schools = st.multiselect(
                "Select schools:",
                options=all_schools,
                default=default_schools
            )
        
        # Filter by completion status
        st.write("### Status")
        completion_options = {
            "All Tasks": None,
            "Incomplete Tasks": 99,
            "Completed Tasks": 100
        }
        
        selected_completion = st.radio(
            "Filter by completion status:",
            options=list(completion_options.keys())
        )
    
    # Apply all filters
    if selected_categories:
        chart_data = chart_data[chart_data['Category'].isin(selected_categories)]
        
    if selected_zones:
        chart_data = chart_data[chart_data['Trustee_Zone'].isin(selected_zones)]
    
    if selected_schools:
        chart_data = chart_data[chart_data['School'].isin(selected_schools)]
    
    if selected_completion != "All Tasks":
        threshold = completion_options[selected_completion]
        if threshold == 100:
            chart_data = chart_data[chart_data['Completion_pct'] == 100]
        else:
            chart_data = chart_data[chart_data['Completion_pct'] < 100]
    
    # Display number of tasks after filtering
    st.write(f"Displaying {len(chart_data)} tasks")
    
    # If too many tasks, provide warning
    if len(chart_data) > 50:
        st.warning(f"Displaying {len(chart_data)} tasks might make the chart hard to read. Consider using more filters to narrow down the view.")
    
    # Prepare data for Gantt chart
    fig = ff.create_gantt(
        chart_data,
        colors={
            'Planning': 'rgb(46, 137, 205)',
            'Delivery': 'rgb(114, 44, 121)',
            'Installation': 'rgb(198, 47, 105)',
            'Issue Resolution': 'rgb(58, 149, 136)',
            'Revisit': 'rgb(214, 39, 40)',
            'Closeout': 'rgb(31, 119, 180)'
        },
        index_col='Category',
        show_colorbar=True,
        group_tasks=True,
        showgrid_x=True,
        showgrid_y=True,
        title='UPS Installation Project Schedule'
    )
    
    # Update layout for better display
    fig.update_layout(
        autosize=True,
        height=800,  # Increased height for better readability
        margin=dict(l=50, r=50, b=100, t=100, pad=4),
        xaxis_title="Timeline",
        yaxis_title="Tasks"
    )
    
    # Hover template to show more info
    for i in range(len(fig.data)):
        if i < len(chart_data):
            fig.data[i].customdata = [
                f"Task: {row['Task']}<br>" +
                f"Resource: {row['Resource']}<br>" +
                f"Date: {row['Start'].strftime('%Y-%m-%d')} to {row['Finish'].strftime('%Y-%m-%d')}<br>" +
                f"Completion: {row['Completion_pct']}%<br>" +
                f"Zone: {row['Trustee_Zone']}<br>" +
                (f"Notes: {row['Notes']}" if pd.notna(row['Notes']) and row['Notes'] != '' else "")
                for _, row in chart_data.iterrows()
            ]
            fig.data[i].hovertemplate = "%{customdata}<extra></extra>"
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display filtered data in a table view
    with st.expander("View Filtered Task Details"):
        st.dataframe(
            chart_data[['Task', 'Category', 'Start', 'Finish', 'Completion_pct', 'Trustee_Zone', 'Resource', 'Notes']],
            use_container_width=True,
            hide_index=True
        )

# Function to show summary
def show_summary():
    df = st.session_state.tasks_data
    
    st.subheader("Project Summary")
    
    # Overall progress
    total_tasks = len(df)
    completed_tasks = len(df[df['Completion_pct'] == 100])
    in_progress_tasks = len(df[(df['Completion_pct'] > 0) & (df['Completion_pct'] < 100)])
    not_started_tasks = len(df[df['Completion_pct'] == 0])
    
    percentage = round((completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0, 1)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tasks", f"{total_tasks}")
    with col2:
        st.metric("Completed", f"{completed_tasks}", f"{percentage}%")
    with col3:
        st.metric("In Progress", f"{in_progress_tasks}", f"{round(in_progress_tasks/total_tasks*100, 1)}%")
    with col4:
        st.metric("Not Started", f"{not_started_tasks}", f"{round(not_started_tasks/total_tasks*100, 1)}%")
    
    # Categories and zones analysis
    st.subheader("Task Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("#### By Category")
        categories = df['Category'].value_counts().reset_index()
        categories.columns = ['Category', 'Count']
        
        # Create a pie chart for categories
        fig = px.pie(
            categories, 
            values='Count', 
            names='Category',
            color='Category',
            color_discrete_map={
                'Planning': 'rgb(46, 137, 205)',
                'Delivery': 'rgb(114, 44, 121)',
                'Installation': 'rgb(198, 47, 105)',
                'Issue Resolution': 'rgb(58, 149, 136)',
                'Revisit': 'rgb(214, 39, 40)',
                'Closeout': 'rgb(31, 119, 180)'
            },
            title="Tasks by Category"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.write("#### By Trustee Zone")
        # Convert to string to handle mixed types
        df['Trustee_Zone'] = df['Trustee_Zone'].astype(str)
        zones = df[df['Trustee_Zone'] != '0']['Trustee_Zone'].value_counts().reset_index()
        zones.columns = ['Zone', 'Count']
        
        if not zones.empty:
            # Create a bar chart for zones
            fig = px.bar(
                zones, 
                x='Zone', 
                y='Count', 
                title="Tasks by Trustee Zone",
                color_discrete_sequence=['rgb(58, 149, 136)']
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No zone data available")
    
    # Timeline analysis
    st.subheader("Project Timeline")
    if not df.empty and 'Start' in df and 'Finish' in df:
        earliest_date = df['Start'].min()
        latest_date = df['Finish'].max()
        
        project_duration = (latest_date - earliest_date).days
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Project Start", earliest_date.strftime('%Y-%m-%d'))
        with col2:
            st.metric("Project End", latest_date.strftime('%Y-%m-%d'))
        with col3:
            st.metric("Duration", f"{project_duration} days")
            
        # Monthly progress chart
        st.subheader("Monthly Task Distribution")
        
        # Create a month column for grouping
        df['Month'] = df['Start'].dt.strftime('%Y-%m')
        
        # Count tasks by month and category
        monthly_tasks = df.groupby(['Month', 'Category']).size().reset_index(name='Count')
        
        # Create a grouped bar chart
        fig = px.bar(
            monthly_tasks,
            x='Month',
            y='Count',
            color='Category',
            color_discrete_map={
                'Planning': 'rgb(46, 137, 205)',
                'Delivery': 'rgb(114, 44, 121)',
                'Installation': 'rgb(198, 47, 105)',
                'Issue Resolution': 'rgb(58, 149, 136)',
                'Revisit': 'rgb(214, 39, 40)',
                'Closeout': 'rgb(31, 119, 180)'
            },
            title="Tasks by Month and Category"
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Main app layout
st.sidebar.header("UPS Installation Project")
st.sidebar.markdown("Project management tool for tracking UPS installations across school board sites.")

view_option = st.sidebar.radio(
    "Select View",
    options=["Gantt Chart", "Data Editor", "Project Summary"]
)

# Show relevant sections based on selected view
if view_option == "Gantt Chart":
    create_gantt_chart()
    
elif view_option == "Data Editor":
    display_and_edit_data()
    
elif view_option == "Project Summary":
    show_summary()

# Footer
st.sidebar.markdown("---")
st.sidebar.info(
    """
    **Instructions:**
    - Use 'Data Editor' to add/edit tasks
    - Use 'Gantt Chart' to visualize with filtering options
    - View 'Project Summary' for analytics
    - Download CSV for backup or sharing
    """
)