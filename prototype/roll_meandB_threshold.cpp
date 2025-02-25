/* -----------------------------------------------------------------------
cppimport
<%
setup_pybind11(cfg)
%>
----------------------------------------------------------------------- */
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <cmath>
#include <vector>
#include <algorithm>
#include <numeric>

namespace py = pybind11;

// Rolling mean in dB with thresholding for 2D array
py::array_t<double> roll_meandB_threshold(py::array_t<double> input, int window_row_size, int window_col_size, double threshold) {
    // Request buffer information from input array
    auto buf = input.request();
    if (buf.ndim != 2) {
        throw std::invalid_argument("Input array must be 2-dimensional");
    }

    int rows = buf.shape[0];
    int cols = buf.shape[1];

    // Prepare output array
    py::array_t<double> output({rows, cols});
    auto input_ptr = static_cast<double*>(buf.ptr);
    auto output_ptr = static_cast<double*>(output.request().ptr);

    // Initialize output matrix with NaN
    std::fill(output_ptr, output_ptr + rows * cols, std::nan(""));

    // Create padded matrix
    int row_pad = (window_row_size - 1) / 2;
    int col_pad = (window_col_size - 1) / 2;
    std::vector<std::vector<double>> padded(rows + 2 * row_pad, std::vector<double>(cols + 2 * col_pad, 0.0));

    // Populate padded matrix
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            padded[i + row_pad][j + col_pad] = input_ptr[i * cols + j];
        }
    }

    // Allocate window vector once
    std::vector<double> window(window_row_size * window_col_size);

    // Compute rolling mean and apply threshold
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            int window_index = 0;

            // Extract window values
            for (int k = 0; k < window_row_size; k++) {
                for (int l = 0; l < window_col_size; l++) {
                    window[window_index++] = padded[i + k][j + l];
                }
            }

            // Compute mean in dB
            double sum = std::accumulate(window.begin(), window.begin() + window_index, 0.0, [](double a, double b) {
                return a + std::pow(10.0, b / 10.0);
            });
            double mean_db = 10.0 * std::log10(sum / window_index);

            // Apply threshold
            output_ptr[i * cols + j] = (mean_db > threshold)
                ? input_ptr[i * cols + j]
                : *std::min_element(window.begin(), window.begin() + window_index);
        }
    }

    return output;
}

// Pybind11 module definition
PYBIND11_MODULE(roll_meandB_threshold, m) {
    m.doc() = "Rolling mean in dB with thresholding for 2D arrays";
    m.def("roll_meandB_threshold", &roll_meandB_threshold, "Compute rolling mean in dB with thresholding",
          py::arg("input"), py::arg("window_row_size"), py::arg("window_col_size"), py::arg("threshold"));
}
