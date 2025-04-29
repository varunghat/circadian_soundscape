# %%
import os
import numpy as np
import pandas as pd
from scipy.io import wavfile
from scipy.signal import get_window, stft
import matplotlib.pyplot as plt
from scipy.fftpack import fft
import cppimport
import argparse
from tqdm import tqdm

# Compile and import C++ modules

# Get the path of the current directory
dir_path = os.path.dirname(os.path.realpath(__file__))


def load_cpp_modules():
    cpp_dir = dir_path  # Folder where .cpp files are located

    print("Importing C++ modules...")
    roll_meandB = cppimport.imp_from_filepath(os.path.join(cpp_dir, "roll_meandB.cpp"))
    print("roll_meandB imported successfully.")

    roll_meandB_vector = cppimport.imp_from_filepath(
        os.path.join(cpp_dir, "roll_meandB_vector.cpp")
    )
    print("roll_meandB_vector imported successfully.")

    roll_meandB_threshold = cppimport.imp_from_filepath(
        os.path.join(cpp_dir, "roll_meandB_threshold.cpp")
    )
    print("roll_meandB_threshold imported successfully.")

    return roll_meandB, roll_meandB_vector, roll_meandB_threshold


# TODO: Move these to a variable to send to all functions
roll_meandB, roll_meandB_vector, roll_meandB_threshold = load_cpp_modules()


