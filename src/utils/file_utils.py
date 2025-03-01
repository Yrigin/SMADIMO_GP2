from datetime import datetime

def generate_csv_filename(project_name):
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"data/{project_name}_{date_str}.csv"
    return filename