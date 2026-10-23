FinPulse — Personal Finance & Subscription Tracker 🚀

FinPulse is a lightweight, local-first personal finance application built with Python. It features an interactive desktop GUI, SQLite data persistence, visual analytics, and an integrated OCR receipt scanner powered by OpenCV and Tesseract.

Features

Interactive GUI: User-friendly desktop interface built with Tkinter.

Local Data Storage: Lightweight SQLite database (finpulse.db) ensuring user privacy and instant performance.

OCR Receipt Scanning: Scan receipt images to extract totals and merchant information automatically.

Visual Analytics: Interactive pie charts and trend lines powered by Matplotlib to visualize spending categories over time.

Subscription Tracking: Monitor recurring spend to identify and manage unused subscriptions.

🛠️ Built With

Python 

Tkinter — Desktop Graphical User Interface

SQLite3 — Local relational database

OpenCV (opencv-python) — Image preprocessing and thresholding

Pytesseract — Python wrapper for Tesseract OCR

Matplotlib — Data visualization and charting

Prerequisites

To run this application directly from the source code, you will need Python 3.x and Tesseract OCR installed on your machine.

Installing Tesseract OCR (Windows)

Download the official Tesseract OCR installer for Windows (e.g., from UB-Mannheim's GitHub).

Run the installer and ensure it installs to the default system path:

C:\Program Files\Tesseract-OCR


The app automatically detects Tesseract if installed at this standard location.

🚀 Getting Started

1. Clone the Repository

git clone https://github.com/Guransh-Singh-1/offscript.git
cd offscript


2. Install Python Dependencies

Install the required packages using the requirements.txt file:

pip install -r requirements.txt


3. Run the Application

Launch the application by running the main Python script:

python offscript_project.py


Project Structure

├── offscript_project.py    # Main application source code
├── requirements.txt        # Python package dependencies
├── README.md               # Project documentation
└── .gitignore              # Files and folders excluded from Git


📄 License

Distributed under the MIT License. See LICENSE for more information.
