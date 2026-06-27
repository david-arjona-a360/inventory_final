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
