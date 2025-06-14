# FFmpeg GUI

A simple, cross-platform graphical interface for [FFmpeg](https://ffmpeg.org/) built with Python and Tkinter.  
Supports common video tasks (trim, rotate/flip, filters, speed adjustment, format conversion, metadata editing, stitching) with drag-and-drop, browse buttons, and real-time log output.

---

## 🚀 Features

- **Files Tab**  
  – Select primary and secondary (for stitching) input files and choose an output destination  
- **Trim**  
  – Cut out a segment by specifying start/end times  
- **Filters**  
  – Reverse, ping-pong effect, or apply any custom FFmpeg video filter  
- **Rotate / Flip**  
  – Quick presets (0°, 90°, 180°, 270°), custom angle, horizontal/vertical flip  
- **Speed**  
  – Change playback speed (0.1× – 4.0×), with optional audio tempo adjustment  
- **Format**  
  – Select container (mp4, mkv, mov, avi, webm), video codec, preset, CRF, bitrates, audio codec  
- **Metadata**  
  – Edit title, artist, album, genre, year, track, comment; attach cover art  
- **Stitch**  
  – Concatenate two videos end-to-end, including audio  
- **Drag & Drop**  
  – Drag files onto the window to populate the input fields  
- **Context-aware Run button**  
  – Disabled on the Files tab; enabled only when an actionable tab is selected  
- **Live Log**  
  – View FFmpeg stdout/stderr in a scrollable panel  

---

## 📋 Requirements

- **Python 3.6+**  
- **Tkinter** (included in most Python installs)  
- **FFmpeg**  
  - Must be in your system `PATH`, or  
  - Place `ffmpeg.exe` (Windows) or `ffmpeg` (macOS/Linux) alongside `ffmpeg_gui.py`

---

## 🛠 Installation

1. **Clone the repo**  
   ```bash
   git clone https://github.com/justicemate/ffmpegGUI.git
   cd ffmpeg-gui
   ```
2. **(Optional) Create a virtual environment**  
   ```bash
   python -m venv venv
   source venv/bin/activate   # macOS/Linux
   .\venv\Scripts\activate    # Windows
   ```
3. **Install dependencies**  
   _No external Python packages are required beyond the standard library._  
   If you add any, list them in `requirements.txt` and run:
   ```bash
   pip install -r requirements.txt
   ```
4. **Ensure FFmpeg is available**  
   - On Windows, download a build from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) and add to `PATH` or drop `ffmpeg.exe` into this folder.  
   - On macOS, you can use Homebrew:  
     ```bash
     brew install ffmpeg
     ```
   - On Linux, install via your distro’s package manager, e.g.:  
     ```bash
     sudo apt install ffmpeg
     ```

---

## ▶️ Usage

1. **Run the GUI**  
   ```bash
   python ffmpeg_gui.py
   ```
2. **Drag & Drop**  
   - Drag a video file onto the window to auto-fill the “Input File” field.  
   - Drag a second file onto the “Second File” entry in the Files tab when using Stitch.
3. **Or click “Browse” / “Save As”** to pick files via dialogs.
4. **Select a tab** for the desired operation:
   - Fill out its controls (e.g. times for Trim, checkboxes for Filters).
5. **Click “Run”** (enabled when a non-Files tab is active).
6. **Watch progress** in the log panel.  
7. **When finished**, a popup informs you of success or error.

---

## ⚙️ File Structure

```
.
├── ffmpeg_gui.py      # Main application
├── requirements.txt   # (Optional) Python deps
├── README.md          # This file
└── .gitignore         # Common ignores (e.g. __pycache__, venv/)
```

---

## 💡 Tips & Troubleshooting

- **FFmpeg not found**  
  If you see `FFmpeg not found at ...`, ensure:
  - The FFmpeg binary is named exactly `ffmpeg` (or `ffmpeg.exe` on Windows).  
  - It’s on your system `PATH`, or located in the same folder as `ffmpeg_gui.py`.
- **Slow GUI on large outputs**  
  The log panel updates per line; for extremely verbose filters, the UI may lag.  
- **Adding new features**  
  1. Copy one of the existing `build_*_tab()` methods  
  2. Add a new tab entry in the `self.notebook.add(...)` list  
  3. Implement the corresponding `elif tab == 'YourTabName'` block in `on_run()`.
- **Packaging**  
  To distribute as a standalone executable, use [PyInstaller](https://pyinstaller.org/):
  ```bash
  pip install pyinstaller
  pyinstaller --onefile --windowed ffmpeg_gui.py
  ```

---

## 🤝 Contributing

1. Fork this repo  
2. Create a feature branch (`git checkout -b feature/YourFeature`)  
3. Commit your changes (`git commit -m "Add YourFeature"`)  
4. Push to your branch (`git push origin feature/YourFeature`)  
5. Open a Pull Request—describe your change and why it’s useful!

---

## 📄 License

This project is released under the **MIT License**. See [LICENSE](LICENSE) for details.
