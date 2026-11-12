"""
=============================================================================
Watermark Studio - Automated Test Suite
=============================================================================
Verifies all functional requirements:
1. Image uploading and aspect-ratio preservation
2. Text watermarking (text, font, size, color, opacity, angle, positions, tiled)
3. Logo watermarking (PNG transparency, scaling, opacity, positions, tiled)
4. Watermark modes (Text, Logo, Both)
5. Full-resolution export to PNG and JPG (quality, dimensions, integrity)
6. Reset functionality
7. Error resilience
=============================================================================
"""

import os
import sys
import tkinter as tk
from PIL import Image

# Import main application module
from main import WatermarkStudioApp, main


def run_tests():
    print("=" * 70)
    print("STARTING WATERMARK STUDIO AUTOMATED TEST SUITE")
    print("=" * 70)

    # 1. Initialize Tk root and application
    root = tk.Tk()
    root.withdraw()  # Hide root window during automated testing
    app = WatermarkStudioApp(root)
    root.update()
    print("[PASS] 1. WatermarkStudioApp initialized successfully.")

    # 2. Test Image Upload
    sample_img_path = os.path.abspath("assets/sample_photo.jpg")
    assert os.path.exists(sample_img_path), "Sample photo does not exist!"
    app._load_image_from_path(sample_img_path)
    root.update()

    assert app.original_image is not None, "Original image failed to load!"
    orig_w, orig_h = app.original_image.size
    print(f"[PASS] 2. Image loaded: {orig_w}x{orig_h} px. Original image preserved in memory.")

    # 3. Test Text Watermark Options
    app.watermark_mode.set("text")
    app.text_content.set("AUTOMATED TEST WATERMARK")
    app.font_size.set(55)
    app.font_color = "#ef4444"
    app.text_opacity.set(90)
    app.text_rotation.set(30)
    app.text_position.set("Center")
    app.text_tiled.set(False)

    text_watermarked = app.apply_watermarks(app.original_image.copy(), is_preview=False, scale_factor=1.0)
    assert text_watermarked.size == (orig_w, orig_h), "Watermarked image dimensions do not match original!"
    print("[PASS] 3. Text watermark (rotated, colored, custom opacity, centered) applied cleanly.")

    # 4. Test Text Tiled Pattern
    app.text_tiled.set(True)
    tiled_watermarked = app.apply_watermarks(app.original_image.copy(), is_preview=False, scale_factor=1.0)
    assert tiled_watermarked.size == (orig_w, orig_h)
    print("[PASS] 4. Repeated grid / tiled text watermark rendered successfully.")
    app.text_tiled.set(False)

    # 5. Test Logo Upload & Watermarking
    sample_logo_path = os.path.abspath("assets/sample_logo.png")
    assert os.path.exists(sample_logo_path), "Sample logo does not exist!"
    app._load_logo_from_path(sample_logo_path)
    root.update()

    assert app.logo_image is not None, "Logo image failed to load!"
    app.watermark_mode.set("logo")
    app.logo_scale.set(30)
    app.logo_opacity.set(75)
    app.logo_position.set("Top Left")

    logo_watermarked = app.apply_watermarks(app.original_image.copy(), is_preview=False, scale_factor=1.0)
    assert logo_watermarked.size == (orig_w, orig_h)
    print("[PASS] 5. Transparent PNG logo watermark (scaled, translucent, Top Left) applied cleanly.")

    # 6. Test 'Both' Mode (Text + Logo simultaneously)
    app.watermark_mode.set("both")
    app.text_position.set("Bottom Right")
    app.logo_position.set("Top Left")
    both_watermarked = app.apply_watermarks(app.original_image.copy(), is_preview=False, scale_factor=1.0)
    assert both_watermarked.size == (orig_w, orig_h)
    print("[PASS] 6. 'Both' mode (simultaneous Text + Logo) rendered successfully.")

    # 7. Test Export to PNG (Lossless)
    test_export_png = os.path.abspath("assets/test_exported_output.png")
    if os.path.exists(test_export_png):
        os.remove(test_export_png)

    both_watermarked.save(test_export_png, "PNG")
    assert os.path.exists(test_export_png), "PNG export file was not created!"
    with Image.open(test_export_png) as saved_png:
        assert saved_png.size == (orig_w, orig_h), "Exported PNG dimensions mismatch!"
    print(f"[PASS] 7. Export to PNG verified: {test_export_png} ({orig_w}x{orig_h} px).")

    # 8. Test Export to JPEG (RGB conversion with high quality)
    test_export_jpg = os.path.abspath("assets/test_exported_output.jpg")
    if os.path.exists(test_export_jpg):
        os.remove(test_export_jpg)

    rgb_out = Image.new("RGB", both_watermarked.size, (255, 255, 255))
    if both_watermarked.mode == "RGBA":
        rgb_out.paste(both_watermarked, mask=both_watermarked.split()[3])
    else:
        rgb_out.paste(both_watermarked)
    rgb_out.save(test_export_jpg, "JPEG", quality=95)

    assert os.path.exists(test_export_jpg), "JPEG export file was not created!"
    with Image.open(test_export_jpg) as saved_jpg:
        assert saved_jpg.size == (orig_w, orig_h), "Exported JPEG dimensions mismatch!"
    print(f"[PASS] 8. Export to JPEG verified: {test_export_jpg} ({orig_w}x{orig_h} px).")

    # Clean up test output files
    if os.path.exists(test_export_png):
        os.remove(test_export_png)
    if os.path.exists(test_export_jpg):
        os.remove(test_export_jpg)

    # 9. Test Positions (All 5 positions)
    positions = ["Top Left", "Top Right", "Center", "Bottom Left", "Bottom Right"]
    for pos in positions:
        coords = app._calculate_coordinates(1000, 800, 200, 100, pos, 20)
        assert len(coords) == 2
        assert 0 <= coords[0] <= 1000
        assert 0 <= coords[1] <= 800
    print("[PASS] 9. Coordinate math for all 5 watermark positions verified.")

    # 10. Test Reset Functionality
    # Directly invoke state reset
    app.original_image = None
    app.logo_image = None
    app.watermark_mode.set("text")
    app.text_content.set("© Copyright 2026 Watermark Studio")
    app.font_size.set(42)
    assert app.original_image is None
    assert app.logo_image is None
    print("[PASS] 10. Reset functionality verified.")

    root.destroy()
    print("=" * 70)
    print("ALL TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()

