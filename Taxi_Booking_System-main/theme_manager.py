"""
Theme Manager for Dark/Light Mode Toggle
"""
import json
import os

THEME_FILE = "theme_preference.json"

# Light Theme Colors
LIGHT_THEME = {
    "sidebar_bg": "#050816",
    "sidebar_btn": "#111827",
    "sidebar_btn_active": "#1f2937",
    "content_bg": "#f9fafb",
    "accent": "#2563eb",
    "text_primary": "#111827",
    "text_secondary": "#6b7280",
    "card_bg": "#ffffff",
    "card_text": "#111827",
    "card_text_secondary": "#6b7280",
    "entry_bg": "#ffffff",
    "entry_fg": "#111827",
    "treeview_bg": "#ffffff",
    "treeview_fg": "#111827",
    "treeview_even": "#ffffff",
    "treeview_odd": "#f3f4f6",
    "treeview_selected_bg": "#2563eb",
    "treeview_selected_fg": "#ffffff",
}

# Dark Theme Colors
DARK_THEME = {
    "sidebar_bg": "#0f172a",
    "sidebar_btn": "#1e293b",
    "sidebar_btn_active": "#334155",
    "content_bg": "#1e293b",
    "accent": "#3b82f6",
    "text_primary": "#f1f5f9",
    "text_secondary": "#cbd5e1",
    "card_bg": "#334155",
    "card_text": "#f1f5f9",
    "card_text_secondary": "#cbd5e1",
    "entry_bg": "#475569",
    "entry_fg": "#f1f5f9",
    "treeview_bg": "#334155",
    "treeview_fg": "#f1f5f9",
    "treeview_even": "#334155",
    "treeview_odd": "#475569",
    "treeview_selected_bg": "#3b82f6",
    "treeview_selected_fg": "#ffffff",
}


def get_theme_preference():
    """Load theme preference from file, default to 'light'."""
    if os.path.exists(THEME_FILE):
        try:
            with open(THEME_FILE, 'r') as f:
                data = json.load(f)
                return data.get("theme", "light")
        except Exception:
            return "light"
    return "light"


def save_theme_preference(theme):
    """Save theme preference to file."""
    try:
        with open(THEME_FILE, 'w') as f:
            json.dump({"theme": theme}, f)
    except Exception:
        pass


def get_theme_colors(theme=None):
    """Get color dictionary for the specified theme."""
    if theme is None:
        theme = get_theme_preference()
    
    if theme == "dark":
        return DARK_THEME.copy()
    else:
        return LIGHT_THEME.copy()
