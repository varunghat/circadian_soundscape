import streamlit as st
import numpy as np
import pandas as pd
import random

from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

import plotly.graph_objects as go

import tkinter as tk
from tkinter import filedialog

from scripts import process
from scripts import plot
from scripts.utils import get_sunrise_sunset
from tqdm import tqdm

import subprocess


####################
# Streamlit config
if "NUM_FREQ_BINS" not in st.session_state:
    st.session_state.NUM_FREQ_BINS = 5

MAX_FREQ_BINS = 5

# List of colors to be used for the plots as default
COLOR_LIST = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]

# List of icons to be used for the plots as default
# car, bug, elephant, bird, bat, human, frog
icon_list = ["🚗", "🦗", "🐘", "🐦", "🦇", "🚶", "🐸"]

st.set_page_config(
    page_title="Circadian Soundscape Visualizer",
    page_icon="images/favicon.ico",
    layout="wide",
    initial_sidebar_state="auto",
)
st.title("Circadian Soundscape Visualizer")
st.write(
    "Versatile browser-based tool for bio-acoustics analysis and circadian soundscape visualization"
)
####################


def select_folder():
    """
    Function to select a folder using a file dialog in tkinter
    Returns the path of the selected folder
    """
    root = tk.Tk()
    root.iconify()
    folder_path = filedialog.askdirectory(master=root)
    root.destroy()
    return folder_path


def select_files():
    """
    Function to select files using a file dialog in tkinter
    Returns the paths of the selected files
    """
    root = tk.Tk()
    root.iconify()
    file_paths = filedialog.askopenfilenames(master=root)
    root.destroy()
    return file_paths


