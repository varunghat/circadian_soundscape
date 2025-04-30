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

    return average_results, max_results, median_results, time_columns


def process_files(files, output_dir, freq_bins, offset=0):

    # Calculate bin labels using the bins TODO: Would this work if bins are not sorted/ overlap/ have missing bins?
    bin_labels = [
        str(freq_bins[i]) + "-" + str(freq_bins[i + 1])
        for i in range(len(freq_bins) - 1)
    ]

    # Initialize dictionaries to store results
    average_results = {label: [] for label in bin_labels}
    max_results = {label: [] for label in bin_labels}
    median_results = {label: [] for label in bin_labels}
    time_columns = []

    for file_path in files:

        average_results, max_results, median_results, time_columns = process_file(
            file_path,
            bin_labels,
            freq_bins,
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

    # Add the time offset to the time columns and mod 24 to wrap around
    average_df.index = (average_df.index + offset) % 24
    max_df.index = (max_df.index + offset) % 24
    median_df.index = (median_df.index + offset) % 24

    # Sort the DataFrames by index
    average_df = average_df.sort_index()
    max_df = max_df.sort_index()
    median_df = median_df.sort_index()

    average_df.to_csv(os.path.join(output_dir, "average_results.csv"))
    max_df.to_csv(os.path.join(output_dir, "max_results.csv"))
    median_df.to_csv(os.path.join(output_dir, "median_results.csv"))

    # Return the paths of the saved files
    return (
        os.path.join(output_dir, "average_results.csv"),
        os.path.join(output_dir, "max_results.csv"),
        os.path.join(output_dir, "median_results.csv"),
    )


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
