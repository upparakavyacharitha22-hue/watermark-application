"""
=============================================================================
Watermark Studio - Desktop Image Watermarking Application
=============================================================================
A modern, professional desktop application built with Python Tkinter and
Pillow (PIL). Allows users to upload images, apply highly customizable text
and logo watermarks with real-time preview, and export high-resolution results.

Author: Watermark Studio Team
Environment: Python 3.x with Tkinter & Pillow (PIL)
=============================================================================
"""

import os
import sys
import math
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageFont


# =============================================================================
# High-DPI Display Awareness (Windows)
# =============================================================================
try:
    if sys.platform == "win32":
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass


# =============================================================================
# Color Palette & Styling Constants (Dark Navy & Purple Theme)
# =============================================================================
COLOR_BG_DARK = "#090d16"         # Primary deep dark navy background
COLOR_BG_SIDEBAR = "#0f172a"      # Elevated sidebar surface
COLOR_BG_CARD = "#1e293b"         # Card / container background
COLOR_BG_CARD_ALT = "#192238"     # Subtle contrasting card
COLOR_CANVAS_BG = "#070a10"       # Preview canvas background
COLOR_BORDER = "#334155"          # Subtle borders
COLOR_BORDER_LIGHT = "#475569"    # Hover / active borders

COLOR_PURPLE_PRIMARY = "#7c3aed"  # Vibrant purple accent (brand primary)
COLOR_PURPLE_HOVER = "#6d28d9"    # Button hover purple
COLOR_PURPLE_ACTIVE = "#5b21b6"   # Button active purple
COLOR_PURPLE_LIGHT = "#c4b5fd"    # Light lavender accent
COLOR_INDIGO_ACCENT = "#4f46e5"   # Secondary deep indigo

COLOR_TEXT_PRIMARY = "#f8fafc"    # Crisp high-contrast white text
COLOR_TEXT_SECONDARY = "#94a3b8"  # Soft slate secondary text
COLOR_TEXT_MUTED = "#64748b"      # Muted descriptions

COLOR_SUCCESS = "#10b981"         # Green success badge
COLOR_WARNING = "#f59e0b"         # Amber warning
COLOR_DANGER = "#ef4444"          # Red alert
COLOR_CYAN = "#06b6d4"            # Cyan highlight

FONT_FAMILY_TITLE = "Segoe UI"
FONT_FAMILY_UI = "Segoe UI"