def plot_file(
    file_path,
    sunrise_sunset_data,
    use_plotly=True,
    colors=None,
    icons=None,
    bin_labels=None,
):
    """
    Function to plot the results from the PMN CSV file
    Args:
        file_path (str): Path to the PMN CSV file
        sunrise_sunset_data (dict): Dictionary containing the sunrise, sunset and solar noon times for each date
        use_plotly (bool): Whether to use plotly for plotting or not (will use matplotlib if False)
        colors (list): List of colors to be used for the plots
        icons (list): List of icons to be used for the plots
        bin_labels (list): List of frequency bins to be used for the plots
    Returns:
        fig1 : Line plot of the PMN data
        fig2 : Polar plot of the PMN data
        fig3 : Color plot of the PMN data
        fig4 : Color polar plot of the PMN data
    """

    df = pd.read_csv(file_path, index_col=0)
    df = process.smooth_data(df)

    # TODO: TEMP FIX TO AVOID NAN VALUES IN THE PLOTS
    # Fill NaN values with 0
    df = df.fillna(0)

    # Convert 0 to a small value to avoid log(0) error
    df[df == 0] = 0.00001

    if use_plotly:

        fig1 = plot.plot_results_line_plotly(
            df,
            "Power-Minus-Noise",
            "-",
            save=False,
            colors=colors,
            # icons=icons,
        )
        fig2 = plot.plot_results_polar_plotly(
            df,
            "Power-Minus-Noise",
            "-",
            save=False,
            colors=colors,
            # icons=icons,
        )
        fig3 = plot.plot_results_color_plotly(
            df,
            "Power-Minus-Noise",
            "-",
            save=False,
            colors=colors,
            # icons=icons,
        )
        fig4 = plot.plot_results_color_polar_plotly(
            df,
            "Power-Minus-Noise",
            "-",
            save=False,
            colors=colors,
            # icons=icons,
        )

        # Add the sunrise, sunset and solar noon times to the plots if available only to the circular plots (polar and color polar)
        if sunrise_sunset_data is not None:
            r_max = df.max().max()  # Max value for radius line length

            for date, data in sunrise_sunset_data.items():
                data = data["results"]

                if "sunrise" in data:
                    # Convert the sunrise time to datetime. Sunrise time is in the format of date and time (e.g. 2024-12-21T07:00:00Z)
                    sunrise_time = (
                        pd.to_datetime(data["sunrise"]).hour
                        + pd.to_datetime(data["sunrise"]).minute / 60
                    )
                    sunrise_deg = (sunrise_time / 24) * 360

                    fig2.add_trace(
                        go.Scatterpolar(
                            r=[-r_max, r_max],
                            theta=[sunrise_deg, sunrise_deg],
                            mode="lines",
                            line=dict(color="orange", dash="dash"),
                            showlegend=False,
                        )
                    )
                    fig4.add_trace(
                        go.Scatterpolar(
                            r=[-r_max * 2, r_max * 2],
                            theta=[sunrise_deg, sunrise_deg],
                            mode="lines",
                            line=dict(color="orange", dash="dash"),
                            showlegend=False,
                        )
                    )

                if "sunset" in data:
                    # Convert the sunset time to datetime. Sunset time is in the format of date and time (e.g. 2024-12-21T17:00:00Z)
                    sunset_time = (
                        pd.to_datetime(data["sunset"]).hour
                        + pd.to_datetime(data["sunset"]).minute / 60
                    )
                    sunset_deg = (sunset_time / 24) * 360

                    fig2.add_trace(
                        go.Scatterpolar(
                            r=[-r_max, r_max],
                            theta=[sunset_deg, sunset_deg],
                            mode="lines",
                            line=dict(color="red", dash="dash"),
                            showlegend=False,
                        )
                    )
                    fig4.add_trace(
                        go.Scatterpolar(
                            r=[-r_max * 2, r_max * 2],
                            theta=[sunset_deg, sunset_deg],
                            mode="lines",
                            line=dict(color="red", dash="dash"),
                            showlegend=False,
                        )
                    )

                if "solar_noon" in data:
                    # Convert the solar noon time to datetime. Solar noon time is in the format of date and time (e.g. 2024-12-21T12:00:00Z)
                    solar_noon_time = (
                        pd.to_datetime(data["solar_noon"]).hour
                        + pd.to_datetime(data["solar_noon"]).minute / 60
                    )
                    solar_noon_deg = (solar_noon_time / 24) * 360

                    fig2.add_trace(
                        go.Scatterpolar(
                            r=[-r_max, r_max],
                            theta=[solar_noon_deg, solar_noon_deg],
                            mode="lines",
                            line=dict(color="blue", dash="dash"),
                            showlegend=False,
                        )
                    )
                    fig4.add_trace(
                        go.Scatterpolar(
                            r=[-r_max * 2, r_max * 2],
                            theta=[solar_noon_deg, solar_noon_deg],
                            mode="lines",
                            line=dict(color="blue", dash="dash"),
                            showlegend=False,
                        )
                    )
            # Add legends for the lines in fig2 and fig4
            fig2.add_trace(
                go.Scatterpolar(
                    r=[None],
                    theta=[None],
                    mode="lines",
                    line=dict(color="orange", dash="dash"),
                    name="Sunrise",
                )
            )

            fig2.add_trace(
                go.Scatterpolar(
                    r=[None],
                    theta=[None],
                    mode="lines",
                    line=dict(color="red", dash="dash"),
                    name="Sunset",
                )
            )

            fig2.add_trace(
                go.Scatterpolar(
                    r=[None],
                    theta=[None],
                    mode="lines",
                    line=dict(color="blue", dash="dash"),
                    name="Solar Noon",
                )
            )

            # Same thing for fig4 if you want
            fig4.add_trace(
                go.Scatterpolar(
                    r=[None],
                    theta=[None],
                    mode="lines",
                    line=dict(color="orange", dash="dash"),
                    name="Sunrise",
                )
            )
            fig4.add_trace(
                go.Scatterpolar(
                    r=[None],
                    theta=[None],
                    mode="lines",
                    line=dict(color="red", dash="dash"),
                    name="Sunset",
                )
            )
            fig4.add_trace(
                go.Scatterpolar(
                    r=[None],
                    theta=[None],
                    mode="lines",
                    line=dict(color="blue", dash="dash"),
                    name="Solar Noon",
                )
            )

    else:
        fig1 = plot.plot_results_line(df, "Power-Minus-Noise", "-", save=False)
        fig2 = plot.plot_results_polar(df, "Power-Minus-Noise", "-", save=False)
        fig3 = plot.plot_results_color(df, "Power-Minus-Noise", "-", save=False)
        fig4 = plot.plot_results_color_polar(df, "Power-Minus-Noise", "-", save=False)

        # Add the sunrise, sunset and solar noon times to the plots if available only to the circular plots (polar and color polar)
        if sunrise_sunset_data is not None:
            for date, data in sunrise_sunset_data.items():
                # Convert the time into a variable with 360 degrees
                data = data["results"]
                if "sunrise" in data:
                    # Convert the sunrise time to datetime. Sunrise time is in the format of date and time (e.g. 2024-12-21T07:00:00Z)
                    sunrise_time = (
                        pd.to_datetime(data["sunrise"]).hour
                        + pd.to_datetime(data["sunrise"]).minute / 60
                    )
                    # Convert the time to radians
                    sunrise_time = (sunrise_time / 24) * 2 * np.pi

                    fig2.gca().axvline(x=sunrise_time, color="orange", linestyle="--")
                    fig4.gca().axvline(x=sunrise_time, color="orange", linestyle="--")
                if "sunset" in data:
                    # Convert the sunset time to datetime. Sunset time is in the format of date and time (e.g. 2024-12-21T17:00:00Z)
                    sunset_time = (
                        pd.to_datetime(data["sunset"]).hour
                        + pd.to_datetime(data["sunset"]).minute / 60
                    )
                    # Convert the time to radians
                    sunset_time = (sunset_time / 24) * 2 * np.pi
                    fig2.gca().axvline(x=sunset_time, color="red", linestyle="--")
                    fig4.gca().axvline(x=sunset_time, color="red", linestyle="--")

                if "solar_noon" in data:
                    # Convert the solar noon time to datetime. Solar noon time is in the format of date and time (e.g. 2024-12-21T12:00:00Z)
                    solar_noon_time = (
                        pd.to_datetime(data["solar_noon"]).hour
                        + pd.to_datetime(data["solar_noon"]).minute / 60
                    )
                    # Convert the time to radians
                    solar_noon_time = (solar_noon_time / 24) * 2 * np.pi
                    fig2.gca().axvline(x=solar_noon_time, color="blue", linestyle="--")
                    fig4.gca().axvline(x=solar_noon_time, color="blue", linestyle="--")

            # For fig2
            top = 0.95  # Y position (close to top)
            right = 0.8  # X position (close to right)

            fig2.text(
                right,
                top,
                "Sunrise: ---",
                color="orange",
                ha="right",
                va="top",
                fontsize=10,
            )
            fig2.text(
                right,
                top - 0.03,
                "Sunset: ---",
                color="red",
                ha="right",
                va="top",
                fontsize=10,
            )
            fig2.text(
                right,
                top - 0.06,
                "Solar Noon: ---",
                color="green",
                ha="right",
                va="top",
                fontsize=10,
            )

            # For fig4
            fig4.text(
                right,
                top,
                "Sunrise: ---",
                color="orange",
                ha="right",
                va="top",
                fontsize=10,
            )
            fig4.text(
                right,
                top - 0.03,
                "Sunset: ---",
                color="red",
                ha="right",
                va="top",
                fontsize=10,
            )
            fig4.text(
                right,
                top - 0.06,
                "Solar Noon: ---",
                color="green",
                ha="right",
                va="top",
                fontsize=10,
            )

    return fig1, fig2, fig3, fig4


