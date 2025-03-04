
import pandas as pd
from datetime import datetime, timedelta
import io
import csv

def csv_to_dataframe(csv_string):
    """
    Convert a CSV string to a pandas DataFrame with proper date parsing.
    """
    try:
        # Read CSV from string
        df = pd.read_csv(io.StringIO(csv_string))
        
        # Convert date strings to datetime objects
        if 'Start' in df.columns:
            df['Start'] = pd.to_datetime(df['Start'])
        
        if 'Finish' in df.columns:
            df['Finish'] = pd.to_datetime(df['Finish'])
            
        return df, None
    except Exception as e:
        return None, str(e)

def dataframe_to_csv(df):
    """
    Convert a pandas DataFrame to a CSV string.
    """
    try:
        return df.to_csv(index=False), None
    except Exception as e:
        return None, str(e)

def create_sample_data():
    """
    Create a sample dataset for the Gantt chart.
    """
    now = datetime.now()
    
    sample_data = {
        'Task': [
            'Project Planning',
            'Requirements Gathering',
            'System Design',
            'Implementation Phase 1',
            'Implementation Phase 2',
            'Testing',
            'Deployment',
            'Documentation'
        ],
        'Resource': [
            'Project Manager',
            'Analyst Team',
            'Design Team',
            'Development Team',
            'Development Team',
            'QA Team',
            'Operations Team',
            'Technical Writer'
        ],
        'Start': [
            now,
            now + timedelta(days=2),
            now + timedelta(days=5),
            now + timedelta(days=10),
            now + timedelta(days=15),
            now + timedelta(days=20),
            now + timedelta(days=25),
            now + timedelta(days=22)
        ],
        'Duration': [3, 4, 6, 6, 6, 5, 3, 5],
        'Finish': [
            now + timedelta(days=3),
            now + timedelta(days=6),
            now + timedelta(days=11),
            now + timedelta(days=16),
            now + timedelta(days=21),
            now + timedelta(days=25),
            now + timedelta(days=28),
            now + timedelta(days=27)
        ],
        'Completion_pct': [100, 80, 60, 40, 20, 10, 0, 0],
        'Trustee_Zone': [0, 0, 0, 1, 2, 0, 0, 0],
        'Category': [
            'Planning', 'Planning', 'Planning', 
            'Development', 'Development', 
            'Testing', 'Deployment', 'Documentation'
        ],
        'Notes': [
            '', '', '', '', '', '', '', ''
        ]
    }
    
    return pd.DataFrame(sample_data)

def recalculate_finish_dates(df):
    """
    Recalculate finish dates based on start dates and durations.
    """
    for idx, row in df.iterrows():
        if pd.notna(row['Start']) and pd.notna(row['Duration']):
            df.at[idx, 'Finish'] = row['Start'] + timedelta(days=int(row['Duration']))
    
    return df

def validate_gantt_data(df):
    """
    Validate the necessary columns for Gantt chart data.
    Returns a tuple (is_valid, error_message)
    """
    required_columns = ['Task', 'Start', 'Finish']
    
    # Check required columns
    for col in required_columns:
        if col not in df.columns:
            return False, f"Missing required column: {col}"
    
    # Check date formats
    try:
        if not pd.api.types.is_datetime64_any_dtype(df['Start']):
            df['Start'] = pd.to_datetime(df['Start'])
        
        if not pd.api.types.is_datetime64_any_dtype(df['Finish']):
            df['Finish'] = pd.to_datetime(df['Finish'])
    except Exception as e:
        return False, f"Error converting date columns: {str(e)}"
    
    return True, ""

if __name__ == "__main__":
    # Example usage
    sample_df = create_sample_data()
    print("Sample data created with shape:", sample_df.shape)
    
    # Convert to CSV and back
    csv_data, _ = dataframe_to_csv(sample_df)
    recovered_df, _ = csv_to_dataframe(csv_data)
    
    print("Data conversion successful:", sample_df.shape == recovered_df.shape)
