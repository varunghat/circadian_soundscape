import numpy as np


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