# Select the folder containing the audio files or select the audio files

st.subheader("File selection")

st.warning(
    "**NOTE:** The file selection window CAN OPEN **MINIMIZED**, please **CHECK THE TASKBAR** for the file dialog window."
)
button_cols = st.columns([2, 1, 2, 5])
with button_cols[0]:
    st.write("Select the folder containing the audio files")
    folder_select_button = st.button("Select folder :file_folder:")

with button_cols[1]:
    st.write("**OR**")


with button_cols[2]:
    st.write("Select the audio files")
    file_select_button = st.button("Select files :musical_note:")


if folder_select_button:

    # Select the folder containing the audio files
    selected_folder_path = select_folder()

    st.session_state.folder_path = selected_folder_path
    st.session_state.selected_files = None

    # DEBUG CODE
    if selected_folder_path:
        st.write(f"Selected folder: {selected_folder_path}")
    # DEBUG CODE END


if file_select_button:

    # Select the audio files
    selected_files = select_files()

    st.session_state.selected_files = selected_files
    st.session_state.folder_path = None

    # DEBUG CODE
    if selected_files:
        # st.write(f"Selected files: {selected_files}")
        st.write(f"Number of files selected: {len(selected_files)}")
    # DEBUG CODE END


st.subheader("Options")
# Options for the user
# Audio file format
audio_format = st.selectbox(
    "Select audio format",
    [
        "Audiomoth: YYYYMMDD_hhmmss.wav",
        "Songmeter: Prefix_YYYYMMDD_hhmmss.wav",
        "TODO: THESE FORMATS NEED TO BE CHECKED",
    ],  # TODO: Check these formats
    index=0,
)

