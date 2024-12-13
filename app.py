import streamlit as st

if 'NUM_FREQ_BINS' not in st.session_state:
    st.session_state.NUM_FREQ_BINS = 1

MAX_FREQ_BINS = 5


st.set_page_config(
    page_title="Circadian Soundscape Visualizer",
    page_icon="images/favicon.ico",
    layout="wide",
    initial_sidebar_state="auto",
)
st.title('Circadian Soundscape Visualizer')
st.write('This is a simple web app that visualizes the circadian soundscape of a location.')

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


cols = st.columns([10,10,2,2],vertical_alignment='bottom')
with cols[2]:
    #st.write('Frequency bins')
    if st.button('add freq bins',key='add_button',disabled=(st.session_state.NUM_FREQ_BINS==MAX_FREQ_BINS)) and st.session_state.NUM_FREQ_BINS < MAX_FREQ_BINS:
        st.session_state.NUM_FREQ_BINS += 1
        
with cols[3]:
    #st.write('Frequency bins')
    if st.button('remove',key='remove_button',disabled=(st.session_state.NUM_FREQ_BINS==1)) and st.session_state.NUM_FREQ_BINS > 1:
        st.session_state.NUM_FREQ_BINS -= 1

for i in range(st.session_state.NUM_FREQ_BINS):
    with cols[0]:
        min_freq = st.number_input('Min frequency (Hz)', min_value=0, value=0, step=1, key=f'min_freq_{i}')
    with cols[1]:
        max_freq = st.number_input('Max frequency (Hz)', min_value=0, value=22050, step=1,key=f'max_freq_{i}')

# Get the values of the frequency bins
freq_bins = []
for i in range(st.session_state.NUM_FREQ_BINS):
    freq_bins.append((st.session_state[f'min_freq_{i}'],st.session_state[f'max_freq_{i}']))

# Button
if st.button('Visualize', key='visualize_button'):
    st.write('Visualizing...')
    #TODO: Add visualization code here