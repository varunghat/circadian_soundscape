import os
import pandas as pd
import numpy as np

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

# Function to interpolate and smooth the data using a moving average
def smooth_data(df, window_size=6):
    return (
        df.interpolate(method="linear")
        .rolling(window=window_size, min_periods=1)
        .mean()
    )

# Function to extract unique hour labels
def extract_hour_labels(labels):
    return [str(label)[:2] for label in labels]

