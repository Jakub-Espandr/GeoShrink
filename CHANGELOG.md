# GeoShrink Changelog

## [0.1.0] - 2025-06-11

### Added
- Initial release of the GeoShrink – GeoTIFF Compressor
  - Input GeoTIFF file selection
  - Output directory selection
  - Automatic output directory suggestion based on input file location
  - Support for .tif and .tiff file formats
  - GeoTIFF to PNG conversion
  - Multi-band image support
  - High-quality LANCZOS resampling
  - Automatic data type normalization
  - Multi-threaded processing for better performance

- **Scale Control**
  - Interactive scale factor slider (0.1 to 0.8)
  - Real-time scale factor updates
  - Precise scale control with 0.05 step increments

- **Size Estimation**
  - Real-time output size estimation
  - Resolution preview
  - File size calculation
  - Compression ratio consideration

- **Progress Tracking**
  - Visual progress bar
  - Status updates
  - Conversion progress per band
  - Cancel operation support

- **Image Information Display**
  - Original resolution display
  - Original file size display
  - Expected output size preview
  - Estimated output file size

### Technical Details
- Built with Python and CustomTkinter
- Uses rasterio for GeoTIFF processing
- Implements multi-threading for better performance
- Supports various image data types
- Automatic data normalization for non-uint8 images

### Dependencies
- rasterio >= 1.3.0
- numpy >= 1.21.0
- Pillow >= 9.0.0
- customtkinter >= 5.2.0
- tkinter (Python standard library) 