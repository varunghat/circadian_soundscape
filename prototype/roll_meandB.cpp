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

namespace py = pybind11;

// Rolling mean in decibels function
py::array_t<double> roll_meandB(py::array_t<double> x, int window_size) {
    // Check for valid window size
    if (window_size <= 0) {
        throw std::invalid_argument("Window size must be a positive integer");
    }

    // Get buffer info from input numpy array
    auto buf = x.request();
    if (buf.ndim != 2) {
        throw std::invalid_argument("Input array must be 2-dimensional");
    }

    int rows = buf.shape[0];
    int cols = buf.shape[1];

    // Output array
    py::array_t<double> out({rows, cols});
    auto x_ptr = static_cast<double*>(buf.ptr);
    auto out_ptr = static_cast<double*>(out.request().ptr);

    try {
        for (int k = 0; k < cols; ++k) { // Iterate over columns
            for (int i = 0; i < rows; ++i) { // Iterate over rows
                int start = std::max(0, i - window_size / 2);
                int end = std::min(i + window_size / 2, rows - 1);

                double sum = 0.0;
                int count = 0;
                bool has_nan = false;

                // Compute sum in the window
                for (int j = start; j <= end; ++j) {
                    double value = x_ptr[j * cols + k];
                    if (std::isnan(value)) {
                        has_nan = true;
                        break;
                    }
                    sum += std::pow(10.0, value / 10.0);
                    ++count;
                }

                // Assign result
                if (has_nan || count == 0) {
                    out_ptr[i * cols + k] = NAN; // Assign NaN for invalid cases
                } else {
                    double mean_dB = 10 * std::log10(sum / count);
                    out_ptr[i * cols + k] = mean_dB;
                }
            }
        }
    } catch (const std::exception &e) {
        throw std::runtime_error(std::string("Error in roll_meandB: ") + e.what());
    } catch (...) {
        throw std::runtime_error("Unknown error occurred in roll_meandB");
    }

    return out;
}

// Pybind11 module definition
PYBIND11_MODULE(roll_meandB, m) {
    m.doc() = "Rolling mean in dB with center alignment"; // Optional module docstring
    m.def("roll_meandB", &roll_meandB, "Compute a rolling mean in decibels",
          py::arg("x"), py::arg("window_size"));
}