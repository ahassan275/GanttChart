import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
from datetime import datetime, timedelta
import numpy as np
import io
import base64

st.set_page_config(layout="wide", page_title="UPS Installation Project Gantt Chart")

st.title("UPS Installation Project Gantt Chart")

# Initialize session state for storing tasks data
if 'tasks_data' not in st.session_state:
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
            st.success(f"Task '{task_to_delete}' deleted successfully!")
    
    with tab4:
        # File upload/download
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Upload Data")
            uploaded_file = st.file_uploader("Upload CSV", type="csv")
            
            if uploaded_file is not None:
                try:
                    df = pd.read_csv(uploaded_file)
                    
                    # Convert date strings to datetime
                    df['Start'] = pd.to_datetime(df['Start'])
                    df['Finish'] = pd.to_datetime(df['Finish'])
                    
                    st.session_state.tasks_data = df
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

# Function to create Gantt chart
def create_gantt_chart():
    df = st.session_state.tasks_data
    
    # Create a copy of the dataframe for visualization
    chart_data = df.copy()
    
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
        height=600,
        margin=dict(l=50, r=50, b=100, t=100, pad=4),
        xaxis_title="Timeline",
        yaxis_title="Tasks"
    )
    
    # Hover template to show more info
    for i in range(len(fig.data)):
        fig.data[i].customdata = [
            f"Resource: {row['Resource']}<br>" +
            f"Completion: {row['Completion_pct']}%<br>" +
            f"Zone: {row['Trustee_Zone']}<br>" +
            f"Notes: {row['Notes']}"
            for _, row in chart_data.iterrows()
        ]
        fig.data[i].hovertemplate = "%{customdata}<extra></extra>"
    
    st.plotly_chart(fig, use_container_width=True)

# Function to show summary
def show_summary():
    df = st.session_state.tasks_data
    
    st.subheader("Project Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_tasks = len(df)
        completed_tasks = len(df[df['Completion_pct'] == 100])
        percentage = round((completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0, 1)
        
        st.metric("Task Completion", f"{completed_tasks}/{total_tasks}", f"{percentage}%")
    
    with col2:
        categories = df['Category'].value_counts().reset_index()
        categories.columns = ['Category', 'Count']
        
        st.bar_chart(categories.set_index('Category'))
    
    with col3:
        zones = df[df['Trustee_Zone'] > 0]['Trustee_Zone'].value_counts().reset_index()
        zones.columns = ['Zone', 'Count']
        
        st.bar_chart(zones.set_index('Zone'))

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
    
    with st.expander("View Task Details"):
        st.dataframe(
            st.session_state.tasks_data,
            use_container_width=True,
            hide_index=True
        )
    
elif view_option == "Data Editor":
    display_and_edit_data()
    
elif view_option == "Project Summary":
    show_summary()
    create_gantt_chart()

# Footer
st.sidebar.markdown("---")
st.sidebar.info(
    """
    **Instructions:**
    - Use 'Data Editor' to add/edit tasks
    - Tasks can be grouped by Category and Zone
    - Download CSV for backup
    - Upload CSV to restore data
    """
)