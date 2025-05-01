import numpy as np
from scipy.ndimage import uniform_filter1d
from numpy.lib.stride_tricks import sliding_window_view


def roll_meandB(x, window_size):
    """
    Calculate the rolling mean of a 2D array along the second axis (columns) with a specified window size.

    Parameters:
    x (numpy.ndarray): 2D array of shape (n, m) where n is the number of rows and m is the number of columns.
    window_size (int): The size of the rolling window.

    Returns:
    numpy.ndarray: 2D array of shape (n, m) containing the rolling mean values.
    """
    # Ensure the input x is a numpy array
    x = np.array(x)

    # Get the number of rows and columns
    rows, cols = x.shape
    out = np.zeros((rows, cols))

    for k in range(cols):
        column = x[:, k]
        for i in range(rows):
            start = max(0, i - window_size // 2)
            end = min(rows - 1, i + window_size // 2)
            window = column[start : end + 1]

            # Handling NA values
            if np.isnan(window).any():
                out[i, k] = np.nan
                continue

            sum = 0
            sum = np.sum(np.power(10, window / 10.0))

            meanDB = 10 * np.log10(sum / len(window))
            out[i, k] = meanDB

    return out


def roll_meandB_efficient(x, window_size):
    """
    Efficient rolling mean in dB over rows of a 2D array.

    Parameters:
    x : np.ndarray, shape (n_rows, n_cols)
        Input 2D array.
    window_size : int
        Size of the rolling window.

    Returns:
    np.ndarray
        Smoothed 2D array in dB scale.
    """
    x = np.asarray(x, dtype=np.float64)

    # Convert to linear scale
    x_lin = np.power(10, x / 10.0)

    # Rolling mean along axis=0 (rows), per column
    smoothed_sum = uniform_filter1d(
        x_lin, size=window_size, axis=0, mode="constant", cval=0.0
    )

    # Create a divisor array (rolling count of valid elements per position)
    ones = np.ones_like(x_lin)
    window_counts = uniform_filter1d(
        ones, size=window_size, axis=0, mode="constant", cval=0.0
    )

    # Avoid division by zero
    with np.errstate(divide="ignore", invalid="ignore"):
        smoothed_lin = smoothed_sum / window_counts
        out = 10 * np.log10(smoothed_lin)
        out[~np.isfinite(out)] = np.nan

    return out


def roll_meandB_vector(x, window_size):
    """
    Calculate the rolling mean of a 1D array with a specified window size.

    Parameters:
    x (numpy.ndarray): 1D array of shape (n,).
    window_size (int): The size of the rolling window.

    Returns:
    numpy.ndarray: 1D array of shape (n,) containing the rolling mean values.
    """
    n = len(x)
    out = np.zeros(n)

    for i in range(n):
        start = max(0, i - window_size // 2)
        end = min(n - 1, i + window_size // 2)
        window = x[start : end + 1]

        # Handling NA values
        if np.isnan(window).any():
            out[i] = np.nan
            continue

        sum = 0
        sum = np.sum(np.power(10, window / 10.0))

        meanDB = 10 * np.log10(sum / len(window))
        out[i] = meanDB

    return out


def roll_meandB_vector_efficient(x, window_size):

    x = np.asarray(x, dtype=np.float64)
    n = len(x)
    out = np.full(n, np.nan)

    # Precompute linear version
    x_lin = np.power(10, x / 10.0)

    for i in range(n):
        start = max(0, i - window_size // 2)
        end = min(n, i + window_size // 2 + 1)

        window = x_lin[start:end]
        if np.isnan(window).any():
            continue

        mean_lin = np.mean(window)
        out[i] = 10 * np.log10(mean_lin)

    return out


def roll_meandB_threshold(x, windowRowSize=9, windowColSize=3, threshold=3):
    """
    Calculate the rolling mean of a 2D array along the second axis (columns) with a specified window size.
    The function also applies a threshold to the rolling mean values.

    Parameters:
    x (numpy.ndarray): 2D array of shape (n, m) where n is the number of rows and m is the number of columns.
    windowRowSize (int): The size of the rolling window along rows.
    windowColSize (int): The size of the rolling window along columns.
    threshold (float): The threshold value for filtering.

    Returns:
    numpy.ndarray: 2D array of shape (n, m) containing the rolling mean values after applying the threshold.
    """
    # Ensure the input x is a numpy array
    x = np.array(x)

    # Get the number of rows and columns
    rows, cols = x.shape
    out = np.zeros((rows, cols))

    padded = np.zeros((rows + windowRowSize - 1, cols + windowColSize - 1))

    rowPad = (windowRowSize - 1) // 2
    colPad = (windowColSize - 1) // 2

    padded[rowPad : rowPad + rows, colPad : colPad + cols] = x

    window = np.ones((windowRowSize * windowColSize))

    for i in range(rows):
        for j in range(cols):
            windowIndex = 0
            for k in range(windowRowSize):
                for l in range(windowColSize):
                    value = padded[i + k, j + l]

                    window[windowIndex] = value
                    windowIndex += 1

            if windowIndex > 0:
                sum = 0
                sum = np.sum(np.power(10, window / 10.0))
                meanDB = 10 * np.log10(sum / windowIndex)
                if meanDB > threshold:
                    out[i, j] = x[i, j]
                else:
                    out[i, j] = min(window[:windowIndex])

    return out


def roll_meandB_threshold_efficient(x, windowRowSize=9, windowColSize=3, threshold=3.0):
    x = np.asarray(x, dtype=np.float64)

    # Padding
    row_pad = (windowRowSize - 1) // 2
    col_pad = (windowColSize - 1) // 2
    x_padded = np.pad(
        x, ((row_pad, row_pad), (col_pad, col_pad)), mode="constant", constant_values=0
    )

    # Sliding window view
    windows = sliding_window_view(x_padded, (windowRowSize, windowColSize))
    win_shape = windows.shape
    num_windows = win_shape[0] * win_shape[1]
    flat_windows = windows.reshape(num_windows, -1)

    # Compute linear mean and dB
    lin_vals = np.power(10, flat_windows / 10.0)
    mean_lin = lin_vals.mean(axis=1)
    mean_db = 10 * np.log10(mean_lin + 1e-10)

    # Compute min of each window
    min_vals = flat_windows.min(axis=1)

    # Use center value from original x
    center_vals = x.flatten()
    out_flat = np.where(mean_db > threshold, center_vals, min_vals)

    # Reshape to original
    return out_flat.reshape(win_shape[0], win_shape[1])
