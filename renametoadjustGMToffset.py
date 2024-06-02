# -*- coding: utf-8 -*-
"""
Created on Fri May 31 21:04:10 2024

@author: lhauser
"""

import os
import datetime
import shutil

# Source and destination directories
source_dir = "./power-to-noise-output"
destination_dir = "./pmn_timeadjusted"

# Ensure the destination directory exists
os.makedirs(destination_dir, exist_ok=True)

# Get the list of all files in the source directory
files = os.listdir(source_dir)
csv_files = [f for f in files if f.endswith(".csv")]


# Function to adjust the timestamp
def adjust_timestamp(filename, offset_hours):
    try:
        # Extract date and time from the filename
        date_str, time_str = filename.split("_")
        time_str = time_str.split(".")[0]

        # Create a datetime object
        dt = datetime.datetime.strptime(date_str + time_str, "%Y%m%d%H%M%S")

        # Subtract the offset hours
        corrected_dt = dt + datetime.timedelta(hours=offset_hours)

        # Format the corrected datetime back to the string
        corrected_date_str = corrected_dt.strftime("%Y%m%d_%H%M%S")

        # Return the new filename
        return corrected_date_str + ".csv"
    except ValueError:
        # Skip files that do not match the expected format
        return None


# Offset in hours (GMT-4)
offset_hours = -4

# Rename files and move them to the destination directory
for filename in csv_files:
    new_filename = adjust_timestamp(filename, offset_hours)
    if new_filename:
        old_path = os.path.join(source_dir, filename)
        new_path = os.path.join(destination_dir, new_filename)
        shutil.copy(old_path, new_path)
        print(f"Copied and renamed: {filename} -> {new_filename}")
    else:
        print(f"Skipped: {filename} (invalid format)")

print("Processing complete.")
