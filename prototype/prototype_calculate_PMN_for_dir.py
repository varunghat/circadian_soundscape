# %%
import os
import numpy as np
import pandas as pd
from scipy.io import wavfile
from scipy.signal import get_window, stft, spectrogram
import matplotlib.pyplot as plt
from scipy.fftpack import fft
from scipy.ndimage import uniform_filter1d
import cppimport
import argparse
from tqdm import tqdm
import gc
import numba

from concurrent.futures import ProcessPoolExecutor, as_completed

from roll_meandB_py import (
    roll_meandB,
    roll_meandB_vector,
    roll_meandB_threshold,
    roll_meandB_efficient,
    roll_meandB_vector_efficient,
    roll_meandB_threshold_efficient,
    roll_meandB_threshold_safe,
    roll_meandB_threshold_numba,
)

# DEBUG cODE
"""
from pympler import muppy, summary, asizeof
import time


def print_memory_summary(tag=""):
    all_objects = muppy.get_objects()
    sum1 = summary.summarize(all_objects)
    print(f"\n[ MEMORY SUMMARY: {tag} ]")
    summary.print_(sum1)
"""

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
# roll_meandB, roll_meandB_vector, roll_meandB_threshold = load_cpp_modules()


def calculate_spectrogram_scipy(sound_segment, wl=384, overlap=0, sampling_rate=44100):
    """
    Calculate the spectrogram using scipy.

    Parameters:
        sound_segment (1D numpy array): Input audio data.
        wl (int): Window length for FFT.
        overlap (float): Overlap percentage (0 to 100).
        sampling_rate (int): Sampling rate of the audio.

    Returns:
        numpy.ndarray: Spectrogram amplitude (2D array).
    """
    step = wl - int(wl * (overlap / 100))
    # Normalize the audio data
    sound_segment = sound_segment / np.max(np.abs(sound_segment))
    window = get_window("hamming", wl, fftbins=True)
    f, t, Sxx = spectrogram(
        sound_segment,
        fs=sampling_rate,
        window=window,
        nperseg=wl,
        noverlap=overlap,
        mode="magnitude",
        scaling="spectrum",  # Important: prevents power scaling
        return_onesided=True,
    )
    return Sxx


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
    smoothed = roll_meandB_efficient(raw_spectro, window_size=window_size)
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


