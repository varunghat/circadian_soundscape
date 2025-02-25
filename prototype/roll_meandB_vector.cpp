/* -----------------------------------------------------------------------
cppimport
<%
setup_pybind11(cfg)
%>
----------------------------------------------------------------------- */
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <cmath>
#include <algorithm>
#include <stdexcept>
#include <iostream>

namespace py = pybind11;

// Rolling mean in decibels for 1D array
py::array_t<double> roll_meandB_vector(const py::array_t<double>& input, int window_size) {
    // Validate window size
    if (window_size <= 0) {
        throw std::invalid_argument("Window size must be a positive integer.");
    }

    // Request buffer info from input array
    auto buf = input.request();
    if (buf.ndim != 1) {
        throw std::invalid_argument("Input array must be one-dimensional.");
    }

    // Extract input data
    auto x = static_cast<double*>(buf.ptr);
    int n = buf.size;

    // Prepare output array
    py::array_t<double> result(buf.size);
    auto out = static_cast<double*>(result.request().ptr);

    try {
        for (int i = 0; i < n; ++i) {
            // Define the rolling window bounds
            int start = std::max(0, i - window_size / 2);
            int end = std::min(i + window_size / 2, n - 1);

            double sum = 0.0;
            int count = 0;
            bool has_nan = false;

            // Process values within the window
            for (int j = start; j <= end; ++j) {
                if (std::isnan(x[j])) {
                    has_nan = true;  // Mark as having NaN and skip
                    break;
                }
                sum += std::pow(10.0, x[j] / 10.0);
                ++count;
            }

            // Assign output based on calculations
            if (has_nan || count == 0) {
                out[i] = std::nan("");  // Assign NaN if invalid
            } else {
                out[i] = 10 * std::log10(sum / count);  // Calculate mean in dB
            }
        }
    } catch (const std::exception& e) {
        // Handle known exceptions
        throw std::runtime_error(std::string("Error in roll_meandB_vector: ") + e.what());
    } catch (...) {
        // Handle unknown exceptions
        throw std::runtime_error("Unknown error in roll_meandB_vector.");
    }

    return result;
}

// Pybind11 module definition
PYBIND11_MODULE(roll_meandB_vector, m) {
    m.doc() = "C++ implementation of rolling mean in dB for 1D arrays";  // Module docstring
    m.def("roll_meandB_vector", &roll_meandB_vector, "Compute rolling mean in dB for a 1D array",
          py::arg("input"), py::arg("window_size"));
}