# Check if the user wants to offset the time
offset_time = st.checkbox("Correct for timezone offset")

offset = st.number_input(
    "Timezone offset (hours)",
    min_value=-12.0,
    max_value=12.0,
    value=0.0,
    step=0.5,
    disabled=not offset_time,
)
# Round offset to nearest 0.5
offset = round(offset * 2) / 2
st.write("Offset:", offset)


# TODO: Is timezone selection necessary? (Daylight savings, etc added problems)

# Frequency bins


cols = st.columns([10, 10, 1, 1.5, 2.1, 2], vertical_alignment="bottom")
with cols[4]:
    # st.write('Frequency bins')
    if (
        st.button(
            "add freq bins",
            key="add_button",
            disabled=(st.session_state.NUM_FREQ_BINS == MAX_FREQ_BINS),
        )
        and st.session_state.NUM_FREQ_BINS < MAX_FREQ_BINS
    ):
        st.session_state.NUM_FREQ_BINS += 1

with cols[5]:
    # st.write('Frequency bins')
    if (
        st.button(
            "remove",
            key="remove_button",
            disabled=(st.session_state.NUM_FREQ_BINS == 1),
        )
        and st.session_state.NUM_FREQ_BINS > 1
    ):
        st.session_state.NUM_FREQ_BINS -= 1

default_frequency_bins = [
    (0, 1500),
    (1500, 5000),
    (5000, 10000),
    (10000, 20000),
    (20000, 60000),
]

# Aggregate function selector
agg_function = st.selectbox(
    "Select the aggregation function",
    [
        "Mean",
        "Median",
        "Max",
        # "Min",
        # "Sum",
        # "Standard Deviation",
        # "Variance",
        # "Count",
        # "Percentile",
        # "Custom?"
    ],
)

for i in range(st.session_state.NUM_FREQ_BINS):
    with cols[0]:
        min_value = 0 if i == 0 else st.session_state[f"max_freq_{i-1}"]

        min_freq = st.number_input(
            "Min frequency (Hz)",
            min_value=0,
            value=default_frequency_bins[i][0],
            step=1,
            key=f"min_freq_{i}",
        )
    with cols[1]:
        min_value = st.session_state[f"min_freq_{i}"] + 1

        max_freq = st.number_input(
            "Max frequency (Hz)",
            min_value=min_value,
            value=default_frequency_bins[i][1],
            step=1,
            key=f"max_freq_{i}",
        )
    with cols[2]:
        # Color picker
        color = st.color_picker(
            "Color", key=f"color_{i}", value=COLOR_LIST[i % len(COLOR_LIST)]
        )
    with cols[3]:
        # icon picker
        icon = st.selectbox(
            "Icon", icon_list, key=f"icon_{i}", index=i % len(icon_list)
        )

# Get the values of the frequency bins, colors, and icons
freq_bins = []
colors = []
icons = []
for i in range(st.session_state.NUM_FREQ_BINS):
    freq_bins.append(
        (st.session_state[f"min_freq_{i}"], st.session_state[f"max_freq_{i}"])
    )
    colors.append(st.session_state[f"color_{i}"])
    icons.append(st.session_state[f"icon_{i}"])