def dB_mode_per_row(matrix, window_size=5):
    """
    Calculate the dB mode for each row in a 2D array.

    Parameters:
        matrix (numpy.ndarray): Input 2D array.
        window_size (int): Rolling window size for smoothing.

    Returns:
        numpy.ndarray: 1D array of dB modes for each row.
    """

    matrix = np.array(matrix, dtype=np.float64)
    modes = np.empty(matrix.shape[0], dtype=np.float64)

    for i, row in enumerate(matrix):
        seq_100 = np.linspace(np.min(row), np.max(row), num=100)
        counts, bin_edges = np.histogram(row, bins=seq_100)

        counts = roll_meandB_vector(counts, window_size=window_size)

        # print("Counts after rolling mean:", counts)

        mids = (bin_edges[:-1] + bin_edges[1:]) / 2

        # print(mids)

        mode = mids[np.argmax(counts)]

        modes[i] = mode

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
    return roll_meandB_threshold_numba(
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
    # print_memory_summary(tag=os.path.basename(__file__))
    wl = 384
    overlap = 0
    threshold = -90
    neighborhood_threshold = 3

    # Step 1: Calculate spectrogram amplitude
    # raw_spectro = calculate_spectrogram_amplitude(sound_segment, wl=wl, overlap=overlap)
    raw_spectro = calculate_spectrogram_amplitude(
        sound_segment, wl=wl, overlap=overlap, sampling_rate=44100
    )
    # print("Step1: Raw spectrogram size (MB):", asizeof.asizeof(raw_spectro) / 1024**2)

    # time.sleep(2)
    # Step 2: Smooth noise profile
    raw_spectro_roll = smooth_noise_profile(
        raw_spectro, window_size=3, threshold=threshold
    )

    # print(
    #    "Step2: Smoothed spectrogram size: (MB)",
    #    asizeof.asizeof(raw_spectro_roll) / 1024**2,
    # )
    # time.sleep(2)

    # print("Raw spectrogram roll shape:", raw_spectro_roll.shape)
    # print("Raw spectrogram roll:", raw_spectro_roll)

    # Step 3: Calculate mode
    spectro_mode = dB_mode_per_row(raw_spectro_roll, window_size=5)

    # print("Step3: Spectrogram mode size: (MB)", asizeof.asizeof(spectro_mode) / 1024**2)

    # time.sleep(2)

    del raw_spectro_roll
    gc.collect()

    # print("Spectrogram mode shape:", spectro_mode.shape)
    # print("Spectrogram mode:", spectro_mode)

    # Step 4:  Smooth the mode
    spectro_mode = roll_meandB_vector(spectro_mode, window_size=5)

    # print("Step4: Smoothed mode size: (MB)", asizeof.asizeof(spectro_mode) / 1024**2)

    # time.sleep(2)
    # print("Spectrogram mode smoothed shape:", spectro_mode.shape)
    # print("Spectrogram mode smoothed:", spectro_mode)

    # Step 5: Subtract background noise
    spectro_less_mode = subtract_background_noise(raw_spectro, spectro_mode)

    # print(
    #    "Step5: Spectrogram less mode size: (MB)",
    #    asizeof.asizeof(spectro_less_mode) / 1024**2,
    # )

    # time.sleep(2)
    del raw_spectro
    gc.collect()
    # print("Spectrogram less mode shape:", spectro_less_mode.shape)
    # print("Spectrogram less mode:", spectro_less_mode)

    # Step 6: Apply neighborhood thresholding
    ale_matrix = apply_threshold_neighborhood(
        spectro_less_mode,
        window_row_size=9,
        window_col_size=3,
        threshold=neighborhood_threshold,
    )

    # print("Step6: ALE matrix size: (MB)", asizeof.asizeof(ale_matrix) / 1024**2)

    # time.sleep(2)
    del spectro_less_mode
    gc.collect()
    # print("ALE matrix shape:", ale_matrix.shape)
    # print("ALE matrix:", ale_matrix)

    # Step 7: Calculate PMN
    PMN = calculate_PMN_from_matrix(ale_matrix)

    # print("Step7: PMN size: (MB)", asizeof.asizeof(PMN) / 1024**2)

    # time.sleep(2)
    del ale_matrix
    gc.collect()
    # print("PMN shape:", PMN.shape)
    # print("PMN:", PMN)

    # Step 8: Duplicate PMN and spectro_mode to match 384 rows
    PMN_repeated = np.tile(PMN, 2)  # Repeat PMN twice
    spectro_mode_repeated = np.tile(spectro_mode, 2)  # Repeat noise values twice

    # Step 9: Create DataFrame
    df = pd.DataFrame(
        {
            "Frequency": np.arange(1, wl + 1),  # Frequency from 1 to 384
            "PMN": PMN_repeated,
            "Noise": spectro_mode_repeated,
        }
    )

    # print("Step9: DataFrame size (MB):", asizeof.asizeof(df) / 1024**2)

    # print_memory_summary(tag=os.path.basename(__file__) + " - After DataFrame creation")
    return df


def calculate_PMN_for_file(filepath, save=False, output_dir=None):
    sampling_rate, data = wavfile.read(
        filepath
    )  # Placeholder for extracting 'from' and 'to'

    # print("Sampling rate:", sampling_rate)
    # print("Data: ", data[:20])

    if save:
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(filepath), "output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        filename = os.path.splitext(os.path.basename(filepath))[0]
        output_path = os.path.join(output_dir, f"{filename}.csv")

    length = int(len(data) / sampling_rate / 60)
    list_df = []
    for k in range(length):
        # print("Processing minute:", k + 1, "of", length, "pid:", os.getpid())
        # Read wav file for the current minute (assuming a utility to extract minutes)
        sound_segment = data[k * sampling_rate * 60 : (k + 1) * sampling_rate * 60]

        df = calculate_PMN(sound_segment)

        # print("PMN shape:", df.shape)
        # print("PMN:", df)
        if save:
            df.to_csv(output_path, mode="a", header=(k == 0), index=False)
        else:
            list_df.append(df)
        # list_df.append(df)

    if not save:
        df_output = pd.concat(list_df, ignore_index=True)
        return df_output
    else:
        # print(f"PMN result saved to {output_path}")
        return None


def calculate_PMN_for_dir(dir_input, dir_output, if_print=False):
    """
    Find all .wav files and export PMN result for each file accordingly in the same directory
    """
    files = next(os.walk(dir_input))[2]
    files = [x for x in files if x.endswith(".WAV")]
    files = np.sort(files)

    os.makedirs(dir_output, exist_ok=True)

    files = [os.path.join(dir_input, file) for file in files]

    # Parallel processing
    no_workers = 4  # Number of workers for parallel processing

    with ProcessPoolExecutor(max_workers=no_workers) as executor:
        futures = [
            executor.submit(wrapped_calculate, file, dir_output) for file in files
        ]

        for f in tqdm(as_completed(futures), total=len(futures)):
            _ = f.result()

    """
    for file in tqdm(files):
        filepath = os.path.join(dir_input, file)
        df_file_result = calculate_PMN_for_file(filepath)
        filename = os.path.splitext(os.path.basename(file))[0]
        filename_output = f"{filename}.csv"
        df_file_result.to_csv(os.path.join(dir_output, filename_output))
        if if_print:
            print(f"{filename_output} exported to {dir_output}")
    """


def wrapped_calculate(file, dir_output):
    try:
        # print(f"Calculating PMN for file: {file}")
        return calculate_PMN_for_file(file, save=True, output_dir=dir_output)
    except Exception as e:
        print(f"⚠️ Error processing {file}: {e}")
        return None


# dir_input = """your input directory"""
# calculate_PMN_for_dir(dir_input)

# Get args from command line
parser = argparse.ArgumentParser(
    description="Calculate PMN for .wav files in a directory."
)
parser.add_argument(
    "--dir_input",
    type=str,
    help="Directory containing .wav files to process.",
)
parser.add_argument(
    "--file_input",
    type=str,
    help="File containing .wav files to process.",
)

parser.add_argument(
    "--file_list",
    type=str,
    help="File containing a list of .wav files to process.",
)

parser.add_argument(
    "--dir_output",
    type=str,
    help="Directory to save the output .csv files. If not provided, it will be created in the input directory.",
)

parser.add_argument(
    "--parallel",
    action="store_true",
    help="Use parallel processing for multiple files.",
)
parser.add_argument(
    "--num_workers",
    type=int,
    default=8,
    help="Number of workers for parallel processing.",
)


if __name__ == "__main__":

    args = parser.parse_args()
    dir_input = None
    file_input = None
    file_list = None

    if args.parallel:
        num_workers = args.num_workers
    else:
        num_workers = 1

    dir_output = args.dir_output

    if args.dir_input:
        if args.file_input or args.file_list:
            raise ValueError(
                "Please provide only one of --dir_input, --file_input, or --file_list argument."
            )

        dir_input = args.dir_input
        if dir_output is None:
            dir_output = os.path.join(dir_input, "output")
        os.makedirs(dir_output, exist_ok=True)

        calculate_PMN_for_dir(dir_input, dir_output)
    elif args.file_input:
        if args.dir_input or args.file_list:
            raise ValueError(
                "Please provide only one of --dir_input, --file_input, or --file_list argument."
            )
        if not os.path.exists(args.file_input):
            raise ValueError(f"File {args.file_input} does not exist.")
        if not args.file_input.endswith(".WAV"):
            raise ValueError(f"File {args.file_input} is not a .WAV file.")

        file_input = args.file_input
        if dir_output is None:
            dir_output = os.path.join(file_input, "output")
        if not os.path.exists(dir_output):
            os.makedirs(dir_output)

        calculate_PMN_for_file(file_input, save=True, output_dir=dir_output)

    elif args.file_list:
        if args.dir_input or args.file_input:
            raise ValueError(
                "Please provide only one of --dir_input, --file_input, or --file_list argument."
            )
        if not os.path.exists(args.file_list):
            raise ValueError(f"File {args.file_list} does not exist.")

        with open(args.file_list, "r") as f:
            file_list = f.readlines()
        file_list = [x.strip() for x in file_list]

        if dir_output is None:
            dir_output = os.path.join(os.path.dirname(file_list[0]), "output")
        if not os.path.exists(dir_output):
            os.makedirs(dir_output)

        # Serial processing
        if args.parallel is False:
            print("Calculating PMN for files in serial...")
            for file in tqdm(file_list):
                calculate_PMN_for_file(file, save=True, output_dir=dir_output)
                print(f"PMN result saved to {file}")

            exit()
        else:
            print("Calculating PMN for files in parallel...")
            # Parallel processing

            with ProcessPoolExecutor(max_workers=num_workers) as executor:

                futures = [
                    executor.submit(wrapped_calculate, file, dir_output)
                    for file in file_list
                ]

                for f in tqdm(as_completed(futures), total=len(futures)):
                    _ = f.result()

    else:
        raise ValueError("Please provide either --dir_input or --file_input argument.")


# %%