# =============================================================================
# Main Application Class
# =============================================================================
class WatermarkStudioApp:
    """
    Main application controller for Watermark Studio.
    Manages GUI state, user interactions, PIL image processing,
    real-time preview generation, and high-fidelity file exports.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Watermark Studio - Professional Image Watermarking")
        self.root.geometry("1260x820")
        self.root.minsize(1020, 680)
        self.root.configure(bg=COLOR_BG_DARK)

        # ---------------------------------------------------------------------
        # Application State
        # ---------------------------------------------------------------------
        self.original_image: Image.Image | None = None
        self.original_image_path: str | None = None
        self.preview_image: Image.Image | None = None
        self.watermarked_preview_tk: ImageTk.PhotoImage | None = None

        self.logo_image: Image.Image | None = None
        self.logo_path: str | None = None

        # Mode: "text", "logo", or "both"
        self.watermark_mode = tk.StringVar(value="text")

        # Text Watermark Settings
        self.text_content = tk.StringVar(value="© Copyright 2026 Watermark Studio")
        self.font_family = tk.StringVar(value="Segoe UI")
        self.font_size = tk.IntVar(value=42)
        self.font_color = "#ffffff"
        self.text_opacity = tk.IntVar(value=80)      # 0 to 100%
        self.text_rotation = tk.IntVar(value=0)      # -180 to 180 degrees
        self.text_position = tk.StringVar(value="Bottom Right")
        self.text_padding = tk.IntVar(value=30)      # pixels relative to bounds
        self.text_tiled = tk.BooleanVar(value=False)

        # Logo Watermark Settings
        self.logo_scale = tk.IntVar(value=22)        # 5% to 75% of base image width
        self.logo_opacity = tk.IntVar(value=85)      # 0 to 100%
        self.logo_position = tk.StringVar(value="Top Right")
        self.logo_padding = tk.IntVar(value=30)
        self.logo_tiled = tk.BooleanVar(value=False)

        # Preview comparison state
        self.show_original_preview = tk.BooleanVar(value=False)

        # Debounce timer for smooth slider updates
        self._preview_debounce_id = None
        self._resize_debounce_id = None

        # Available fonts for text watermarking
        self.available_fonts = self._discover_available_fonts()

        # Build GUI
        self._setup_styles()
        self._build_header()
        self._build_main_layout()
        self._build_status_bar()

        # Canvas resize listener
        self.preview_canvas.bind("<Configure>", self._on_canvas_resize)

        # Try loading initial sample if available
        self._load_default_sample_if_present()

    # =========================================================================
    # Font Discovery Helper
    # =========================================================================
    def _discover_available_fonts(self) -> dict[str, str]:
        """Discovers standard system fonts for clean PIL rendering."""
        font_candidates = {
            "Segoe UI": ["segoeui.ttf", "segoeui"],
            "Arial": ["arial.ttf", "arial"],
            "Calibri": ["calibri.ttf", "calibri"],
            "Impact": ["impact.ttf", "impact"],
            "Times New Roman": ["times.ttf", "times"],
            "Georgia": ["georgia.ttf", "georgia"],
            "Courier New": ["cour.ttf", "cour"],
            "Verdana": ["verdana.ttf", "verdana"],
        }
        found_fonts: dict[str, str] = {}
        for display_name, filenames in font_candidates.items():
            for fname in filenames:
                try:
                    # Test if PIL can load this font
                    ImageFont.truetype(fname, 16)
                    found_fonts[display_name] = fname
                    break
                except Exception:
                    # Check C:/Windows/Fonts on Windows
                    win_path = os.path.join("C:\\Windows\\Fonts", fname if fname.endswith(".ttf") else f"{fname}.ttf")
                    if os.path.exists(win_path):
                        found_fonts[display_name] = win_path
                        break

        # Fallback guarantee
        if not found_fonts:
            found_fonts["Default Font"] = "default"
        return found_fonts

    def _get_pil_font(self, font_name: str, size: int) -> ImageFont.ImageFont | ImageFont.FreeTypeFont:
        """Returns a loaded PIL font with graceful fallback to default."""
        font_file = self.available_fonts.get(font_name)
        if font_file and font_file != "default":
            try:
                return ImageFont.truetype(font_file, max(8, int(size)))
            except Exception:
                pass
        try:
            return ImageFont.truetype("arial.ttf", max(8, int(size)))
        except Exception:
            return ImageFont.load_default()

    # =========================================================================
    # GUI Setup & Styles
    # =========================================================================
    def _setup_styles(self):
        """Initializes ttk styles matching the dark navy/purple theme."""
        style = ttk.Style()
        style.theme_use("clam")

        # Combobox style
        style.configure(
            "Dark.TCombobox",
            fieldbackground=COLOR_BG_CARD,
            background=COLOR_BG_CARD,
            foreground=COLOR_TEXT_PRIMARY,
            darkcolor=COLOR_BORDER,
            lightcolor=COLOR_BORDER,
            bordercolor=COLOR_BORDER,
            arrowcolor=COLOR_TEXT_PRIMARY,
            padding=5
        )
        style.map(
            "Dark.TCombobox",
            fieldbackground=[("readonly", COLOR_BG_CARD)],
            selectbackground=[("readonly", COLOR_PURPLE_PRIMARY)],
            selectforeground=[("readonly", COLOR_TEXT_PRIMARY)]
        )

        # Scale / Sliders
        style.configure(
            "Purple.Horizontal.TScale",
            troughcolor=COLOR_BG_DARK,
            background=COLOR_PURPLE_PRIMARY,
            sliderlength=18,
            sliderthickness=14,
            relief="flat",
            bordercolor=COLOR_BORDER
        )

        # Scrollbar
        style.configure(
            "Dark.Vertical.TScrollbar",
            troughcolor=COLOR_BG_SIDEBAR,
            background=COLOR_BORDER,
            arrowcolor=COLOR_TEXT_SECONDARY,
            bordercolor=COLOR_BG_SIDEBAR,
            relief="flat"
        )
        style.map(
            "Dark.Vertical.TScrollbar",
            background=[("active", COLOR_PURPLE_PRIMARY)]
        )

    def _build_header(self):
        """Builds modern top navigation / branding header."""
        header_frame = tk.Frame(self.root, bg=COLOR_BG_SIDEBAR, height=64)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        header_frame.pack_propagate(False)

        # Accent bottom line
        accent_line = tk.Frame(self.root, bg=COLOR_PURPLE_PRIMARY, height=2)
        accent_line.pack(side=tk.TOP, fill=tk.X)

        # Left branding
        brand_container = tk.Frame(header_frame, bg=COLOR_BG_SIDEBAR)
        brand_container.pack(side=tk.LEFT, padx=20, pady=8)

        # App Icon Badge
        icon_badge = tk.Label(
            brand_container,
            text=" ✦ ",
            font=(FONT_FAMILY_TITLE, 14, "bold"),
            bg=COLOR_PURPLE_PRIMARY,
            fg=COLOR_TEXT_PRIMARY,
            padx=4,
            pady=2
        )
        icon_badge.pack(side=tk.LEFT, padx=(0, 10))

        title_box = tk.Frame(brand_container, bg=COLOR_BG_SIDEBAR)
        title_box.pack(side=tk.LEFT)

        app_title = tk.Label(
            title_box,
            text="WATERMARK STUDIO",
            font=(FONT_FAMILY_TITLE, 14, "bold"),
            bg=COLOR_BG_SIDEBAR,
            fg=COLOR_TEXT_PRIMARY
        )
        app_title.pack(anchor="w")

        app_subtitle = tk.Label(
            title_box,
            text="Modern Desktop Image Watermarking & Branding Engine",
            font=(FONT_FAMILY_UI, 8),
            bg=COLOR_BG_SIDEBAR,
            fg=COLOR_TEXT_MUTED
        )
        app_subtitle.pack(anchor="w")

        # Right status chips
        right_chips = tk.Frame(header_frame, bg=COLOR_BG_SIDEBAR)
        right_chips.pack(side=tk.RIGHT, padx=20, pady=12)

        version_chip = tk.Label(
            right_chips,
            text="PRO v1.0",
            font=(FONT_FAMILY_UI, 8, "bold"),
            bg=COLOR_BG_CARD,
            fg=COLOR_PURPLE_LIGHT,
            padx=10,
            pady=4,
            relief="flat"
        )
        version_chip.pack(side=tk.RIGHT, padx=6)

        self.header_status_chip = tk.Label(
            right_chips,
            text="● Waiting for Image",
            font=(FONT_FAMILY_UI, 8, "bold"),
            bg=COLOR_BG_CARD,
            fg=COLOR_WARNING,
            padx=10,
            pady=4,
            relief="flat"
        )
        self.header_status_chip.pack(side=tk.RIGHT, padx=6)

    def _build_main_layout(self):
        """Constructs sidebar panel and preview workspace."""
        content_frame = tk.Frame(self.root, bg=COLOR_BG_DARK)
        content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Left Sidebar (Scrollable Canvas container)
        self._build_sidebar(content_frame)

        # Main Center Workspace (Preview)
        self._build_workspace(content_frame)

    def _build_sidebar(self, parent: tk.Frame):
        """Constructs scrollable sidebar containing all controls."""
        sidebar_outer = tk.Frame(parent, bg=COLOR_BG_SIDEBAR, width=420)
        sidebar_outer.pack(side=tk.LEFT, fill=tk.Y)
        sidebar_outer.pack_propagate(False)

        # Canvas for smooth scrolling
        sidebar_canvas = tk.Canvas(
            sidebar_outer,
            bg=COLOR_BG_SIDEBAR,
            highlightthickness=0,
            borderwidth=0
        )
        sidebar_scrollbar = ttk.Scrollbar(
            sidebar_outer,
            orient="vertical",
            command=sidebar_canvas.yview,
            style="Dark.Vertical.TScrollbar"
        )
        self.sidebar_frame = tk.Frame(sidebar_canvas, bg=COLOR_BG_SIDEBAR)

        self.sidebar_frame.bind(
            "<Configure>",
            lambda e: sidebar_canvas.configure(scrollregion=sidebar_canvas.bbox("all"))
        )
        canvas_window = sidebar_canvas.create_window((0, 0), window=self.sidebar_frame, anchor="nw")

        def _configure_sidebar_width(event):
            sidebar_canvas.itemconfig(canvas_window, width=event.width)
        sidebar_canvas.bind("<Configure>", _configure_sidebar_width)

        sidebar_canvas.configure(yscrollcommand=sidebar_scrollbar.set)

        sidebar_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sidebar_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Enable mousewheel scrolling on sidebar
        def _on_mousewheel(event):
            sidebar_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        sidebar_canvas.bind_all("<MouseWheel>", lambda event: self._bind_mousewheel_safely(event, sidebar_canvas))

        # Build Sidebar Cards
        self._build_image_source_card(self.sidebar_frame)
        self._build_watermark_mode_card(self.sidebar_frame)
        self._build_text_settings_card(self.sidebar_frame)
        self._build_logo_settings_card(self.sidebar_frame)
        self._build_export_card(self.sidebar_frame)

    def _bind_mousewheel_safely(self, event, canvas):
        """Handles mousewheel scrolling when hovering over sidebar widgets."""
        widget = event.widget
        # Only scroll sidebar if mouse is over sidebar or its children
        if str(widget).startswith(str(self.sidebar_frame)) or widget == canvas:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # =========================================================================
    # Sidebar Cards
    # =========================================================================
    def _create_card(self, parent: tk.Frame, title: str) -> tuple[tk.Frame, tk.Frame]:
        """Helper to create a visually cohesive card with header and body."""
        card_container = tk.Frame(parent, bg=COLOR_BG_CARD, padx=14, pady=12, highlightthickness=1, highlightbackground=COLOR_BORDER)
        card_container.pack(fill=tk.X, padx=12, pady=7)

        title_label = tk.Label(
            card_container,
            text=title,
            font=(FONT_FAMILY_TITLE, 10, "bold"),
            bg=COLOR_BG_CARD,
            fg=COLOR_TEXT_PRIMARY
        )
        title_label.pack(anchor="w", pady=(0, 8))

        body_frame = tk.Frame(card_container, bg=COLOR_BG_CARD)
        body_frame.pack(fill=tk.X)
        return card_container, body_frame

    def _build_image_source_card(self, parent: tk.Frame):
        """Card 1: Image Upload and Metadata Display."""
        _, body = self._create_card(parent, "📁 1. Source Image")

        btn_row = tk.Frame(body, bg=COLOR_BG_CARD)
        btn_row.pack(fill=tk.X, pady=(0, 8))

        # Upload Image button
        self.btn_upload = self._create_button(
            btn_row,
            text="⬆  Upload Image",
            command=self.upload_image,
            bg=COLOR_PURPLE_PRIMARY,
            hover_bg=COLOR_PURPLE_HOVER,
            fg=COLOR_TEXT_PRIMARY,
            bold=True
        )
        self.btn_upload.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        # Quick Sample button
        btn_sample = self._create_button(
            btn_row,
            text="✦ Sample",
            command=self.load_sample_image,
            bg=COLOR_BG_CARD_ALT,
            hover_bg=COLOR_BORDER,
            fg=COLOR_PURPLE_LIGHT,
            bold=False
        )
        btn_sample.pack(side=tk.RIGHT, padx=(4, 0))

        # Metadata info box
        self.info_box = tk.Frame(body, bg=COLOR_BG_DARK, padx=10, pady=8, highlightthickness=1, highlightbackground=COLOR_BORDER)
        self.info_box.pack(fill=tk.X)

        self.lbl_image_name = tk.Label(
            self.info_box,
            text="No image loaded",
            font=(FONT_FAMILY_UI, 9, "bold"),
            bg=COLOR_BG_DARK,
            fg=COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        self.lbl_image_name.pack(fill=tk.X)

        self.lbl_image_dims = tk.Label(
            self.info_box,
            text="Supported: JPG, JPEG, PNG",
            font=(FONT_FAMILY_UI, 8),
            bg=COLOR_BG_DARK,
            fg=COLOR_TEXT_MUTED,
            anchor="w"
        )
        self.lbl_image_dims.pack(fill=tk.X, pady=(2, 0))

    def _build_watermark_mode_card(self, parent: tk.Frame):
        """Card 2: Selector for Text / Logo / Both watermark mode."""
        _, body = self._create_card(parent, "🎨 2. Watermark Type")

        modes_frame = tk.Frame(body, bg=COLOR_BG_CARD)
        modes_frame.pack(fill=tk.X)

        modes = [
            ("✍  Text", "text"),
            ("🖼  Logo", "logo"),
            ("✨  Both", "both")
        ]

        self.mode_buttons = {}
        for idx, (label_text, mode_val) in enumerate(modes):
            btn = tk.Button(
                modes_frame,
                text=label_text,
                font=(FONT_FAMILY_UI, 9, "bold"),
                bg=COLOR_PURPLE_PRIMARY if self.watermark_mode.get() == mode_val else COLOR_BG_DARK,
                fg=COLOR_TEXT_PRIMARY,
                activebackground=COLOR_PURPLE_HOVER,
                activeforeground=COLOR_TEXT_PRIMARY,
                relief="flat",
                bd=0,
                padx=8,
                pady=7,
                cursor="hand2",
                command=lambda m=mode_val: self._on_mode_change(m)
            )
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
            self.mode_buttons[mode_val] = btn

    def _on_mode_change(self, new_mode: str):
        """Handles switching between Text, Logo, and Both watermark modes."""
        self.watermark_mode.set(new_mode)
        for m_val, btn in self.mode_buttons.items():
            if m_val == new_mode:
                btn.configure(bg=COLOR_PURPLE_PRIMARY, fg=COLOR_TEXT_PRIMARY)
            else:
                btn.configure(bg=COLOR_BG_DARK, fg=COLOR_TEXT_SECONDARY)
        self._update_cards_visibility()
        self.schedule_preview_update()

    def _update_cards_visibility(self):
        """Toggles visual emphasis on active cards."""
        mode = self.watermark_mode.get()
        if mode in ("text", "both"):
            self.text_card_container.configure(highlightbackground=COLOR_PURPLE_PRIMARY)
        else:
            self.text_card_container.configure(highlightbackground=COLOR_BORDER)

        if mode in ("logo", "both"):
            self.logo_card_container.configure(highlightbackground=COLOR_PURPLE_PRIMARY)
        else:
            self.logo_card_container.configure(highlightbackground=COLOR_BORDER)

    def _build_text_settings_card(self, parent: tk.Frame):
        """Card 3: Text Watermark controls (text, font, size, color, opacity, position)."""
        self.text_card_container, body = self._create_card(parent, "✍ 3. Text Watermark Settings")
        self.text_card_container.configure(highlightbackground=COLOR_PURPLE_PRIMARY)

        # Text input
        tk.Label(
            body,
            text="Watermark Text",
            font=(FONT_FAMILY_UI, 8, "bold"),
            bg=COLOR_BG_CARD,
            fg=COLOR_TEXT_SECONDARY
        ).pack(anchor="w")

        text_entry = tk.Entry(
            body,
            textvariable=self.text_content,
            font=(FONT_FAMILY_UI, 10),
            bg=COLOR_BG_DARK,
            fg=COLOR_TEXT_PRIMARY,
            insertbackground=COLOR_TEXT_PRIMARY,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=COLOR_BORDER,
            highlightcolor=COLOR_PURPLE_PRIMARY
        )
        text_entry.pack(fill=tk.X, pady=(2, 8), ipady=5)
        text_entry.bind("<KeyRelease>", lambda e: self.schedule_preview_update())

        # Font & Size Row
        row_font = tk.Frame(body, bg=COLOR_BG_CARD)
        row_font.pack(fill=tk.X, pady=(0, 8))

        # Font dropdown
        col_font = tk.Frame(row_font, bg=COLOR_BG_CARD)
        col_font.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        tk.Label(
            col_font,
            text="Font Family",
            font=(FONT_FAMILY_UI, 8, "bold"),
            bg=COLOR_BG_CARD,
            fg=COLOR_TEXT_SECONDARY
        ).pack(anchor="w")

        font_names = list(self.available_fonts.keys())
        combo_font = ttk.Combobox(
            col_font,
            textvariable=self.font_family,
            values=font_names,
            state="readonly",
            style="Dark.TCombobox"
        )
        combo_font.pack(fill=tk.X, pady=(2, 0))
        combo_font.bind("<<ComboboxSelected>>", lambda e: self.schedule_preview_update())

        # Font Size Slider
        col_size = tk.Frame(row_font, bg=COLOR_BG_CARD)
        col_size.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(4, 0))

        self.lbl_font_size = tk.Label(
            col_size,
            text=f"Font Size: {self.font_size.get()} px",
            font=(FONT_FAMILY_UI, 8, "bold"),
            bg=COLOR_BG_CARD,
            fg=COLOR_TEXT_SECONDARY
        )
        self.lbl_font_size.pack(anchor="w")

        slider_size = ttk.Scale(
            col_size,
            from_=12,
            to=140,
            orient="horizontal",
            variable=self.font_size,
            style="Purple.Horizontal.TScale",
            command=self._on_font_size_slider
        )
        slider_size.pack(fill=tk.X, pady=(2, 0))

        # Color & Quick Swatches Row
        color_row = tk.Frame(body, bg=COLOR_BG_CARD)
        color_row.pack(fill=tk.X, pady=(0, 8))

        tk.Label(
            color_row,
            text="Font Color",
            font=(FONT_FAMILY_UI, 8, "bold"),
            bg=COLOR_BG_CARD,
            fg=COLOR_TEXT_SECONDARY
        ).pack(anchor="w")

        swatch_frame = tk.Frame(color_row, bg=COLOR_BG_CARD)
        swatch_frame.pack(fill=tk.X, pady=(3, 0))

        # Active color preview chip
        self.color_swatch = tk.Label(
            swatch_frame,
            bg=self.font_color,
            width=4,
            height=1,
            relief="ridge",
            bd=1,
            highlightthickness=1,
            highlightbackground=COLOR_BORDER
        )
        self.color_swatch.pack(side=tk.LEFT, padx=(0, 8))

        btn_color = self._create_button(
            swatch_frame,
            text="Pick Color...",
            command=self._pick_text_color,
            bg=COLOR_BG_CARD_ALT,
            hover_bg=COLOR_BORDER,
            fg=COLOR_TEXT_PRIMARY,
            bold=False
        )
        btn_color.pack(side=tk.LEFT, padx=(0, 10))

        # Preset palette chips
        presets = ["#ffffff", "#000000", "#ef4444", "#f59e0b", "#06b6d4", "#a855f7"]
        for c in presets:
            sw = tk.Button(
                swatch_frame,
                bg=c,
                width=2,
                height=1,
                relief="flat",
                bd=0,
                cursor="hand2",
                command=lambda clr=c: self._set_text_color(clr)
            )
            sw.pack(side=tk.LEFT, padx=2)

        # Opacity Slider
        opacity_row = tk.Frame(body, bg=COLOR_BG_CARD)
        opacity_row.pack(fill=tk.X, pady=(0, 8))

        self.lbl_text_opacity = tk.Label(
            opacity_row,
            text=f"Opacity: {self.text_opacity.get()}%",
            font=(FONT_FAMILY_UI, 8, "bold"),
            bg=COLOR_BG_CARD,
            fg=COLOR_TEXT_SECONDARY
        )
        self.lbl_text_opacity.pack(anchor="w")

        slider_text_op = ttk.Scale(
            opacity_row,
            from_=5,
            to=100,
            orient="horizontal",
            variable=self.text_opacity,
            style="Purple.Horizontal.TScale",
            command=self._on_text_opacity_slider
        )
        slider_text_op.pack(fill=tk.X, pady=(2, 0))

        # Rotation Slider
        rotation_row = tk.Frame(body, bg=COLOR_BG_CARD)
        rotation_row.pack(fill=tk.X, pady=(0, 8))

        self.lbl_text_rotation = tk.Label(
            rotation_row,
            text=f"Angle / Rotation: {self.text_rotation.get()}°",
            font=(FONT_FAMILY_UI, 8, "bold"),
            bg=COLOR_BG_CARD,
            fg=COLOR_TEXT_SECONDARY
        )
        self.lbl_text_rotation.pack(anchor="w")

        slider_rotation = ttk.Scale(
            rotation_row,
            from_=-90,
            to=90,
            orient="horizontal",
            variable=self.text_rotation,
            style="Purple.Horizontal.TScale",
            command=self._on_text_rotation_slider
        )
        slider_rotation.pack(fill=tk.X, pady=(2, 0))

        # Position Selection Grid
        pos_header = tk.Frame(body, bg=COLOR_BG_CARD)
        pos_header.pack(fill=tk.X, pady=(0, 4))

        tk.Label(
            pos_header,
            text="Text Position",
            font=(FONT_FAMILY_UI, 8, "bold"),
            bg=COLOR_BG_CARD,
            fg=COLOR_TEXT_SECONDARY
        ).pack(side=tk.LEFT)

        # Tiled pattern checkbox
        chk_tiled = tk.Checkbutton(
            pos_header,
            text="Repeated Grid / Tiled",
            variable=self.text_tiled,
            font=(FONT_FAMILY_UI, 8),
            bg=COLOR_BG_CARD,
            fg=COLOR_CYAN,
            selectcolor=COLOR_BG_DARK,
            activebackground=COLOR_BG_CARD,
            activeforeground=COLOR_CYAN,
            command=self.schedule_preview_update
        )
        chk_tiled.pack(side=tk.RIGHT)

        pos_grid = tk.Frame(body, bg=COLOR_BG_CARD)
        pos_grid.pack(fill=tk.X, pady=(0, 6))

        positions = [
            ("Top Left", 0, 0),
            ("Center", 0, 1),
            ("Top Right", 0, 2),
            ("Bottom Left", 1, 0),
            ("Bottom Right", 1, 2)
        ]

        self.text_pos_buttons = {}
        for pos_name, r, c in positions:
            p_btn = tk.Button(
                pos_grid,
                text=pos_name,
                font=(FONT_FAMILY_UI, 8, "bold"),
                bg=COLOR_PURPLE_PRIMARY if self.text_position.get() == pos_name else COLOR_BG_DARK,
                fg=COLOR_TEXT_PRIMARY,
                relief="flat",
                bd=0,
                padx=6,
                pady=5,
                cursor="hand2",
                command=lambda p=pos_name: self._set_text_position(p)
            )
            p_btn.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")
            pos_grid.grid_columnconfigure(c, weight=1)
            self.text_pos_buttons[pos_name] = p_btn

        # Padding / Offset Slider
        padding_row = tk.Frame(body, bg=COLOR_BG_CARD)
        padding_row.pack(fill=tk.X)

        self.lbl_text_padding = tk.Label(
            padding_row,
            text=f"Margin / Padding: {self.text_padding.get()} px",
            font=(FONT_FAMILY_UI, 8, "bold"),
            bg=COLOR_BG_CARD,
            fg=COLOR_TEXT_SECONDARY
        )
        self.lbl_text_padding.pack(anchor="w")

        slider_pad = ttk.Scale(
            padding_row,
            from_=5,
            to=120,
            orient="horizontal",
            variable=self.text_padding,
            style="Purple.Horizontal.TScale",
            command=self._on_text_padding_slider
        )
        slider_pad.pack(fill=tk.X, pady=(2, 0))

    def _on_font_size_slider(self, val):
        self.lbl_font_size.configure(text=f"Font Size: {int(float(val))} px")
        self.schedule_preview_update()

    def _on_text_opacity_slider(self, val):
        self.lbl_text_opacity.configure(text=f"Opacity: {int(float(val))}%")
        self.schedule_preview_update()

    def _on_text_rotation_slider(self, val):
        self.lbl_text_rotation.configure(text=f"Angle / Rotation: {int(float(val))}°")
        self.schedule_preview_update()

    def _on_text_padding_slider(self, val):
        self.lbl_text_padding.configure(text=f"Margin / Padding: {int(float(val))} px")
        self.schedule_preview_update()

    def _pick_text_color(self):
        """Opens native color chooser dialog."""
        _, hex_code = colorchooser.askcolor(color=self.font_color, title="Select Watermark Text Color")
        if hex_code:
            self._set_text_color(hex_code)

    def _set_text_color(self, hex_code: str):
        """Updates text color swatch and triggers preview refresh."""
        self.font_color = hex_code
        self.color_swatch.configure(bg=hex_code)
        self.schedule_preview_update()

    def _set_text_position(self, pos_name: str):
        """Sets text watermark position."""
        self.text_position.set(pos_name)
        for name, btn in self.text_pos_buttons.items():
            if name == pos_name:
                btn.configure(bg=COLOR_PURPLE_PRIMARY, fg=COLOR_TEXT_PRIMARY)
            else:
                btn.configure(bg=COLOR_BG_DARK, fg=COLOR_TEXT_SECONDARY)
        self.schedule_preview_update()

    def _build_logo_settings_card(self, parent: tk.Frame):
        """Card 4: Logo Watermark controls (upload logo, scale, opacity, position)."""
        self.logo_card_container, body = self._create_card(parent, "🖼 4. Logo Watermark Settings")

        logo_btn_row = tk.Frame(body, bg=COLOR_BG_CARD)
        logo_btn_row.pack(fill=tk.X, pady=(0, 8))

        btn_upload_logo = self._create_button(
            logo_btn_row,
            text="⬆  Upload Logo (PNG)",
            command=self.upload_logo,
            bg=COLOR_INDIGO_ACCENT,
            hover_bg=COLOR_PURPLE_HOVER,
            fg=COLOR_TEXT_PRIMARY,
            bold=True
        )
        btn_upload_logo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        btn_sample_logo = self._create_button(
            logo_btn_row,
            text="✦ Sample",
            command=self.load_sample_logo,
            bg=COLOR_BG_CARD_ALT,
            hover_bg=COLOR_BORDER,
            fg=COLOR_PURPLE_LIGHT,
            bold=False
        )
        btn_sample_logo.pack(side=tk.RIGHT, padx=(4, 0))

        # Logo status info
        self.lbl_logo_info = tk.Label(
            body,
            text="No logo selected (PNG with transparency recommended)",
            font=(FONT_FAMILY_UI, 8),
            bg=COLOR_BG_DARK,
            fg=COLOR_TEXT_MUTED,
            padx=8,
            pady=5,
            anchor="w",
            highlightthickness=1,
            highlightbackground=COLOR_BORDER
        )
        self.lbl_logo_info.pack(fill=tk.X, pady=(0, 8))

        # Logo Scale Slider
        scale_row = tk.Frame(body, bg=COLOR_BG_CARD)
        scale_row.pack(fill=tk.X, pady=(0, 8))

        self.lbl_logo_scale = tk.Label(
            scale_row,
            text=f"Logo Scale: {self.logo_scale.get()}% of width",
            font=(FONT_FAMILY_UI, 8, "bold"),
            bg=COLOR_BG_CARD,
            fg=COLOR_TEXT_SECONDARY
        )
        self.lbl_logo_scale.pack(anchor="w")

        slider_scale = ttk.Scale(
            scale_row,
            from_=5,
            to=70,
            orient="horizontal",
            variable=self.logo_scale,
            style="Purple.Horizontal.TScale",
            command=self._on_logo_scale_slider
        )
        slider_scale.pack(fill=tk.X, pady=(2, 0))

        # Logo Opacity Slider
        logo_op_row = tk.Frame(body, bg=COLOR_BG_CARD)
        logo_op_row.pack(fill=tk.X, pady=(0, 8))

        self.lbl_logo_opacity = tk.Label(
            logo_op_row,
            text=f"Logo Opacity: {self.logo_opacity.get()}%",
            font=(FONT_FAMILY_UI, 8, "bold"),
            bg=COLOR_BG_CARD,
            fg=COLOR_TEXT_SECONDARY
        )
        self.lbl_logo_opacity.pack(anchor="w")

        slider_logo_op = ttk.Scale(
            logo_op_row,
            from_=5,
            to=100,
            orient="horizontal",
            variable=self.logo_opacity,
            style="Purple.Horizontal.TScale",
            command=self._on_logo_opacity_slider
        )
        slider_logo_op.pack(fill=tk.X, pady=(2, 0))

        # Logo Position Grid
        pos_logo_header = tk.Frame(body, bg=COLOR_BG_CARD)
        pos_logo_header.pack(fill=tk.X, pady=(0, 4))

        tk.Label(
            pos_logo_header,
            text="Logo Position",
            font=(FONT_FAMILY_UI, 8, "bold"),
            bg=COLOR_BG_CARD,
            fg=COLOR_TEXT_SECONDARY
        ).pack(side=tk.LEFT)

        chk_logo_tiled = tk.Checkbutton(
            pos_logo_header,
            text="Repeated Grid / Tiled",
            variable=self.logo_tiled,
            font=(FONT_FAMILY_UI, 8),
            bg=COLOR_BG_CARD,
            fg=COLOR_CYAN,
            selectcolor=COLOR_BG_DARK,
            activebackground=COLOR_BG_CARD,
            activeforeground=COLOR_CYAN,
            command=self.schedule_preview_update
        )
        chk_logo_tiled.pack(side=tk.RIGHT)

        logo_pos_grid = tk.Frame(body, bg=COLOR_BG_CARD)
        logo_pos_grid.pack(fill=tk.X, pady=(0, 6))

        positions = [
            ("Top Left", 0, 0),
            ("Center", 0, 1),
            ("Top Right", 0, 2),
            ("Bottom Left", 1, 0),
            ("Bottom Right", 1, 2)
        ]

        self.logo_pos_buttons = {}
        for pos_name, r, c in positions:
            p_btn = tk.Button(
                logo_pos_grid,
                text=pos_name,
                font=(FONT_FAMILY_UI, 8, "bold"),
                bg=COLOR_PURPLE_PRIMARY if self.logo_position.get() == pos_name else COLOR_BG_DARK,
                fg=COLOR_TEXT_PRIMARY,
                relief="flat",
                bd=0,
                padx=6,
                pady=5,
                cursor="hand2",
                command=lambda p=pos_name: self._set_logo_position(p)
            )
            p_btn.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")
            logo_pos_grid.grid_columnconfigure(c, weight=1)
            self.logo_pos_buttons[pos_name] = p_btn

        # Logo Margin / Padding Slider
        logo_padding_row = tk.Frame(body, bg=COLOR_BG_CARD)
        logo_padding_row.pack(fill=tk.X)

        self.lbl_logo_padding = tk.Label(
            logo_padding_row,
            text=f"Margin / Padding: {self.logo_padding.get()} px",
            font=(FONT_FAMILY_UI, 8, "bold"),
            bg=COLOR_BG_CARD,
            fg=COLOR_TEXT_SECONDARY
        )
        self.lbl_logo_padding.pack(anchor="w")

        slider_logo_pad = ttk.Scale(
            logo_padding_row,
            from_=5,
            to=120,
            orient="horizontal",
            variable=self.logo_padding,
            style="Purple.Horizontal.TScale",
            command=self._on_logo_padding_slider
        )
        slider_logo_pad.pack(fill=tk.X, pady=(2, 0))

    def _on_logo_scale_slider(self, val):
        self.lbl_logo_scale.configure(text=f"Logo Scale: {int(float(val))}% of width")
        self.schedule_preview_update()

    def _on_logo_opacity_slider(self, val):
        self.lbl_logo_opacity.configure(text=f"Logo Opacity: {int(float(val))}%")
        self.schedule_preview_update()

    def _on_logo_padding_slider(self, val):
        self.lbl_logo_padding.configure(text=f"Margin / Padding: {int(float(val))} px")
        self.schedule_preview_update()

    def _set_logo_position(self, pos_name: str):
        """Sets logo watermark position."""
        self.logo_position.set(pos_name)
        for name, btn in self.logo_pos_buttons.items():
            if name == pos_name:
                btn.configure(bg=COLOR_PURPLE_PRIMARY, fg=COLOR_TEXT_PRIMARY)
            else:
                btn.configure(bg=COLOR_BG_DARK, fg=COLOR_TEXT_SECONDARY)
        self.schedule_preview_update()

    def _build_export_card(self, parent: tk.Frame):
        """Card 5: Save Watermarked Image and Reset."""
        _, body = self._create_card(parent, "💾 5. Save & Actions")

        # Save Button (Prominent Purple Gradient styling)
        self.btn_save = self._create_button(
            body,
            text="💾  Save Watermarked Image",
            command=self.save_watermarked_image,
            bg=COLOR_PURPLE_PRIMARY,
            hover_bg=COLOR_PURPLE_HOVER,
            fg=COLOR_TEXT_PRIMARY,
            bold=True,
            pady=10
        )
        self.btn_save.pack(fill=tk.X, pady=(0, 6))

        # Reset button
        btn_reset = self._create_button(
            body,
            text="🔄  Reset All",
            command=self.reset_all,
            bg=COLOR_BG_CARD_ALT,
            hover_bg=COLOR_BORDER,
            fg=COLOR_DANGER,
            bold=False,
            pady=6
        )
        btn_reset.pack(fill=tk.X)

    # =========================================================================
    # Workspace & Preview Canvas
    # =========================================================================
    def _build_workspace(self, parent: tk.Frame):
        """Constructs center workspace containing toolbar and interactive canvas."""
        workspace = tk.Frame(parent, bg=COLOR_BG_DARK)
        workspace.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Toolbar above canvas
        toolbar = tk.Frame(workspace, bg=COLOR_BG_CARD, height=44, highlightthickness=1, highlightbackground=COLOR_BORDER)
        toolbar.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        toolbar.pack_propagate(False)

        # Title / Mode label
        tk.Label(
            toolbar,
            text="PREVIEW WORKSPACE",
            font=(FONT_FAMILY_TITLE, 9, "bold"),
            bg=COLOR_BG_CARD,
            fg=COLOR_PURPLE_LIGHT
        ).pack(side=tk.LEFT, padx=14)

        # Compare toggle button
        self.btn_compare = tk.Button(
            toolbar,
            text="👁  Hold to View Original",
            font=(FONT_FAMILY_UI, 8, "bold"),
            bg=COLOR_BG_DARK,
            fg=COLOR_TEXT_SECONDARY,
            activebackground=COLOR_PURPLE_PRIMARY,
            activeforeground=COLOR_TEXT_PRIMARY,
            relief="flat",
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2"
        )
        self.btn_compare.pack(side=tk.LEFT, padx=8)
        self.btn_compare.bind("<ButtonPress-1>", self._on_compare_press)
        self.btn_compare.bind("<ButtonRelease-1>", self._on_compare_release)

        # Right side info indicators
        self.lbl_preview_scale = tk.Label(
            toolbar,
            text="Fit: 100%",
            font=(FONT_FAMILY_UI, 8),
            bg=COLOR_BG_CARD,
            fg=COLOR_TEXT_MUTED
        )
        self.lbl_preview_scale.pack(side=tk.RIGHT, padx=14)

        self.lbl_preview_dims = tk.Label(
            toolbar,
            text="No Image Loaded",
            font=(FONT_FAMILY_UI, 8, "bold"),
            bg=COLOR_BG_CARD,
            fg=COLOR_CYAN
        )
        self.lbl_preview_dims.pack(side=tk.RIGHT, padx=10)

        # Main Canvas with dark backdrop
        canvas_container = tk.Frame(workspace, bg=COLOR_CANVAS_BG, highlightthickness=1, highlightbackground=COLOR_BORDER)
        canvas_container.pack(fill=tk.BOTH, expand=True)

        self.preview_canvas = tk.Canvas(
            canvas_container,
            bg=COLOR_CANVAS_BG,
            highlightthickness=0,
            borderwidth=0
        )
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)

        # Draw empty state placeholder
        self._render_empty_state()

    def _render_empty_state(self):
        """Displays modern placeholder graphics when no image is loaded."""
        self.preview_canvas.delete("all")
        w = max(400, self.preview_canvas.winfo_width())
        h = max(300, self.preview_canvas.winfo_height())
        cx, cy = w // 2, h // 2

        # Draw decorative card
        card_w, card_h = 440, 260
        x1, y1 = cx - card_w // 2, cy - card_h // 2
        x2, y2 = cx + card_w // 2, cy + card_h // 2

        # Dashed container box
        self.preview_canvas.create_rectangle(
            x1, y1, x2, y2,
            outline=COLOR_BORDER,
            dash=(6, 4),
            width=2,
            fill=COLOR_BG_SIDEBAR
        )

        # Icon
        self.preview_canvas.create_text(
            cx, cy - 50,
            text="📸",
            font=(FONT_FAMILY_TITLE, 36),
            fill=COLOR_PURPLE_LIGHT
        )

        # Main message
        self.preview_canvas.create_text(
            cx, cy + 10,
            text="No Image Uploaded Yet",
            font=(FONT_FAMILY_TITLE, 14, "bold"),
            fill=COLOR_TEXT_PRIMARY
        )

        # Subtitle instructions
        self.preview_canvas.create_text(
            cx, cy + 42,
            text="Click 'Upload Image' or '✦ Sample' on the sidebar to begin.\nAdd custom text or your transparent logo watermark in real-time.",
            font=(FONT_FAMILY_UI, 9),
            fill=COLOR_TEXT_MUTED,
            justify=tk.CENTER
        )

        # Supported badges
        self.preview_canvas.create_text(
            cx, cy + 85,
            text="JPG  •  JPEG  •  PNG  •  WEBP  •  BMP",
            font=(FONT_FAMILY_UI, 8, "bold"),
            fill=COLOR_CYAN
        )

    def _on_compare_press(self, event):
        """Temporarily shows the original unwatermarked image."""
        if self.original_image is not None:
            self.show_original_preview.set(True)
            self.btn_compare.configure(bg=COLOR_PURPLE_PRIMARY, fg=COLOR_TEXT_PRIMARY)
            self._render_preview()

    def _on_compare_release(self, event):
        """Restores the watermarked preview upon releasing button."""
        if self.original_image is not None:
            self.show_original_preview.set(False)
            self.btn_compare.configure(bg=COLOR_BG_DARK, fg=COLOR_TEXT_SECONDARY)
            self._render_preview()

    # =========================================================================
    # Status Bar
    # =========================================================================
    def _build_status_bar(self):
        """Bottom application status and telemetry bar."""
        status_bar = tk.Frame(self.root, bg=COLOR_BG_SIDEBAR, height=26, highlightthickness=1, highlightbackground=COLOR_BORDER)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        status_bar.pack_propagate(False)

        self.lbl_status = tk.Label(
            status_bar,
            text=" Ready",
            font=(FONT_FAMILY_UI, 8),
            bg=COLOR_BG_SIDEBAR,
            fg=COLOR_TEXT_SECONDARY
        )
        self.lbl_status.pack(side=tk.LEFT, padx=12)

        sys_info = tk.Label(
            status_bar,
            text="Python 3.12 • Tkinter & Pillow Engine ",
            font=(FONT_FAMILY_UI, 8),
            bg=COLOR_BG_SIDEBAR,
            fg=COLOR_TEXT_MUTED
        )
        sys_info.pack(side=tk.RIGHT, padx=12)

    def set_status(self, message: str, is_error: bool = False):
        """Updates the status bar text."""
        color = COLOR_DANGER if is_error else COLOR_TEXT_SECONDARY
        self.lbl_status.configure(text=f" {'⚠' if is_error else '●'} {message}", fg=color)

    # =========================================================================
    # UI Utility Helpers
    # =========================================================================
    def _create_button(
        self,
        parent: tk.Frame,
        text: str,
        command,
        bg: str = COLOR_BG_CARD,
        hover_bg: str = COLOR_BORDER,
        fg: str = COLOR_TEXT_PRIMARY,
        bold: bool = False,
        pady: int = 6
    ) -> tk.Button:
        """Helper to create polished modern flat buttons with hover effects."""
        weight = "bold" if bold else "normal"
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=(FONT_FAMILY_UI, 9, weight),
            bg=bg,
            fg=fg,
            activebackground=hover_bg,
            activeforeground=fg,
            relief="flat",
            bd=0,
            padx=10,
            pady=pady,
            cursor="hand2"
        )

        def _on_enter(e):
            btn.configure(bg=hover_bg)

        def _on_leave(e):
            btn.configure(bg=bg)

        btn.bind("<Enter>", _on_enter)
        btn.bind("<Leave>", _on_leave)
        return btn

    # =========================================================================
    # Image Upload & Management Functions
    # =========================================================================
    def upload_image(self):
        """
        Prompts user to select an image (JPG, JPEG, PNG, WEBP, BMP).
        Loads the image into memory while preserving original resolution.
        """
        file_types = [
            ("Supported Images", "*.jpg *.jpeg *.png *.webp *.bmp"),
            ("PNG Images", "*.png"),
            ("JPEG Images", "*.jpg *.jpeg"),
            ("All Files", "*.*")
        ]
        file_path = filedialog.askopenfilename(
            title="Select Image to Watermark",
            filetypes=file_types
        )
        if not file_path:
            return

        self._load_image_from_path(file_path)

    def _load_image_from_path(self, file_path: str):
        """Loads and validates an image from disk."""
        try:
            loaded_img = Image.open(file_path)
            # Verify image can be parsed
            loaded_img.verify()
            # Reopen after verify() closes the file
            self.original_image = Image.open(file_path)
            self.original_image_path = file_path

            # Update info labels
            orig_w, orig_h = self.original_image.size
            file_name = os.path.basename(file_path)
            file_size_kb = os.path.getsize(file_path) / 1024
            size_str = f"{file_size_kb:.1f} KB" if file_size_kb < 1024 else f"{(file_size_kb / 1024):.2f} MB"

            # Truncate filename if long
            disp_name = (file_name[:24] + "...") if len(file_name) > 27 else file_name
            self.lbl_image_name.configure(text=disp_name, fg=COLOR_TEXT_PRIMARY)
            self.lbl_image_dims.configure(
                text=f"{orig_w} × {orig_h} px  •  {size_str}",
                fg=COLOR_CYAN
            )

            self.header_status_chip.configure(text="● Image Loaded", fg=COLOR_SUCCESS)
            self.set_status(f"Loaded: {file_name} ({orig_w}×{orig_h} px, {size_str})")

            # Update preview
            self._render_preview()

        except Exception as ex:
            messagebox.showerror(
                "Image Load Error",
                f"Failed to load image:\n{file_path}\n\nError: {str(ex)}"
            )
            self.set_status("Failed to load image.", is_error=True)

    def load_sample_image(self):
        """Convenience loader for bundled sample photo."""
        sample_path = os.path.join(os.path.dirname(__file__), "assets", "sample_photo.jpg")
        if os.path.exists(sample_path):
            self._load_image_from_path(sample_path)
        else:
            messagebox.showinfo("Sample Image", "Sample photo not found in assets folder.")

    def _load_default_sample_if_present(self):
        """Auto-loads sample image on startup if present."""
        sample_path = os.path.join(os.path.dirname(__file__), "assets", "sample_photo.jpg")
        if os.path.exists(sample_path):
            self.root.after(100, lambda: self._load_image_from_path(sample_path))

    # =========================================================================
    # Logo Upload & Management Functions
    # =========================================================================
    def upload_logo(self):
        """
        Prompts user to select a logo (PNG, JPG, etc.).
        Maintains aspect ratio and transparency.
        """
        file_types = [
            ("PNG Transparent Images", "*.png"),
            ("All Supported Images", "*.png *.jpg *.jpeg *.webp *.bmp"),
            ("All Files", "*.*")
        ]
        file_path = filedialog.askopenfilename(
            title="Select Logo Watermark",
            filetypes=file_types
        )
        if not file_path:
            return

        self._load_logo_from_path(file_path)

    def _load_logo_from_path(self, file_path: str):
        """Loads and parses logo image."""
        try:
            logo = Image.open(file_path)
            self.logo_image = logo.convert("RGBA")
            self.logo_path = file_path

            lw, lh = self.logo_image.size
            file_name = os.path.basename(file_path)
            disp_name = (file_name[:20] + "...") if len(file_name) > 23 else file_name
            self.lbl_logo_info.configure(
                text=f"Logo: {disp_name} ({lw}×{lh} px)",
                fg=COLOR_TEXT_PRIMARY
            )
            self.set_status(f"Logo loaded: {file_name} ({lw}×{lh} px)")

            # Auto-switch to logo or both if on text
            if self.watermark_mode.get() == "text":
                self._on_mode_change("both")
            else:
                self.schedule_preview_update()

        except Exception as ex:
            messagebox.showerror(
                "Logo Load Error",
                f"Failed to load logo image:\n{file_path}\n\nError: {str(ex)}"
            )
            self.set_status("Failed to load logo.", is_error=True)

    def load_sample_logo(self):
        """Convenience loader for bundled sample logo."""
        sample_path = os.path.join(os.path.dirname(__file__), "assets", "sample_logo.png")
        if os.path.exists(sample_path):
            self._load_logo_from_path(sample_path)
        else:
            messagebox.showinfo("Sample Logo", "Sample logo not found in assets folder.")

    # =========================================================================
    # Core Watermarking Engine (PIL)
    # =========================================================================
    def apply_watermarks(self, target_image: Image.Image, is_preview: bool = False, scale_factor: float = 1.0) -> Image.Image:
        """
        Applies text and/or logo watermarks to a base image.

        Args:
            target_image: Base PIL image to watermark.
            is_preview: Whether rendering for the GUI preview canvas.
            scale_factor: Ratio of target_image dimensions to original image dimensions.
                          Used to scale font size and margins proportionally so
                          preview exactly matches final high-res export.

        Returns:
            Watermarked PIL Image (RGBA or RGB).
        """
        mode = self.watermark_mode.get()
        base_rgba = target_image.convert("RGBA")
        canvas_w, canvas_h = base_rgba.size

        # Create overlay layer for transparent composites
        overlay = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))

        # 1. Apply Text Watermark
        if mode in ("text", "both") and self.text_content.get().strip():
            self._apply_text_layer(overlay, canvas_w, canvas_h, scale_factor)

        # 2. Apply Logo Watermark
        if mode in ("logo", "both") and self.logo_image is not None:
            self._apply_logo_layer(overlay, canvas_w, canvas_h, scale_factor)

        # Composite overlay on top of base image
        result = Image.alpha_composite(base_rgba, overlay)
        return result

    def _apply_text_layer(self, overlay: Image.Image, canvas_w: int, canvas_h: int, scale_factor: float):
        """Renders rotated, transparent text watermark onto overlay layer."""
        text = self.text_content.get()
        if not text:
            return

        # Scaled font size & padding for fidelity
        scaled_size = max(8, int(self.font_size.get() * scale_factor))
        scaled_pad = max(4, int(self.text_padding.get() * scale_factor))
        font = self._get_pil_font(self.font_family.get(), scaled_size)

        # Parse color and alpha
        hex_col = self.font_color.lstrip("#")
        try:
            r = int(hex_col[0:2], 16)
            g = int(hex_col[2:4], 16)
            b = int(hex_col[4:6], 16)
        except Exception:
            r, g, b = 255, 255, 255
        alpha = int(self.text_opacity.get() * 2.55)

        # Measure text accurately using getbbox
        temp_img = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        bbox = temp_draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0] + 16
        text_h = bbox[3] - bbox[1] + 16

        # Draw text onto a dedicated scrap image
        scrap = Image.new("RGBA", (text_w, text_h), (0, 0, 0, 0))
        sdraw = ImageDraw.Draw(scrap)
        sdraw.text((-bbox[0] + 8, -bbox[1] + 8), text, fill=(r, g, b, alpha), font=font)

        # Rotate text if angle is specified
        angle = self.text_rotation.get()
        if angle != 0:
            rotated_scrap = scrap.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
        else:
            rotated_scrap = scrap

        rw, rh = rotated_scrap.size

        # Check for Tiled pattern vs Single position
        if self.text_tiled.get():
            step_x = max(rw + 40, int(150 * scale_factor))
            step_y = max(rh + 30, int(100 * scale_factor))
            for x in range(0, canvas_w, step_x):
                for y in range(0, canvas_h, step_y):
                    overlay.paste(rotated_scrap, (x + 10, y + 10), rotated_scrap)
        else:
            pos_x, pos_y = self._calculate_coordinates(
                canvas_w, canvas_h, rw, rh,
                self.text_position.get(), scaled_pad
            )
            overlay.paste(rotated_scrap, (pos_x, pos_y), rotated_scrap)

    def _apply_logo_layer(self, overlay: Image.Image, canvas_w: int, canvas_h: int, scale_factor: float):
        """Renders scaled, transparent logo watermark onto overlay layer."""
        if self.logo_image is None:
            return

        orig_lw, orig_lh = self.logo_image.size
        if orig_lw <= 0 or orig_lh <= 0:
            return

        # Target width as percentage of base image width
        scale_pct = self.logo_scale.get() / 100.0
        target_lw = max(16, int(canvas_w * scale_pct))
        target_lh = max(16, int(orig_lh * (target_lw / orig_lw)))

        # Resize logo with Lanczos resampling
        resized_logo = self.logo_image.resize((target_lw, target_lh), Image.Resampling.LANCZOS)

        # Adjust alpha channel for opacity
        opacity_factor = self.logo_opacity.get() / 100.0
        r, g, b, a = resized_logo.split()
        a = a.point(lambda p: int(p * opacity_factor))
        resized_logo.putalpha(a)

        scaled_pad = max(4, int(self.logo_padding.get() * scale_factor))

        if self.logo_tiled.get():
            step_x = max(target_lw + 50, int(180 * scale_factor))
            step_y = max(target_lh + 40, int(140 * scale_factor))
            for x in range(0, canvas_w, step_x):
                for y in range(0, canvas_h, step_y):
                    overlay.paste(resized_logo, (x + 20, y + 20), resized_logo)
        else:
            pos_x, pos_y = self._calculate_coordinates(
                canvas_w, canvas_h, target_lw, target_lh,
                self.logo_position.get(), scaled_pad
            )
            overlay.paste(resized_logo, (pos_x, pos_y), resized_logo)

    def _calculate_coordinates(self, canvas_w: int, canvas_h: int, item_w: int, item_h: int, position: str, pad: int) -> tuple[int, int]:
        """Calculates (x, y) coordinates for bounding box alignment."""
        if position == "Top Left":
            return (pad, pad)
        elif position == "Top Right":
            return (max(0, canvas_w - item_w - pad), pad)
        elif position == "Center":
            return ((canvas_w - item_w) // 2, (canvas_h - item_h) // 2)
        elif position == "Bottom Left":
            return (pad, max(0, canvas_h - item_h - pad))
        elif position == "Bottom Right":
            return (max(0, canvas_w - item_w - pad), max(0, canvas_h - item_h - pad))
        else:
            # Default fallback: Bottom Right
            return (max(0, canvas_w - item_w - pad), max(0, canvas_h - item_h - pad))

    # =========================================================================
    # Preview Management & Canvas Rendering
    # =========================================================================
    def schedule_preview_update(self):
        """Debounces slider / keystroke events for fluid 60fps-like responsiveness."""
        if self._preview_debounce_id is not None:
            self.root.after_cancel(self._preview_debounce_id)
        self._preview_debounce_id = self.root.after(30, self._render_preview)

    def _on_canvas_resize(self, event):
        """Handles canvas resizing when the window is maximized or adjusted."""
        if self._resize_debounce_id is not None:
            self.root.after_cancel(self._resize_debounce_id)
        self._resize_debounce_id = self.root.after(60, self._render_preview)

    def _render_preview(self):
        """
        Renders the active preview onto the canvas.
        Maintains aspect ratio and scales smoothly without altering the original.
        """
        if self.original_image is None:
            self._render_empty_state()
            self.lbl_preview_dims.configure(text="No Image Loaded")
            self.lbl_preview_scale.configure(text="Fit: ---")
            return

        cw = self.preview_canvas.winfo_width()
        ch = self.preview_canvas.winfo_height()

        if cw <= 20 or ch <= 20:
            return

        orig_w, orig_h = self.original_image.size

        # Fit image into canvas preserving aspect ratio with padding
        margin = 20
        avail_w = max(100, cw - margin * 2)
        avail_h = max(100, ch - margin * 2)

        fit_scale = min(avail_w / orig_w, avail_h / orig_h)
        target_w = max(10, int(orig_w * fit_scale))
        target_h = max(10, int(orig_h * fit_scale))

        # Check if user is holding compare button to view unwatermarked original
        if self.show_original_preview.get():
            preview_base = self.original_image.resize((target_w, target_h), Image.Resampling.LANCZOS)
            final_preview = preview_base.convert("RGB")
            status_text = "Showing Original Image"
        else:
            # Render scaled preview base
            preview_base = self.original_image.resize((target_w, target_h), Image.Resampling.LANCZOS)
            # Apply watermarks scaled proportionally to preview dimensions
            scale_ratio = target_w / orig_w
            final_preview = self.apply_watermarks(preview_base, is_preview=True, scale_factor=scale_ratio)
            status_text = "Watermarked Preview"

        # Update Tkinter PhotoImage
        self.watermarked_preview_tk = ImageTk.PhotoImage(final_preview)

        # Clear and draw centered on canvas
        self.preview_canvas.delete("all")
        cx, cy = cw // 2, ch // 2

        # Draw subtle backdrop drop-shadow
        shadow_offset = 4
        self.preview_canvas.create_rectangle(
            cx - target_w // 2 + shadow_offset,
            cy - target_h // 2 + shadow_offset,
            cx + target_w // 2 + shadow_offset,
            cy + target_h // 2 + shadow_offset,
            fill="#05070c",
            outline=""
        )

        # Place image on canvas
        self.preview_canvas.create_image(cx, cy, image=self.watermarked_preview_tk, anchor="center")

        # Update preview toolbar chips
        self.lbl_preview_dims.configure(text=f"{status_text}: {target_w}×{target_h} px")
        self.lbl_preview_scale.configure(text=f"Fit: {int(fit_scale * 100)}% (Original {orig_w}×{orig_h})")

    # =========================================================================
    # Save Image Functionality (Full-Resolution Export)
    # =========================================================================
    def save_watermarked_image(self):
        """
        Applies watermarks directly to a full-resolution copy of the original
        image and prompts user to save as PNG or JPG.
        """
        if self.original_image is None:
            messagebox.showwarning(
                "No Image Loaded",
                "Please upload an image before attempting to save."
            )
            return

        mode = self.watermark_mode.get()
        if mode in ("text", "both") and not self.text_content.get().strip() and (mode == "text" or self.logo_image is None):
            messagebox.showwarning(
                "Missing Watermark",
                "Please enter watermark text or upload a logo before saving."
            )
            return

        # Default filename suggestion
        orig_basename = os.path.splitext(os.path.basename(self.original_image_path or "watermarked"))[0]
        suggested_name = f"{orig_basename}_watermarked.png"

        save_path = filedialog.asksaveasfilename(
            title="Save Watermarked Image",
            initialfile=suggested_name,
            defaultextension=".png",
            filetypes=[
                ("PNG Image (Lossless)", "*.png"),
                ("JPEG Image (High Quality)", "*.jpg *.jpeg"),
                ("All Files", "*.*")
            ]
        )
        if not save_path:
            return

        try:
            self.set_status("Applying watermarks to full-resolution image...")
            self.root.update_idletasks()

            # Render watermark directly at full original resolution (scale_factor = 1.0)
            orig_copy = self.original_image.copy()
            final_output = self.apply_watermarks(orig_copy, is_preview=False, scale_factor=1.0)

            # Handle format specifics
            ext = os.path.splitext(save_path)[1].lower()
            if ext in (".jpg", ".jpeg"):
                # Convert RGBA to RGB with clean solid background
                rgb_output = Image.new("RGB", final_output.size, (255, 255, 255))
                if final_output.mode == "RGBA":
                    rgb_output.paste(final_output, mask=final_output.split()[3])
                else:
                    rgb_output.paste(final_output)
                rgb_output.save(save_path, "JPEG", quality=95, optimize=True)
            else:
                final_output.save(save_path, "PNG", optimize=True)

            out_size_kb = os.path.getsize(save_path) / 1024
            size_str = f"{out_size_kb:.1f} KB" if out_size_kb < 1024 else f"{(out_size_kb / 1024):.2f} MB"
            ow, oh = final_output.size

            self.set_status(f"Saved successfully: {os.path.basename(save_path)} ({ow}×{oh} px, {size_str})")

            # Success confirmation dialog with option to open folder
            msg = (
                f"Your watermarked image has been successfully saved!\n\n"
                f"File: {os.path.basename(save_path)}\n"
                f"Resolution: {ow} × {oh} px\n"
                f"File Size: {size_str}\n"
                f"Destination: {save_path}\n\n"
                f"Would you like to open the output folder?"
            )
            open_folder = messagebox.askyesno("Watermark Studio - Save Successful", msg)
            if open_folder:
                folder = os.path.dirname(save_path)
                if sys.platform == "win32":
                    os.startfile(folder)
                elif sys.platform == "darwin":
                    os.system(f"open '{folder}'")
                else:
                    os.system(f"xdg-open '{folder}'")

        except Exception as ex:
            messagebox.showerror(
                "Export Error",
                f"An error occurred while saving the image:\n\n{str(ex)}"
            )
            self.set_status("Failed to save image.", is_error=True)

    # =========================================================================
    # Reset Application State
    # =========================================================================
    def reset_all(self):
        """
        Clears the loaded image, logo, and resets all settings
        to sensible defaults after user confirmation.
        """
        if self.original_image is not None or self.logo_image is not None:
            confirm = messagebox.askyesno(
                "Reset Watermark Studio",
                "Are you sure you want to reset all images and watermark settings?"
            )
            if not confirm:
                return

        # Reset images
        self.original_image = None
        self.original_image_path = None
        self.preview_image = None
        self.watermarked_preview_tk = None
        self.logo_image = None
        self.logo_path = None

        # Reset watermark settings
        self.watermark_mode.set("text")
        self.text_content.set("© Copyright 2026 Watermark Studio")
        self.font_family.set("Segoe UI")
        self.font_size.set(42)
        self.font_color = "#ffffff"
        self.color_swatch.configure(bg="#ffffff")
        self.text_opacity.set(80)
        self.text_rotation.set(0)
        self.text_position.set("Bottom Right")
        self.text_padding.set(30)
        self.text_tiled.set(False)

        self.logo_scale.set(22)
        self.logo_opacity.set(85)
        self.logo_position.set("Top Right")
        self.logo_padding.set(30)
        self.logo_tiled.set(False)

        # Reset UI labels
        self.lbl_image_name.configure(text="No image loaded", fg=COLOR_TEXT_SECONDARY)
        self.lbl_image_dims.configure(text="Supported: JPG, JPEG, PNG", fg=COLOR_TEXT_MUTED)
        self.lbl_logo_info.configure(
            text="No logo selected (PNG with transparency recommended)",
            fg=COLOR_TEXT_MUTED
        )
        self.header_status_chip.configure(text="● Waiting for Image", fg=COLOR_WARNING)

        # Reset mode buttons
        self._on_mode_change("text")
        self._set_text_position("Bottom Right")
        self._set_logo_position("Top Right")

        # Reset sliders labels
        self.lbl_font_size.configure(text="Font Size: 42 px")
        self.lbl_text_opacity.configure(text="Opacity: 80%")
        self.lbl_text_rotation.configure(text="Angle / Rotation: 0°")
        self.lbl_text_padding.configure(text="Margin / Padding: 30 px")
        self.lbl_logo_scale.configure(text="Logo Scale: 22% of width")
        self.lbl_logo_opacity.configure(text="Logo Opacity: 85%")
        self.lbl_logo_padding.configure(text="Margin / Padding: 30 px")

        # Clear canvas
        self._render_empty_state()
        self.set_status("All settings and images have been reset.")


# =============================================================================
# Application Entrypoint
# =============================================================================
def main():
    """Main application initialization."""
    root = tk.Tk()
    app = WatermarkStudioApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

