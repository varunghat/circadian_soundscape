import streamlit as st
import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from scripts import process
from scripts import plot
####################
# Streamlit config
if 'NUM_FREQ_BINS' not in st.session_state:
    st.session_state.NUM_FREQ_BINS = 1

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

# List of animal emojis to be used for the plots as default
# car, human, bug, elephant, bird, frog, bat
animal_emoji_list = ['🚗', '🚶', '🦗' , '🐘', '🐦', '🐸', '🦇']

st.set_page_config(
    page_title="Circadian Soundscape Visualizer",
    page_icon="images/favicon.ico",
    layout="wide",
    initial_sidebar_state="auto",
)
st.title('Circadian Soundscape Visualizer')
st.write('This is a simple web app that visualizes the circadian soundscape of a location.')
####################


def plot_file(file_path):

    df = pd.read_csv(file_path, index_col=0)
    df = process.smooth_data(df)

    fig1 = plot.plot_results_line(df, "Power-Minus-Noise", "-", save=False)
    fig2 = plot.plot_results_polar(df, "Power-Minus-Noise", "-", save=False)
    fig3 = plot.plot_results_color(df, "Power-Minus-Noise", "-", save=False)
    fig4 = plot.plot_results_color_polar(df, "Power-Minus-Noise", "-", save=False)
    return fig1, fig2, fig3, fig4




# Read a file or folder
uploaded_files = st.file_uploader(
    "Choose audiofiles",
    type=['wav', 'mp3', 'flac'], 
    accept_multiple_files=True) #TODO: Add more file types

# Options for the user
# Audio file format
audio_format = st.selectbox(
    "Select audio format",
    ["Audiomoth: YYYYMMDD_hhmmss.wav","Songmeter: Prefix_YYYYMMDD_hhmmss.wav", "TODO: THESE FORMATS NEED TO BE CHECKED"], #TODO: Check these formats
    index=0
)

# Check if the user wants to offset the time
offset_time = st.checkbox("Correct for timezone offset")

offset = st.number_input('Timezone offset (hours)', min_value=-12.0, max_value=12.0, value=0.0, step=0.5,disabled=not offset_time)
# Round offset to nearest 0.5
offset = round(offset * 2) / 2
st.write('Offset:', offset)


#TODO: Is timezone selection necessary? (Daylight savings, etc added problems)

# Frequency bins


cols = st.columns([10,10,1,1.5,2.1,2],vertical_alignment='bottom')
with cols[4]:
    #st.write('Frequency bins')
    if st.button('add freq bins',key='add_button',disabled=(st.session_state.NUM_FREQ_BINS==MAX_FREQ_BINS)) and st.session_state.NUM_FREQ_BINS < MAX_FREQ_BINS:
        st.session_state.NUM_FREQ_BINS += 1
        
with cols[5]:
    #st.write('Frequency bins')
    if st.button('remove',key='remove_button',disabled=(st.session_state.NUM_FREQ_BINS==1)) and st.session_state.NUM_FREQ_BINS > 1:
        st.session_state.NUM_FREQ_BINS -= 1

for i in range(st.session_state.NUM_FREQ_BINS):
    with cols[0]:
        min_freq = st.number_input('Min frequency (Hz)', min_value=0, value=0, step=1, key=f'min_freq_{i}')
    with cols[1]:
        max_freq = st.number_input('Max frequency (Hz)', min_value=0, value=22050, step=1,key=f'max_freq_{i}')
    with cols[2]:
        # Color picker
        color = st.color_picker('Color', key=f'color_{i}', value=COLOR_LIST[i % len(COLOR_LIST)])
    with cols[3]:
        # Animal emoji picker
        animal_emoji = st.selectbox('Icon', animal_emoji_list, key=f'animal_emoji_{i}', index=i % len(animal_emoji_list))

# Get the values of the frequency bins, colors, and animal emojis
freq_bins = []
colors = []
animal_emojis = []
for i in range(st.session_state.NUM_FREQ_BINS):
    freq_bins.append((st.session_state[f'min_freq_{i}'],st.session_state[f'max_freq_{i}']))
    colors.append(st.session_state[f'color_{i}'])
    animal_emojis.append(st.session_state[f'animal_emoji_{i}'])

# TODO: Do we need to make sure frequency bins are not overlapping?

# Add a way to upload csv files
csv_upload = st.file_uploader("Upload the aggregated PMN CSV file for a day (AFTER RUNNING AGGREGATE PMN separately, should be fixed later)", type=['csv'])

# Button
if st.button('Visualize', key='visualize_button'):
    st.write('Visualizing...')
    #TODO: Add visualization code here for PMN
    plots = plot_file(csv_upload)
    for fig in plots:
        st.pyplot(fig)
