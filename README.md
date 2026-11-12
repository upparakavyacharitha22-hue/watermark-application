# Watermark Studio ✦

A modern, professional desktop image watermarking application built with **Python**, **Tkinter**, and **Pillow (PIL)**. Inspired by web tools like [Watermarkly](https://watermarkly.com/), **Watermark Studio** brings fast, privacy-friendly, offline batch and single-image watermarking right to your desktop with a sleek dark navy and purple UI.

---

## 📸 Overview

**Watermark Studio** allows photographers, content creators, and businesses to protect their visual work with highly customizable text and logo watermarks. The application renders watermarks in real-time onto a non-destructive viewport while preserving the original image's full resolution and quality upon export.

---

## ✨ Main Features

### 1. 📁 Image Upload & Viewport
- **Format Support:** Upload any `JPG`, `JPEG`, `PNG`, `WEBP`, or `BMP` image.
- **Aspect-Ratio Preservation:** Automatically scales preview to fit the application workspace without stretching, cropping, or distorting.
- **Non-Destructive:** The original image in memory is never modified.
- **Metadata Telemetry:** Displays file name, original dimensions (e.g., `1920 × 1080 px`), and file size in real-time.
- **Sample Image Included:** Click **"✦ Sample"** to instantly test with a bundled landscape photo.

### 2. ✍️ Text Watermark Customization
- **Custom Text:** Enter any copyright notice, brand name, or author handle.
- **Font Selection:** Choose from standard system fonts (`Segoe UI`, `Arial`, `Times New Roman`, `Calibri`, `Impact`, `Georgia`, `Courier New`, `Verdana`).
- **Font Size Slider:** Smoothly adjust text size from `12 px` to `140 px`.
- **Color Picker & Presets:** Native color picker dialog plus 6 instant one-click swatches (White, Black, Red, Gold, Cyan, Violet).
- **Opacity / Transparency:** Continuous slider from `5%` to `100%` transparency.
- **Rotation / Angle:** Rotate text anywhere between `-90°` and `+90°` (ideal for diagonal watermark stamps).
- **5-Point Alignment:** Position watermark at **Top Left**, **Top Right**, **Center**, **Bottom Left**, or **Bottom Right**.
- **Repeated Grid / Tiling:** Enable the **Tiled** checkbox to create a copyright protection grid across the entire image.
- **Margin / Padding:** Adjust distance from image borders (`5 px` to `120 px`).

### 3. 🖼️ Logo Watermark Customization
- **Logo Upload:** Load transparent `PNG` logos or other image files.
- **Proportional Scaling:** Scale the logo from `5%` to `70%` of the image width while strictly preserving its original aspect ratio.
- **Opacity / Transparency:** Adjust logo transparency from `5%` to `100%`.
- **5-Point Alignment & Tiling:** Position logo at any of the 5 positions or repeat across the whole canvas.
- **Sample Logo Included:** Click **"✦ Sample"** in the logo panel to test with the bundled transparent PNG logo.

### 4. 🎨 Multi-Mode Watermarking
- **✍ Text Mode:** Render text-only watermarks.
- **🖼 Logo Mode:** Render logo-only watermarks.
- **✨ Both Mode:** Combine text and logo simultaneously (e.g., logo in Top Left, copyright text in Bottom Right).

### 5. 👁️ Preview & Comparison
- **Live 60fps-like Debounced Preview:** Changes to text, sliders, colors, or positions update smoothly in real time.
- **Hold to View Original:** Click and hold the **"👁 Hold to View Original"** button in the top toolbar to instantly preview the unwatermarked image, and release to return.
- **Responsive Canvas:** Resizing or maximizing the window dynamically recalculates the preview fit.

### 6. 💾 High-Fidelity Export
- **Full-Resolution Export:** Applies watermarks mathematically to the full original resolution so exported files maintain 100% of their original sharpness and quality.
- **Format Choices:** Save as lossless **PNG** or optimized high-quality **JPEG (95%)**.
- **Safe Alpha Handling:** Converts RGBA to RGB with a clean background when exporting as JPEG.
- **Confirmation & Direct Folder Access:** Prompts to open the destination folder directly after saving.

### 7. 🔄 Reset & Error Handling
- **Reset All:** Clears active images, logos, and returns settings to sensible defaults with confirmation.
- **Error Resilience:** Gracefully catches unsupported formats, missing files, corrupted images, and invalid values with user-friendly dialogs.

---

## 🛠️ Technologies Used

| Technology | Purpose |
| :--- | :--- |
| **Python 3.10+ / 3.12** | Core programming language |
| **Tkinter** | Native Python desktop graphical user interface framework |
| **ttk (Themed Tk)** | Modern themed controls (sliders, scrollbars, comboboxes) |
| **Pillow (PIL) 10+** | High-performance image loading, alpha compositing, font rendering, and saving |

---

## 📂 Project Structure

```text
WatermarkStudio/
│
├── main.py              # Main desktop application source code
├── test_app.py          # Automated verification test suite
├── requirements.txt     # Python dependencies (Pillow)
├── README.md            # Comprehensive documentation & execution guide
└── assets/              # Bundled sample assets
    ├── sample_photo.jpg # High-resolution sample photo
    └── sample_logo.png  # Transparent PNG logo for quick testing
```

---

## 🚀 Installation & Execution

### Prerequisites
Make sure you have **Python 3.10 or newer** installed on your system.

### Step 1: Install Dependencies
Open your terminal (PowerShell, Command Prompt, or bash) in the project folder and run:

```bash
pip install -r requirements.txt
```

### Step 2: Run the Application
Execute the main entry point:

```bash
python main.py
```

---

## 💻 Running in IDEs

### Running in Visual Studio Code (VS Code)
1. Open **VS Code**.
2. Click **File > Open Folder...** and select the `watermarking application` (or `WatermarkStudio`) folder.
3. Open `main.py` in the editor.
4. Make sure your Python interpreter is selected in the bottom-right status bar (e.g., Python 3.12.x).
5. Press `F5` to start debugging, or click the **▷ Run Python File** button in the top-right corner.

### Running in PyCharm
1. Open **PyCharm**.
2. Click **Open** and select the project directory.
3. If prompted to create a virtual environment, choose Python 3.10+.
4. In the built-in terminal (`Alt + F12`), run:
   ```bash
   pip install -r requirements.txt
   ```
5. Right-click `main.py` in the Project Explorer tree and select **Run 'main'**.

---

## 🧪 Testing the Application

### 1. Automated Test Suite
Run the included test suite to verify all core capabilities headlessly:

```bash
python test_app.py
```

Expected output:
```text
======================================================================
STARTING WATERMARK STUDIO AUTOMATED TEST SUITE
======================================================================
[PASS] 1. WatermarkStudioApp initialized successfully.
[PASS] 2. Image loaded: 1200x800 px. Original image preserved in memory.
[PASS] 3. Text watermark (rotated, colored, custom opacity, centered) applied cleanly.
[PASS] 4. Repeated grid / tiled text watermark rendered successfully.
[PASS] 5. Transparent PNG logo watermark (scaled, translucent, Top Left) applied cleanly.
[PASS] 6. 'Both' mode (simultaneous Text + Logo) rendered successfully.
[PASS] 7. Export to PNG verified.
[PASS] 8. Export to JPEG verified.
[PASS] 9. Coordinate math for all 5 watermark positions verified.
[PASS] 10. Reset functionality verified.
======================================================================
ALL TESTS PASSED WITH 100% SUCCESS!
======================================================================
```

### 2. Manual Testing Checklist
1. **Upload Image:**
   - Click **"⬆ Upload Image"** and choose any photo, or click **"✦ Sample"** to load the bundled landscape photo.
   - Verify image dimensions, file size, and status chip update.
2. **Text Watermark:**
   - Type a custom watermark text (e.g., `© 2026 MyBrand Studio`).
   - Drag the **Font Size** slider to verify resizing.
   - Click **"Pick Color..."** or click one of the palette chips (e.g., Cyan or Gold) to change color.
   - Adjust the **Opacity** slider and **Rotation** slider.
   - Click each of the 5 position buttons (**Top Left**, **Top Right**, **Center**, **Bottom Left**, **Bottom Right**).
   - Check the **"Repeated Grid / Tiled"** box to test full-image tiling.
3. **Logo Watermark:**
   - Click **"🖼 Logo"** or **"✨ Both"** in the Watermark Type card.
   - Click **"⬆ Upload Logo (PNG)"** or **"✦ Sample"** to load the bundled transparent logo.
   - Adjust the **Logo Scale** slider, **Opacity** slider, and position.
4. **Compare Original:**
   - Press and hold **"👁 Hold to View Original"** on the toolbar to check before/after.
5. **Save Watermarked Image:**
   - Click **"💾 Save Watermarked Image"**.
   - Select destination folder and choose `.png` or `.jpg`.
   - Verify the success dialog appears with file size and dimension details.
6. **Reset:**
   - Click **"🔄 Reset All"**, confirm the dialog, and verify the workspace returns to the empty state.

---

## 🛡️ License & Credit
Developed as a clean, beginner-friendly yet production-grade desktop application for Python Tkinter project submissions.
Built with Python 3, Tkinter, and Pillow (PIL).

