# data_converter.py
import pandas as pd
from datetime import datetime, timedelta
import os

def convert_ups_data(excel_file_path, output_csv_path=None):
    """
    Convert UPS project Excel spreadsheet data into format for Gantt chart application.
    
    Parameters:
    excel_file_path (str): Path to the UPS Project Excel file
    output_csv_path (str, optional): Path where to save the output CSV. If None, uses 'gantt_data.csv'
    
    Returns:
    pandas.DataFrame: The converted data ready for Gantt chart import
    """
    
    if output_csv_path is None:
        output_csv_path = 'gantt_data.csv'
        
    print(f"Reading Excel file: {excel_file_path}")
    
    # Read the main project status sheet
    project_df = pd.read_excel(excel_file_path, sheet_name='Project status')
    
    # Read the issues sheet
    try:
        issues_df = pd.read_excel(excel_file_path, sheet_name='school with issues')
        has_issues_sheet = True
        print(f"Found issues sheet with {len(issues_df)} records")
    except:
        has_issues_sheet = False
        print("No issues sheet found")
        issues_df = pd.DataFrame()
    
    # Read the revisits sheet
    try:
        revisits_df = pd.read_excel(excel_file_path, sheet_name='Schools to be revisted')
        has_revisits_sheet = True
        print(f"Found revisits sheet with {len(revisits_df)} records")
    except:
        has_revisits_sheet = False
        print("No revisits sheet found")
        revisits_df = pd.DataFrame()
    
    # Initialize output dataframe
    gantt_data = []
    
    # Set current date for planning new tasks
    today = datetime.now().date()
    
    # Helper function to map status to completion percentage
    def map_status_to_completion(status):
        if not isinstance(status, str):
            return 0
        status = status.lower().strip()
        if status == 'done':
            return 100
        elif status == 'started':
            return 50
        else:
            return 0
    
    # Helper function to get resource by category
    def get_resource(category):
        resources = {
            'Planning': 'Project Manager',
            'Delivery': 'Delivery Team',
            'Installation': 'Installation Team',
            'Issue Resolution': 'Specialized Team',
            'Revisit': 'Maintenance Team',
            'Closeout': 'Project Manager'
        }
        return resources.get(category, 'Unassigned')
    
    # Add planning phase tasks
    planning_tasks = [
        {'Task': 'Planning & Preparation', 'Duration': 2, 'Completion_pct': 100},
        {'Task': 'Data Closet Assessment', 'Duration': 3, 'Completion_pct': 80},
        {'Task': 'Team Assignments', 'Duration': 1, 'Completion_pct': 100}
    ]
    
    start_date = today - timedelta(days=5)  # Planning started a few days ago
    
    for i, task in enumerate(planning_tasks):
        task_start = start_date + timedelta(days=i)
        task_finish = task_start + timedelta(days=task['Duration'])
        
        gantt_data.append({
            'Task': task['Task'],
            'Resource': get_resource('Planning'),
            'Start': task_start,
            'Duration': task['Duration'],
            'Finish': task_finish,
            'Completion_pct': task['Completion_pct'],
            'Trustee_Zone': 0,  # 0 for non-school tasks
            'Category': 'Planning',
            'Notes': ''
        })
    
    last_planning_date = gantt_data[-1]['Finish']
    next_task_date = last_planning_date
    
    # Process main project status sheet
    for idx, row in project_df.iterrows():
        # Skip header or empty rows
        if not isinstance(row.get('Sites'), str) or row['Sites'].upper() == 'ELEMENTARY SCHOOLS' or row['Sites'].upper() == 'SECONDARY SCHOOLS':
            continue
        
        school_name = row['Sites'].strip()
        if pd.isna(school_name) or not school_name:
            continue
            
        # Get status and convert to completion percentage
        status = row.get('UPS Replacement Status', 'Not Started')
        completion = map_status_to_completion(status)
        
        # Get zone information
        zone = row.get('Trustee Zones', 0)
        if pd.isna(zone):
            zone = 0
        
        # Get notes
        notes = row.get('Notes', '')
        if pd.isna(notes):
            notes = ''
        
        # Try to get deployment date, if available
        has_deployment_date = False
        deployment_date = row.get('Deployment Date')
        if deployment_date is not None and not pd.isna(deployment_date):
            if isinstance(deployment_date, datetime) or isinstance(deployment_date, pd.Timestamp):
                delivery_date = deployment_date.date() - timedelta(days=1)
                installation_date = deployment_date.date()
                has_deployment_date = True
        
        # If no deployment date, use next available date
        if not has_deployment_date:
            # For remaining schools, schedule from the next day
            if completion == 0:  # Not started
                delivery_date = next_task_date + timedelta(days=1)
                installation_date = delivery_date + timedelta(days=1)
                next_task_date = installation_date
            else:
                # For completed or started schools, use a past date
                # Skip these if you only want to include remaining work
                continue
        
        # Add delivery task
        gantt_data.append({
            'Task': f"{school_name}: Delivery",
            'Resource': get_resource('Delivery'),
            'Start': delivery_date,
            'Duration': 1,
            'Finish': delivery_date + timedelta(days=1),
            'Completion_pct': completion,
            'Trustee_Zone': zone,
            'Category': 'Delivery',
            'Notes': notes
        })
        
        # Add installation task
        gantt_data.append({
            'Task': f"{school_name}: Installation",
            'Resource': get_resource('Installation'),
            'Start': installation_date,
            'Duration': 1,
            'Finish': installation_date + timedelta(days=1),
            'Completion_pct': completion,
            'Trustee_Zone': zone,
            'Category': 'Installation',
            'Notes': notes
        })
    
    # Process schools with issues
    if has_issues_sheet:
        for idx, row in issues_df.iterrows():
            # Get school name from appropriate column
            school_col = 'School ' if 'School ' in issues_df.columns else 'School'
            if school_col not in row or pd.isna(row[school_col]):
                continue
                
            school_name = row[school_col].strip()
            
            # Get issue details
            issue = row.get('Issues', '')
            if pd.isna(issue):
                issue = ''
            
            # Get status if available
            issue_status = row.get('Status', '')
            if pd.isna(issue_status) or not isinstance(issue_status, str):
                completion = 0
            elif issue_status.lower() == 'done' or issue_status.lower() == 'resolved':
                completion = 100
            elif issue_status.lower() == 'pending':
                completion = 30
            else:
                completion = 50
            
            # Find zone from main project data
            zone = 0
            for project_row in project_df.iterrows():
                if project_row[1].get('Sites') == school_name:
                    z = project_row[1].get('Trustee Zones', 0)
                    if not pd.isna(z):
                        zone = z
                    break
            
            # Schedule for issue resolution
            issue_start_date = next_task_date + timedelta(days=1)
            issue_duration = 2  # Issues typically take 2 days
            
            gantt_data.append({
                'Task': f"{school_name}: Issue Resolution",
                'Resource': get_resource('Issue Resolution'),
                'Start': issue_start_date,
                'Duration': issue_duration,
                'Finish': issue_start_date + timedelta(days=issue_duration),
                'Completion_pct': completion,
                'Trustee_Zone': zone,
                'Category': 'Issue Resolution',
                'Notes': issue
            })
            
            next_task_date = issue_start_date + timedelta(days=issue_duration)
    
    # Process schools needing revisits
    if has_revisits_sheet:
        for idx, row in revisits_df.iterrows():
            if 'School' not in row or pd.isna(row['School']):
                continue
                
            school_name = row['School'].strip()
            
            # Get issue details
            issue = row.get('Issues', '')
            if pd.isna(issue):
                issue = ''
            
            # Get status if available
            revisit_status = row.get('Status', '')
            if pd.isna(revisit_status) or not isinstance(revisit_status, str):
                completion = 0
            elif revisit_status.lower() == 'done' or revisit_status.lower() == 'completed':
                completion = 100
            elif revisit_status.lower() == 'pending':
                completion = 0
            else:
                completion = 50
            
            # Get assigned team member if available
            resource = row.get('Team member assigned', '')
            if pd.isna(resource) or not resource:
                resource = get_resource('Revisit')
            
            # Find zone from main project data
            zone = 0
            for project_row in project_df.iterrows():
                if project_row[1].get('Sites') == school_name:
                    z = project_row[1].get('Trustee Zones', 0)
                    if not pd.isna(z):
                        zone = z
                    break
            
            # Schedule for revisit
            revisit_start_date = next_task_date + timedelta(days=1)
            revisit_duration = 1  # Revisits typically take 1 day
            
            gantt_data.append({
                'Task': f"{school_name}: Revisit",
                'Resource': resource,
                'Start': revisit_start_date,
                'Duration': revisit_duration,
                'Finish': revisit_start_date + timedelta(days=revisit_duration),
                'Completion_pct': completion,
                'Trustee_Zone': zone,
                'Category': 'Revisit',
                'Notes': issue
            })
            
            next_task_date = revisit_start_date + timedelta(days=revisit_duration)
    
    # Add project closeout tasks
    closeout_start = next_task_date + timedelta(days=3)
    
    gantt_data.append({
        'Task': 'Final Documentation',
        'Resource': get_resource('Closeout'),
        'Start': closeout_start,
        'Duration': 3,
        'Finish': closeout_start + timedelta(days=3),
        'Completion_pct': 0,
        'Trustee_Zone': 0,
        'Category': 'Closeout',
        'Notes': ''
    })
    
    gantt_data.append({
        'Task': 'Project Review',
        'Resource': get_resource('Closeout'),
        'Start': closeout_start + timedelta(days=4),
        'Duration': 1,
        'Finish': closeout_start + timedelta(days=5),
        'Completion_pct': 0,
        'Trustee_Zone': 0,
        'Category': 'Closeout',
        'Notes': ''
    })
    
    # Convert to DataFrame
    result_df = pd.DataFrame(gantt_data)
    
    # Save to CSV
    result_df.to_csv(output_csv_path, index=False)
    print(f"Conversion complete. {len(result_df)} tasks generated.")
    print(f"Output saved to: {output_csv_path}")
    
    return result_df

# Example usage
if __name__ == "__main__":
    # Check if file exists in current directory
    excel_file = "UPS Project Tracking sheet.xlsx"
    if not os.path.exists(excel_file):
        excel_file = input("Enter the path to your Excel file: ")
    
    output_file = "gantt_data.csv"
    
    try:
        df = convert_ups_data(excel_file, output_file)
        print(f"Generated {len(df)} tasks from the UPS project data")
        print(f"Task categories: {df['Category'].value_counts().to_dict()}")
    except Exception as e:
        print(f"Error converting data: {e}")