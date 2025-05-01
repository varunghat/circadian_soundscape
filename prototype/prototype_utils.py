import shutil
import sys

def check_cpp_compiler():
    """
    Checks if a C++ compiler (cl.exe on Windows, g++ on Linux/Mac) is available.
    Raises an error or gives instructions if not found.
    """
    if sys.platform.startswith('win'):
        compiler = shutil.which('cl')
        if compiler is None:
            raise EnvironmentError(
                "C++ compiler (cl.exe) not found!\n"
                "Please install Visual Studio Build Tools with C++ workload "
                "and run this script from 'Developer Command Prompt for VS'."
            )
    else:
        # For Linux/Mac
        compiler = shutil.which('g++') or shutil.which('clang++')
        if compiler is None:
            raise EnvironmentError(
                "C++ compiler (g++ or clang++) not found!\n"
                "Please install a C++ compiler via your package manager.\n"
                "e.g., sudo apt install build-essential"
            )
    return compiler