# TODO: Do we need to make sure frequency bins are not overlapping?


# Check if the user has selected same colors for different bins
if len(colors) != len(set(colors)):
    st.error("You have selected the same color for different frequency bins.")

# Check if the user has selected same icons for different bins
if len(icons) != len(set(icons)):
    st.error("You have selected the same icon for different frequency bins.")

# extra options
st.subheader("Additional options")

# Check if the user wants sunrise, sunset and solar noon times to be plotted
sunrise_sunset = st.checkbox(
    "Plot sunrise, sunset and solar noon times (if available) :sunrise:"
)

sunrise_sunset_data = None

if sunrise_sunset:
    lat = st.text_input("Latitude", value="0.0", key="lat")
    lng = st.text_input("Longitude", value="0.0", key="lng")

    # Check if the user has entered valid latitude and longitude
    try:
        float(lat)
        float(lng)

        if not (-90 <= float(lat) <= 90):
            st.error("Please enter a valid latitude between -90 and 90.")

        if not (-180 <= float(lng) <= 180):
            st.error("Please enter a valid longitude between -180 and 180.")
    except ValueError:
        st.error("Please enter **valid** latitude and longitude.")

force_reprocess_files = st.checkbox(
    "Force reprocess files (if already processed) :repeat:",
    value=False,
    help="If checked, all files will be reprocessed, even if they have already been processed (PMN calculated).",
)

if force_reprocess_files:
    st.warning(
        "Force reprocess files option is checked. All existing PMN files will be deleted."
    )


# Add a way to upload csv files
csv_upload = st.file_uploader(
    "Upload the aggregated PMN CSV file for a day (AFTER RUNNING AGGREGATE PMN separately, should be fixed later)",
    type=["csv"],
)

use_parallel = st.toggle(
    "Use parallel processing (if available) :computer:",
    value=True,
    help="If checked, the PMN calculation will be done in parallel using multiple cores.",
)

if use_parallel:
    st.warning(
        "Parallel processing option is checked. The PMN calculation will be done in parallel using multiple cores."
    )
    # number of workers
    num_workers = st.number_input(
        "Number of workers (cores) to use for parallel processing",
        min_value=1,
        max_value=8,
        value=4,
        step=1,
    )
    st.write(f"Number of workers: {num_workers}")

