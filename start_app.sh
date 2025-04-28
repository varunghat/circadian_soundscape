#!/bin/bash

echo "Checking environment..."

if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating it now..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing requirements..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "Virtual environment already exists. Activating..."
    source venv/bin/activate
fi

echo "Starting the app..."
streamlit run app.py