def calculate_spectrogram_amplitude(
    sound_segment, wl=384, overlap=0, sampling_rate=44100
):
    """
    Calculate the amplitude of the spectrogram with normalization and dB conversion.

    Parameters:
        sound_segment (1D numpy array): Input audio data.
        wl (int): Window length for FFT.
        overlap (float): Overlap percentage (0 to 100).
        sampling_rate (int): Sampling rate of the audio.

    Returns:
        numpy.ndarray: Spectrogram amplitude in dB (2D array).
    """
    # Normalize the audio data
    sound_segment = sound_segment / np.max(np.abs(sound_segment))

    # Parameters
    step = wl - int(wl * (overlap / 100))
    window = get_window("hamming", wl, fftbins=True)
    window /= np.sum(window)  # Normalize the window to match R's behavior

    # Process the signal
    segments = [
        sound_segment[i : i + wl] * window
        for i in range(0, len(sound_segment) - wl + 1, step)
    ]
    fft_segments = [np.abs(fft(segment))[: wl // 2] for segment in segments]

    # Combine FFT segments into a matrix
    amplitude = np.array(fft_segments).T

    # Normalize and convert to dB
    amplitude /= np.max(amplitude)  # Normalize amplitude
    epsilon = 1e-10  # Small constant to avoid log(0)
    raw_spectro = 20 * np.log10(amplitude + epsilon)

    return raw_spectro


def smooth_noise_profile(raw_spectro, window_size=3, threshold=-90):
    """
    Smooth the noise profile using a moving average filter and apply a minimum threshold.

    Parameters:
        raw_spectro (numpy.ndarray): Input spectrogram.
        window_size (int): Window size for smoothing.
        threshold (float): Minimum value to apply to the smoothed result.

    Returns:
        numpy.ndarray: Smoothed spectrogram with threshold applied.
    """
    smoothed = roll_meandB.roll_meandB(raw_spectro, window_size=window_size)
    return np.maximum(smoothed, threshold)


def calculate_mode_per_row(matrix, window_size=5):
    """
    Calculate the mode for each row in a 2D array.

    Parameters:
        matrix (numpy.ndarray): Input 2D array.
        window_size (int): Rolling window size for smoothing.

    Returns:
        numpy.ndarray: 1D array of modes for each row.
    """
    rows, _ = matrix.shape
    modes = np.empty(rows, dtype=np.float64)

    for i, row in enumerate(matrix):
        modes[i] = roll_meandB_vector.roll_meandB_vector(row, window_size).max()
    return modes


def subtract_background_noise(spectrogram, background_noise):
    """
    Subtract the background noise from the spectrogram, truncating negative values to zero.

    Parameters:
        spectrogram (numpy.ndarray): Input spectrogram.
        background_noise (numpy.ndarray): Background noise (1D array).

    Returns:
        numpy.ndarray: Spectrogram with background noise subtracted.
    """
    result = spectrogram - background_noise[:, None]
    return np.maximum(result, 0)


def apply_threshold_neighborhood(
    matrix, window_row_size=9, window_col_size=3, threshold=3
):
    """
    Apply thresholding to neighborhoods in a 2D matrix using a rolling mean filter.

    Parameters:
        matrix (numpy.ndarray): Input 2D array.
        window_row_size (int): Row size for the rolling window.
        window_col_size (int): Column size for the rolling window.
        threshold (float): Threshold for applying the neighborhood operation.

    Returns:
        numpy.ndarray: Processed matrix after applying thresholding.
    """
    return roll_meandB_threshold.roll_meandB_threshold(
        matrix, window_row_size, window_col_size, threshold
    )


def calculate_PMN_from_matrix(ale_matrix):
    """
    Calculate Power Minus Noise (PMN) from the processed matrix.

    Parameters:
        ale_matrix (numpy.ndarray): Input matrix after neighborhood processing.

    Returns:
        numpy.ndarray: PMN values for each row.
    """
    return ale_matrix.sum(axis=1)


def calculate_PMN(sound_segment):
    """
    Calculate df Power Minus Noise (PMN) from sound segment.

    Parameters:
        sound_segment: Input sound array.

    Returns:
        pandas.DataFrame: PMN values as df.
    """
    wl = 384
    overlap = 0
    threshold = -90
    neighborhood_threshold = 3

    # Step 1: Calculate spectrogram amplitude
    raw_spectro = calculate_spectrogram_amplitude(sound_segment, wl=wl, overlap=overlap)

    # Step 2: Smooth noise profile
    raw_spectro_roll = smooth_noise_profile(
        raw_spectro, window_size=3, threshold=threshold
    )

    # Step 3: Calculate mode
    spectro_mode = calculate_mode_per_row(raw_spectro_roll, window_size=5)

    # Step 4: Subtract background noise
    spectro_less_mode = subtract_background_noise(raw_spectro, spectro_mode)

    # Step 5: Apply neighborhood thresholding
    ale_matrix = apply_threshold_neighborhood(
        spectro_less_mode,
        window_row_size=9,
        window_col_size=3,
        threshold=neighborhood_threshold,
    )

    # Step 6: Calculate PMN
    PMN = calculate_PMN_from_matrix(ale_matrix)

    # Step 7: Duplicate PMN and spectro_mode to match 384 rows
    PMN_repeated = np.tile(PMN, 2)  # Repeat PMN twice
    spectro_mode_repeated = np.tile(spectro_mode, 2)  # Repeat noise values twice

    # Step 8: Create DataFrame
    df = pd.DataFrame(
        {
            "Frequency": np.arange(1, wl + 1),  # Frequency from 1 to 384
            "PMN": PMN_repeated,
            "Noise": spectro_mode_repeated,
        }
    )
    return df


def calculate_PMN_for_file(filepath):
    sampling_rate, data = wavfile.read(
        filepath
    )  # Placeholder for extracting 'from' and 'to'
    length = int(len(data) / sampling_rate / 60)
    list_df = []
    for k in range(length):
        # Read wav file for the current minute (assuming a utility to extract minutes)
        sound_segment = data[k * sampling_rate * 60 : (k + 1) * sampling_rate * 60]
        df = calculate_PMN(sound_segment)
        list_df.append(df)
    df_output = pd.concat(list_df)
    return df_output


def calculate_PMN_for_dir(dir_input, dir_output, if_print=False):
    """
    Find all .wav files and export PMN result for each file accordingly in the same directory
    """
    files = next(os.walk(dir_input))[2]
    files = [x for x in files if x.endswith(".WAV")]
    files = np.sort(files)
    for file in tqdm(files):
        filepath = os.path.join(dir_input, file)
        df_file_result = calculate_PMN_for_file(filepath)
        filename = os.path.splitext(os.path.basename(file))[0]
        filename_output = f"{filename}.csv"
        df_file_result.to_csv(os.path.join(dir_output, filename_output))
        if if_print:
            print(f"{filename_output} exported to {dir_output}")


# dir_input = """your input directory"""
# calculate_PMN_for_dir(dir_input)

# Get args from command line
parser = argparse.ArgumentParser(
    description="Calculate PMN for .wav files in a directory."
)
parser.add_argument(
    "dir_input",
    type=str,
    help="Directory containing .wav files to process.",
)
parser.add_argument(
    "dir_output",
    type=str,
    help="Directory to save the output .csv files.",
)

args = parser.parse_args()
dir_input = args.dir_input
dir_output = args.dir_output

if not os.path.exists(dir_output):
    os.makedirs(dir_output)

if not os.path.exists(dir_input):
    raise FileNotFoundError(f"Input directory {dir_input} does not exist.")


calculate_PMN_for_dir(dir_input, dir_output)


# %%