use_plotly = st.toggle("Use Plotly (Interactive)?", value=True)
# Button
if st.button("Visualize", key="visualize_button"):
    st.write("Visualizing...")
    selected_files = None
    # Extract the dates from the audio files
    if st.session_state.folder_path:
        # Collect all audio files in the selected folder with specified extensions
        audio_extensions = [".wav", ".mp3", ".flac"]
        all_files = list(Path(st.session_state.folder_path).rglob("*"))
        selected_files = [
            file for file in all_files if file.suffix.lower() in audio_extensions
        ]
    elif st.session_state.selected_files:
        selected_files = st.session_state.selected_files
        selected_files = [Path(file) for file in selected_files]
    else:
        st.error("Please select a folder or files to proceed.")
        st.stop()  # TODO: Instead of stopping, just return to the top of the page

    # Check if the user has selected any files
    if selected_files is not None:

        # Get all the dates from the selected files
        dates = set()

        for file in selected_files:
            if audio_format == "Audiomoth: YYYYMMDD_hhmmss.wav":
                date_str = file.stem.split("_")[0]
            elif audio_format == "Songmeter: Prefix_YYYYMMDD_hhmmss.wav":
                date_str = file.stem.split("_")[1]
            else:
                st.error("Invalid audio format selected.")
                st.stop()
            dates.add(date_str)

        # DEBUG CODE
        st.write(f"Number of dates: {len(dates)}")
        # DEBUG CODE END

        # Fetch sunrise, sunset and solar noon times for each date if the user has selected the option
        # TODO: Add check to see if dates are consecutive and if so, fetch the range of dates using the api
        if sunrise_sunset:
            sunrise_sunset_data = {}
            # Fetching sunrise, sunset loading
            with st.spinner("Fetching sunrise, sunset and solar noon times..."):
                for date in dates:
                    sunrise_sunset_data[date] = get_sunrise_sunset(lat, lng, date)

        # DEBUG CODE
        st.write(f"Sunrise, sunset and solar noon times: {sunrise_sunset_data}")
        # DEBUG CODE END

        # Process the audio files and calculate PMN
        scratch_dir = Path("scratch")
        if not scratch_dir.exists():
            scratch_dir.mkdir(parents=True, exist_ok=True)

        # Create the output directory if it doesn't exist
        pmn_output_dir = Path("scratch/pmn_results")
        if not pmn_output_dir.exists():
            pmn_output_dir.mkdir(parents=True, exist_ok=True)

        aggreated_dir = Path("scratch/aggregated_results")
        if not aggreated_dir.exists():
            aggreated_dir.mkdir(parents=True, exist_ok=True)

        # TODO: SHOULD WE DELETE THE PREVIOUS FILES? OR CREATE NEW DIRECTORY EVERY TIME?
        existing_pmn_files = list(pmn_output_dir.glob("*.csv"))

        if force_reprocess_files:

            # Delete the existing PMN files if the user wants to reprocess the files
            selected_files_unprocessed = selected_files
            for file in existing_pmn_files:
                file.unlink()

        else:

            selected_files_unprocessed = [
                file
                for file in selected_files
                if file.stem not in [f.stem for f in existing_pmn_files]
            ]

        # Check if the files have already been processed
        if len(selected_files_unprocessed) == 0:
            st.warning("All files have already been processed.")
        else:
            st.write(
                f"Processing {len(selected_files_unprocessed)} files out of {len(selected_files)}..."
            )

            with st.spinner("Processing audio files..."):
                # Create a temporary text document with the selected files
                temp_file_path = scratch_dir / "selected_files.txt"
                with open(temp_file_path, "w") as f:
                    for file in selected_files_unprocessed:
                        f.write(str(file) + "\n")

                # Process one file at a time
                command = [
                    "python",
                    "prototype/prototype_calculate_PMN_for_dir.py",
                    "--file_list",
                    str(temp_file_path),
                    "--dir_output",
                    str(pmn_output_dir),
                ]
                if use_parallel:
                    command += [
                        "--parallel",
                        "--num_workers",
                        str(num_workers),
                    ]
                res = subprocess.run(command)
                if res.returncode != 0:
                    st.error("Error processing the audio files.")
                    st.stop()
                st.success("Audio files processed successfully.")

        with st.spinner("Aggregating the PMN results..."):
            # Aggregate the PMN results
            # TODO: HORRIBLE TEMPORARY CODE, PLEASE FIX LATER
            freq_bins = [t[0] for t in freq_bins] + [
                freq_bins[-1][-1]
            ]  # Flatten the list of tuples

            files = [
                str(file) for file in pmn_output_dir.glob("*.csv")
            ]  # TODO: Check if this works with the new directory structure

            avg_csv, max_csv, median_csv = process.process_files(
                files=files,
                output_dir=aggreated_dir,
                freq_bins=freq_bins,
                offset=offset,
            )
        display_csv_file = None
        if csv_upload is not None:
            display_csv_file = csv_upload
        else:
            if agg_function == "Mean":
                display_csv_file = avg_csv
            elif agg_function == "Max":
                display_csv_file = max_csv
            elif agg_function == "Median":
                display_csv_file = median_csv

    else:
        st.error("No files selected.")
        st.stop()
        # TODO: Instead of stopping, just return to the top of the page

    if use_plotly:
        plots = plot_file(
            display_csv_file,
            sunrise_sunset_data,
            use_plotly=True,
            colors=colors,
            icons=icons,
        )
        for fig in plots:
            st.plotly_chart(fig, use_container_width=True)

    else:
        plots = plot_file(
            display_csv_file,
            sunrise_sunset_data,
            use_plotly=False,
            colors=colors,
            icons=icons,
        )
        for fig in plots:
            st.pyplot(fig)
