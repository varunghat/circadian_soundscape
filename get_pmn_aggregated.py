# Load libraries
import os
import numpy as np
import pandas as pd

# Set directory
drive = "./pmn_timeadjusted/"  # Directory where the CSV files are stored
# Set the day
chosen_day = "20240409"  # The day for which the CSV files are to be read

year = "2024"
month = "04"

# Set the start and end day
start_day = "08"
end_day = "11"

# Get the list of all CSV files in the specified directory
all_files = os.listdir(drive)
files = [f for f in all_files if f.endswith(".csv")]


files = [f for f in all_files if f.startswith(chosen_day)]


chosen_days = [
    year + month + "{:02d}".format(i) for i in range(int(start_day), int(end_day) + 1)
]
print(chosen_days)
file_dict = {k: [] for k in chosen_days}
for day in chosen_days:
    file_list = [f for f in all_files if f.startswith(day)]
    file_dict[day] = file_list
    # print(day,"->entire day data available: ",len(file_list) == (24*60)/5)


def process_file(
    file_path,
    bin_labels,
    bins,
    average_results,
    max_results,
    median_results,
    time_columns,
):

    df = pd.read_csv(file_path)

    # print(df)

    # Multiply the 'Frequency' column by 750
    df["Frequency"] = df["Frequency"] * 750

    # Extract the time from the filename and convert it to a time digit
    filename = os.path.basename(file_path)
    time_str = filename.split("_")[1][:4]
    time_digit = int(time_str)

    # Add the time digit to the time columns list
    time_columns.append(time_digit)

    # Bin the 'Frequency' values
    df["Frequency Bin"] = pd.cut(df["Frequency"], bins, labels=bin_labels)

    # Group by 'Frequency Bin' and aggregate 'PMN' values
    avg_agg = df.groupby("Frequency Bin")["PMN"].mean()
    max_agg = df.groupby("Frequency Bin")["PMN"].max()
    median_agg = df.groupby("Frequency Bin")["PMN"].median()

    # Store the results
    for label in bin_labels:
        average_results[label].append(avg_agg.get(label, np.nan))
        max_results[label].append(max_agg.get(label, np.nan))
        median_results[label].append(median_agg.get(label, np.nan))

    return average_results, max_results, median_results, time_columns


# Define frequency bins
bins = [0, 1500, 5000, 10000, 20000, 60000]
bin_labels = ["0-1500", "1500-5000", "5000-10000", "10k-20000", "20k-60000"]
colors = ["blue", "green", "orange", "red", "purple"]


def process_files(files):

    # Initialize dictionaries to store results
    average_results = {label: [] for label in bin_labels}
    max_results = {label: [] for label in bin_labels}
    median_results = {label: [] for label in bin_labels}
    time_columns = []

    for filename in files:
        file_path = os.path.join(drive, filename)
        average_results, max_results, median_results, time_columns = process_file(
            file_path,
            bin_labels,
            bins,
            average_results,
            max_results,
            median_results,
            time_columns,
        )

        # Create DataFrames from the results
        average_df = pd.DataFrame(average_results, index=time_columns).sort_index()
        max_df = pd.DataFrame(max_results, index=time_columns).sort_index()
        median_df = pd.DataFrame(median_results, index=time_columns).sort_index()

        average_df.index = average_df.index / 100.0
        max_df.index = max_df.index / 100.0
        median_df.index = median_df.index / 100.0

        average_df.to_csv(os.path.join(drive, "average_results.csv"))
        max_df.to_csv(os.path.join(drive, "max_results.csv"))
        median_df.to_csv(os.path.join(drive, "median_results.csv"))


process_files(files)
