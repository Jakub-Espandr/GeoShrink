<p align="center">
  <a href="https://i.ibb.co/d4x589mV/icon.png">
    <img src="https://i.ibb.co/d4x589mV/icon.png" alt="GeoShrink Logo" width="250"/>
  </a>
</p>

<h1 align="center">GeoShrink – GeoTIFF Compressor</h1>
<p align="center"><em>(Born4Flight | FlyCamCzech | Jakub Ešpandr)</em></p>

## Overview
GeoShrink is a lightweight tool for fast conversion of GeoTIFF raster files to PNG format, with optional resizing to reduce resolution or file size. Designed for geospatial workflows where sharing or previewing large imagery (e.g. from UAV, satellite, or remote sensing) requires more compact formats.

---

## ✨ Features

- **File Management**
  - Input GeoTIFF file selection
  - Output directory selection
  - Support for .tif and .tiff file formats

- **Image Processing**
  - GeoTIFF to PNG conversion
  - Multi-band image support
  - High-quality LANCZOS resampling
  - Multi-threaded processing

- **Scale Control**
  - Interactive scale factor slider (0.1 to 0.8)
  - Real-time scale factor updates
  - Precise scale control

- **Size Estimation**
  - Real-time output size estimation
  - Resolution preview
  - File size calculation

- **Progress Tracking**
  - Visual progress bar
  - Status updates
  - Cancel operation support

---

## 📦 Requirements

- Python 3.6+
- [rasterio](https://rasterio.readthedocs.io/) – Geospatial raster I/O library
- [numpy](https://numpy.org/) – Numerical computing library
- [Pillow](https://python-pillow.org/) – Image processing library
- [customtkinter](https://github.com/TomSchimansky/CustomTkinter) – Modern UI library

---

## 🚀 Installation

```bash
git clone https://github.com/Jakub-Espandr/geoshrink.git
cd geoshrink
```

Create a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
```

Install required Python libraries:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python main.py
```

---

## 🛠️ Usage

1. **Select Input**: Click the "Select GeoTIFF" button to choose your input GeoTIFF file.
2. **Choose Output**: Click the "Select Directory" button to specify where to save the output.
3. **Adjust Scale**: Use the slider to set the desired scale factor (0.1 to 0.8).
4. **Monitor Progress**: Watch the progress bar and status updates during conversion.
5. **Cancel if Needed**: Use the cancel button to stop the conversion process.

---

## 📁 Project Structure

```
geoshrink/
├── main.py                  # Entry point
├── assets/
│   ├── icons/              # Application icons
│   └── fonts/              # Custom fonts
├── requirements.txt        # Dependencies
└── CHANGELOG.md           # Version history
```

---

## 🔐 License

This project is licensed under the **Non-Commercial Public License (NCPL v1.0)**  
© 2025 Jakub Ešpandr - Born4FLight, FlyCamCzech

See the [LICENSE](https://github.com/Jakub-Espandr/geoshrink/raw/main/LICENSE) file for full terms.

---

## 🙏 Acknowledgments

- Built with ❤️ using CustomTkinter and open-source libraries
