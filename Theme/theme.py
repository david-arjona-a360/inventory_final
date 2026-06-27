"""
Shared theme extracted from Theme/logo.jpg (A360 logo).

Extracted palette:
  PRIMARY     #df212b  – A360 brand red
  SECONDARY   #796a6d  – muted gray-mauve
  ACCENT      #8d3f44  – dark red accent
  LIGHT_BG    #efe5e3  – very light pinkish beige
  WHITE       #ffffff  – clean white background
  DARK_RED    #b81a24  – hover / darker variant
  TEXT_DARK   #3a3a3a  – high-contrast body text
  TEXT_MUTED  #796a6d  – secondary / muted text (matches SECONDARY)
  BORDER      #d9d0ce  – light border derived from LIGHT_BG

Button standard (applied in both Insumos and Equipos modules):
  ┌──────────┬────────────┬──────────┬──────────┬──────────┬──────────┐
  │ Property │ Primary    │ Secondary│ Danger   │ Nav      │ Logout   │
  ├──────────┼────────────┼──────────┼──────────┼──────────┼──────────┤
  │ BG       │ PRIMARY    │ WHITE    │ none     │ none     │ PRIMARY  │
  │ Text     │ WHITE      │ TEXT_DARK│ PRIMARY  │ TEXT_DARK│ WHITE    │
  │ Border   │ none       │ BORDER   │ PRIMARY  │ none     │ none     │
  │ Hover BG │ HOVER      │ LIGHT_BG │ LIGHT_BG │ LIGHT_BG │ DARK_RED │
  │ Height   │ 36px       │ 36px     │ 36px     │ —        │ —        │
  │ Font     │ 10pt Bold  │ 10pt     │ 10pt     │ 13pt Bold│ 13pt Bold│
  │ Radius   │ 4px        │ 4px      │ 4px      │ 4px      │ 4px      │
  └──────────┴────────────┴──────────┴──────────┴──────────┴──────────┘
"""

import os

THEME_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(THEME_DIR, "logo.jpg")

PRIMARY     = "#df212b"
SECONDARY   = "#796a6d"
ACCENT      = "#8d3f44"
LIGHT_BG    = "#efe5e3"
WHITE       = "#ffffff"
DARK_RED    = "#b81a24"
TEXT_DARK   = "#3a3a3a"
TEXT_MUTED  = "#796a6d"
BORDER      = "#d9d0ce"
HOVER       = "#c91d26"

ROLE_COLORS = {
    "admin":  PRIMARY,
    "editor": SECONDARY,
    "viewer": TEXT_MUTED,
}

LOGO_WIDTH = 100
