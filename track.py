import requests
import csv
import os
import subprocess
from tkinter import *
from tkinter import ttk
from tkcalendar import Calendar
from datetime import datetime, timedelta
import json
import base64
import math
from ttkthemes import ThemedTk

def round_to_nearest_quarter_hour(seconds):
    minutes = seconds / 60
    return round(minutes / 15) * 15 * 60

def get_user_info(api_token):
    auth = base64.b64encode(f"{api_token}:api_token".encode()).decode()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {auth}"
    }

    response = requests.get('https://api.track.toggl.com/api/v8/me', headers=headers)
    data = json.loads(response.text)

    return data['data']['id'], data['data']['fullname']

def get_hours_and_entries(api_token, start_date, end_date, user_id):
    auth = base64.b64encode(f"{api_token}:api_token".encode()).decode()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {auth}"
    }

    url = f"https://api.track.toggl.com/reports/api/v2/details?workspace_id=6347046&since={start_date}&until={end_date}&user_agent=api_test&user_ids={user_id}"

    response = requests.get(url, headers=headers)
    data = json.loads(response.text)

    total_seconds = sum([round_to_nearest_quarter_hour(entry["dur"] / 1000) for entry in data["data"]])
    total_hours = total_seconds / 3600

    return total_hours, data["data"]

def submit():
    global hours, entries, user_id, user_name
    api_token = api_entry.get()
    start_date = start_cal.selection_get().isoformat()
    end_date = end_cal.selection_get().isoformat()

    if user_id is None or user_name is None:
        user_id, user_name = get_user_info(api_token)
    hours, entries = get_hours_and_entries(api_token, start_date, end_date, user_id)
    result_label.config(text=f"Total hours worked: {hours}")

def export_to_csv():
    filename = f'[{user_name}] Timesheet.csv'
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Start Time", "End Time", "Hours Worked"])

        for entry in entries:
            date = entry["start"].split('T')[0]
            start_time = entry["start"].split('T')[1]
            end_time = entry["end"].split('T')[1]
            duration = round_to_nearest_quarter_hour(entry["dur"] / 1000) / 3600
            writer.writerow([date, start_time, end_time, duration])

        writer.writerow(["Total", "", "", hours])

    if os.name == 'nt':  # For Windows
        os.startfile(filename)
    else:  # For macOS and Linux
        subprocess.call(['open', filename])

root = ThemedTk(theme="arc")  # Use the "arc" theme

api_label = ttk.Label(root, text="API Token")
api_label.pack()
api_entry = ttk.Entry(root)
api_entry.pack()

start_label = ttk.Label(root, text="Start Date")
start_label.pack()
start_cal = Calendar(root)
start_cal.pack()

end_label = ttk.Label(root, text="End Date")
end_label.pack()
end_cal = Calendar(root)
end_cal.pack()

submit_button = ttk.Button(root, text="Submit", command=submit)
submit_button.pack()

export_button = ttk.Button(root, text="Export to CSV", command=export_to_csv)
export_button.pack()

result_label = ttk.Label(root, text="")
result_label.pack()

user_id = None
user_name = None

root.mainloop()