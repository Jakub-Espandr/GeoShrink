import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import numpy as np
from PIL import Image
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import math
import time
from tkinter import font
import threading

def process_band(band, new_width, new_height):
    return np.array(Image.fromarray(band).resize((new_width, new_height), Image.Resampling.LANCZOS))

def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes:.1f} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.1f} KB"
    else:
        return f"{size_bytes/(1024*1024):.1f} MB"

class GeoTiffConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("GeoShrink – GeoTIFF Compressor")
        self.root.geometry("600x700")
        self.root.minsize(600, 700)
        self.set_application_icon()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # Load custom fonts
        try:
            font_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "fonts")
            self.regular_font = ("fccTYPO-Regular", 12)
            self.bold_font = ("fccTYPO-Bold", 12)
        except Exception as e:
            print(f"Warning: Could not load custom fonts: {e}")
            self.regular_font = ("Arial", 12)
            self.bold_font = ("Arial", 12)

        # Set main window background to match frames
        self.root.configure(bg="#232323")
        # Main frame with larger corner radius and matching color
        self.main_frame = ctk.CTkFrame(root, corner_radius=20, fg_color="#232323")
        self.main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Input file selection (use grid for perfect alignment)
        input_frame = ctk.CTkFrame(self.main_frame, corner_radius=20)
        input_frame.pack(fill="x", pady=(15, 5))
        ctk.CTkLabel(input_frame, text="Input", font=self.bold_font, anchor="w").grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=(5, 0))
        self.input_path = tk.StringVar(value="No file selected")
        lbl_input = ctk.CTkLabel(input_frame, textvariable=self.input_path, font=self.regular_font, anchor="w")
        lbl_input.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        btn_input = ctk.CTkButton(input_frame, text="Select GeoTIFF", command=self.browse_input, fg_color="#444444", hover_color="#666666", text_color="white", font=self.bold_font, corner_radius=20, width=140, height=36)
        btn_input.grid(row=1, column=1, padx=5, pady=5)
        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_columnconfigure(1, weight=0)

        # Output directory selection (use grid for perfect alignment)
        output_frame = ctk.CTkFrame(self.main_frame, corner_radius=14)
        output_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(output_frame, text="Output", font=self.bold_font, anchor="w").grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=(5, 0))
        self.output_path = tk.StringVar(value="No directory selected")
        lbl_output = ctk.CTkLabel(output_frame, textvariable=self.output_path, font=self.regular_font, anchor="w")
        lbl_output.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        btn_output = ctk.CTkButton(output_frame, text="Select Directory", command=self.browse_output, fg_color="#444444", hover_color="#666666", text_color="white", font=self.bold_font, corner_radius=20, width=140, height=36)
        btn_output.grid(row=1, column=1, padx=5, pady=5)
        output_frame.grid_columnconfigure(0, weight=1)
        output_frame.grid_columnconfigure(1, weight=0)

        # Scale factor
        scale_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        scale_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(scale_frame, text="Scale Settings", font=self.bold_font, anchor="w").pack(anchor="w", padx=5, pady=(5, 0))
        scale_inner = ctk.CTkFrame(scale_frame, fg_color="transparent")
        scale_inner.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(scale_inner, text="Scale Factor:", font=self.regular_font).pack(side="left")
        self.scale_factor = tk.DoubleVar(value=0.5)
        self.scale_slider = ctk.CTkSlider(scale_inner, from_=0.1, to=0.8, variable=self.scale_factor, command=self.on_slider_change, width=200)
        self.scale_slider.pack(side="left", padx=10)
        self.scale_value_label = ctk.CTkLabel(scale_inner, text="0.50", font=self.regular_font, width=40)
        self.scale_value_label.pack(side="left", padx=5)

        # Size estimator frame
        estimate_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        estimate_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(estimate_frame, text="Size Estimator", font=self.bold_font, anchor="w").pack(anchor="w", padx=5, pady=(5, 0))
        self.estimate_var = tk.StringVar(value="Load a file to see size estimate")
        ctk.CTkLabel(estimate_frame, textvariable=self.estimate_var, font=self.regular_font, anchor="w", wraplength=500).pack(fill="x", padx=5, pady=5)

        # Image information frame
        info_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        info_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(info_frame, text="Image Information", font=self.bold_font, anchor="w").pack(anchor="w", padx=5, pady=(5, 0))
        self.resolution_var = tk.StringVar(value="Resolution: Not loaded")
        ctk.CTkLabel(info_frame, textvariable=self.resolution_var, font=self.regular_font, anchor="w").pack(fill="x", padx=5, pady=2)
        self.filesize_var = tk.StringVar(value="File size: Not loaded")
        ctk.CTkLabel(info_frame, textvariable=self.filesize_var, font=self.regular_font, anchor="w").pack(fill="x", padx=5, pady=2)

        # Convert and Cancel buttons (side by side)
        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.pack(pady=25)
        self.convert_button = ctk.CTkButton(button_frame, text="Convert", command=self.convert, fg_color="#39FF14", hover_color="#6fff47", text_color="black", font=self.bold_font, corner_radius=20, width=180, height=44)
        self.convert_button.grid(row=0, column=0, padx=(0, 10))
        self.cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=self.cancel_conversion, fg_color="#444444", hover_color="#666666", text_color="white", font=self.bold_font, corner_radius=20, width=120, height=44, state="disabled")
        self.cancel_button.grid(row=0, column=1)

        # Progress bar
        self.progress = ctk.CTkProgressBar(self.main_frame, width=400)
        self.progress.pack(pady=15)
        self.progress.set(0)

        # Status label
        self.status_var = tk.StringVar(value="Ready")
        ctk.CTkLabel(self.main_frame, textvariable=self.status_var, font=self.regular_font, anchor="center").pack(fill="x", pady=(8, 18))

        # Store original image info for size estimation
        self.original_width = None
        self.original_height = None
        self.original_bands = None
        self.original_size = None

        self.cancel_requested = False

    def on_slider_change(self, value):
        # Round to nearest 0.05
        rounded_value = round(float(value) * 20) / 20
        self.scale_value_label.configure(text=f"{rounded_value:.2f}")
        self.scale_factor.set(rounded_value)
        self.update_size_estimate()

    def update_size_estimate(self, event=None):
        if not all([self.original_width, self.original_height, self.original_bands]):
            self.estimate_var.set("Load a file to see size estimate")
            return
        try:
            scale = self.scale_factor.get()
            if scale <= 0 or scale > 1:
                self.estimate_var.set("Scale factor must be between 0 and 1")
                return
            new_width = int(self.original_width * scale)
            new_height = int(self.original_height * scale)
            bytes_per_pixel = 4  # RGBA
            raw_size = new_width * new_height * bytes_per_pixel
            compression_ratio = 2  # PNG is often 2:1 or better
            estimated_size = raw_size / compression_ratio
            self.estimate_var.set(
                f"Expected output size: {new_width} x {new_height} pixels\n"
                f"Estimated file size: {format_size(estimated_size)}"
            )
        except Exception:
            self.estimate_var.set("Invalid scale factor")

    def browse_input(self):
        filename = filedialog.askopenfilename(
            filetypes=[("GeoTIFF files", "*.tif *.tiff"), ("All files", "*.*")]
        )
        if filename:
            self.input_path.set(filename)
            # Set default output directory to input file's directory
            self.output_path.set(os.path.dirname(filename))
            # Load and display image information
            self.load_image_info(filename)

    def browse_output(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_path.set(directory)

    def load_image_info(self, filename):
        try:
            with rasterio.open(filename) as src:
                # Store original dimensions for size estimation
                self.original_width = src.width
                self.original_height = src.height
                self.original_bands = src.count
                self.original_size = os.path.getsize(filename)
                
                # Get resolution
                resolution = f"Resolution: {src.width} x {src.height} pixels"
                self.resolution_var.set(resolution)
                
                # Get file size
                self.filesize_var.set(f"File size: {format_size(self.original_size)}")
                
                # Update size estimate
                self.update_size_estimate()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading image information: {str(e)}")
            self.resolution_var.set("Resolution: Error loading")
            self.filesize_var.set("File size: Error loading")
            self.estimate_var.set("Error loading file information")

    def update_progress(self, value):
        self.progress['value'] = value
        self.root.update_idletasks()
        self.root.update()

    def convert(self):
        input_file = self.input_path.get()
        output_dir = self.output_path.get()
        scale_factor = self.scale_factor.get()
        num_threads = os.cpu_count()

        if input_file == "No file selected" or output_dir == "No directory selected":
            messagebox.showerror("Error", "Please select input file and output directory")
            return

        self.status_var.set("Converting...")
        self.root.update_idletasks()
        self.progress.set(0)
        self.convert_button.configure(fg_color="#444444", hover_color="#666666", text_color="white", state="disabled")
        self.cancel_button.configure(state="normal", fg_color="#FF5E13", hover_color="#FF8C42")
        self.cancel_requested = False
        threading.Thread(target=self._convert_worker, args=(input_file, output_dir, scale_factor), daemon=True).start()

    def cancel_conversion(self):
        self.cancel_requested = True
        self.status_var.set("Cancelling...")
        self.root.update_idletasks()

    def _convert_worker(self, input_file, output_dir, scale_factor):
        try:
            with rasterio.open(input_file) as src:
                new_width = int(src.width * scale_factor)
                new_height = int(src.height * scale_factor)
                data = src.read()
                n_bands = data.shape[0]
                resized_data = np.zeros((n_bands, new_height, new_width), dtype=data.dtype)
                for i in range(n_bands):
                    if self.cancel_requested:
                        self.root.after(0, lambda: self.status_var.set("Conversion cancelled"))
                        self.root.after(0, lambda: self.progress.set(0))
                        self.root.after(0, lambda: self.convert_button.configure(fg_color="#39FF14", hover_color="#6fff47", text_color="black", state="normal"))
                        self.root.after(0, lambda: self.cancel_button.configure(state="disabled", fg_color="#444444", hover_color="#666666"))
                        return
                    resized_data[i] = process_band(data[i], new_width, new_height)
                    progress = (i + 1) / n_bands
                    self.root.after(0, lambda p=progress: self.progress.set(p))
                output_file = os.path.join(output_dir, os.path.splitext(os.path.basename(input_file))[0] + '.png')
                if data.dtype != np.uint8:
                    resized_data = ((resized_data - resized_data.min()) * (255.0 / (resized_data.max() - resized_data.min()))).astype(np.uint8)
                if resized_data.shape[0] == 1:
                    img = Image.fromarray(resized_data[0])
                elif resized_data.shape[0] == 3:
                    img = Image.fromarray(np.transpose(resized_data, (1, 2, 0)), mode='RGB')
                elif resized_data.shape[0] == 4:
                    img = Image.fromarray(np.transpose(resized_data, (1, 2, 0)), mode='RGBA')
                else:
                    img = Image.fromarray(resized_data[0])
                self.root.after(0, lambda: self.progress.set(0.95))
                img.save(output_file, optimize=True, compress_level=9)
                output_size = os.path.getsize(output_file)
                compression_ratio = self.original_size / output_size if output_size > 0 else 0
                self.root.after(0, lambda: self.progress.set(1.0))
                self.root.after(0, lambda: self.status_var.set("Conversion completed!"))
                self.root.after(0, lambda: self.convert_button.configure(fg_color="#39FF14", hover_color="#6fff47", text_color="black", state="normal"))
                self.root.after(0, lambda: self.cancel_button.configure(state="disabled", fg_color="#444444", hover_color="#666666"))
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success",
                    f"File converted and saved to:\n{output_file}\n\n"
                    f"Original size: {format_size(self.original_size)}\n"
                    f"Output size: {format_size(output_size)}\n"
                    f"Compression ratio: {compression_ratio:.1f}:1"
                ))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            self.root.after(0, lambda: self.status_var.set("Error occurred"))
            self.root.after(0, lambda: self.convert_button.configure(fg_color="#39FF14", hover_color="#6fff47", text_color="black", state="normal"))
            self.root.after(0, lambda: self.cancel_button.configure(state="disabled", fg_color="#444444", hover_color="#666666"))
        finally:
            self.root.after(0, lambda: self.progress.set(0))
            self.root.after(0, lambda: self.status_var.set("Ready"))

    def set_application_icon(self):
        """Set the application icon based on the operating system."""
        try:
            # Get the absolute path to the icons directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(current_dir, "assets", "icons")
            print(f"Looking for icons in: {icon_path}")  # Debug print
            
            if sys.platform == "darwin":  # macOS
                icon_file = os.path.join(icon_path, "icon.png")
                print(f"Loading macOS icon from: {icon_file}")  # Debug print
                if os.path.exists(icon_file):
                    icon = tk.PhotoImage(file=icon_file)
                    self.root.iconphoto(True, icon)
                else:
                    print(f"Icon file not found: {icon_file}")
            elif sys.platform == "win32":  # Windows
                icon_file = os.path.join(icon_path, "icon.ico")
                print(f"Loading Windows icon from: {icon_file}")  # Debug print
                if os.path.exists(icon_file):
                    self.root.iconbitmap(icon_file)
                else:
                    print(f"Icon file not found: {icon_file}")
            else:  # Linux and other Unix-like systems
                icon_file = os.path.join(icon_path, "icon.png")
                print(f"Loading Linux icon from: {icon_file}")  # Debug print
                if os.path.exists(icon_file):
                    icon = tk.PhotoImage(file=icon_file)
                    self.root.iconphoto(True, icon)
                else:
                    print(f"Icon file not found: {icon_file}")
        except Exception as e:
            print(f"Error loading application icon: {str(e)}")
            print(f"Current working directory: {os.getcwd()}")
            print(f"Platform: {sys.platform}")

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    root = ctk.CTk()
    root.title("GeoTIFF to PNG Converter")
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'icons', 'icon.png' if sys.platform == 'darwin' else 'icon.ico' if sys.platform == 'win32' else 'icon.png')
    if os.path.exists(icon_path):
        icon = tk.PhotoImage(file=icon_path)
        root.iconphoto(True, icon)
    app = GeoTiffConverter(root)
    root.mainloop()
