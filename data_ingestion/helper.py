
import pytz
from datetime import datetime
import os

def get_all_file_names(directory):
    file_names = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_names.append(file)
    return file_names

def preprocess_date(date_str, timezone="Asia/Kolkata"):
    local = pytz.timezone(timezone)
    naive = datetime.strptime(date_str, "%d-%m-%Y %H:%M:%S")
    local_dt = local.localize(naive, is_dst=None)  # Localize to the given timezone
    return local_dt
