@echo off
echo Checking environment...

if not exist venv (
    echo Virtual environment not found. Creating it now...
    python -m venv venv
    call venv\Scripts\activate
    echo Installing requirements...
    pip install --upgrade pip
    pip install -r requirements.txt
) else (
    echo Virtual environment already exists. Activating...
    call venv\Scripts\activate
)

echo Starting the app...
streamlit run app.py

pause
