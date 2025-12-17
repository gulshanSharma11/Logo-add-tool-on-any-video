# 🎬 Turbo Video Watermarker

A high-performance, local web application to batch add logos/watermarks to videos. Built with **Python**, **Streamlit**, and **FFmpeg** for maximum speed.

It uses direct FFmpeg commands and parallel processing to brand 10-15 videos simultaneously without re-encoding audio, making it significantly faster than standard Python video editors.

## ✨ Features

* **⚡ Turbo Speed:** Uses raw FFmpeg commands and parallel CPU threads.
* **📂 Logo Library:** Upload once, save forever. Switch between different brand logos instantly.
* **👁️ Smart Preview:** instantly generate a single-frame preview to check alignment before processing.
* **📏 Custom Control:**
    * **Resize:** Adjust logo width via slider (50px - 1000px).
    * **Position:** Use presets (Bottom-Left, Top-Right, etc.) or **Manual X/Y** coordinates.
* **📥 Batch & Zip:** Process unlimited videos at once and auto-download them as a single ZIP file.
* **🛡️ Server Safe:** Auto-cleans temporary files to save disk space.

---

## 🚀 Installation (Run Locally)

### Prerequisites
1.  **Python 3.8+** installed.
2.  **FFmpeg** installed on your system.
    * *Mac:* `brew install ffmpeg`
    * *Windows:* [Download FFmpeg](https://ffmpeg.org/download.html) and add to PATH.
    * *Linux:* `sudo apt install ffmpeg`

### Step 1: Clone or Download
Clone this repository or download the code.

git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
cd your-repo-name


###  How to run
1) Install Dipendencies
***pip install streamlit moviepy
***If that doesn't work, try: pip3 install "moviepy<2.0"
***brew install ffmpeg
2) Run software
***streamlit run File Name.py
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# 🎬 Basic Video Watermarker (Pure Python Version)

A simple, beginner-friendly video watermarker built with **Python**, **Streamlit**, and **MoviePy**.

This is the "Classic" version of the tool. Unlike the Turbo version (which uses complex FFmpeg commands), this version uses standard Python libraries to process videos frame-by-frame. It is excellent for learning how video editing works in Python, though it is slower than the Turbo version.

## ✨ Features

* **Pure Python Logic:** Uses `MoviePy` for all video compositing. Easy to modify and understand.
* **📂 Logo Library:** Save your favorite logos and switch between them instantly.
* **📍 Simple Positioning:** Place logos in corners (Bottom-Left, Top-Right, etc.) or Center.
* **👁️ Preview:** Generate a preview image to check alignment before processing.
* **📦 Batch Processing:** Upload multiple videos and download them all as a single ZIP file.

---

## 🛠️ Prerequisites & Installation

### 1. Install Python
Ensure you have Python 3.8 or higher installed.

### 2. Install Libraries
This version relies on `moviepy` (specifically version 1.x is recommended for stability) and `streamlit`.


###  How to run
1) Install Dipendencies
***pip install streamlit moviepy
***If that doesn't work, try: pip3 install "moviepy<2.0"
2) Run software
***streamlit run File Name.py

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
📖 How to use
Logo Settings (Left Panel):

Select Logo: Choose a saved logo from the library or upload a new one.

Save: If uploading, you can name and save the logo for future use.

Size & Position: Adjust the width slider. Choose "Standard Presets" for quick corners or "Custom" for exact X/Y pixels.

Speed: Adjust the "Concurrent Videos" slider (Default is 3). Higher = Faster, but uses more CPU.

Upload Videos (Right Panel):

Drag and drop multiple video files (MP4, MOV, AVI).

Preview:

Click 👁️ Generate Preview. The app will grab the first second of the first video to show you exactly how it looks.

Process:

Click ⚡ START TURBO PROCESSING.

Wait for the progress bar to finish.

Click the 📥 Download ZIP button to get your branded videos.
