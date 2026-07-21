import sys
import os

_theme_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Theme"))
if _theme_dir not in sys.path:
    sys.path.insert(0, _theme_dir)

from theme import (
    PRIMARY, SECONDARY, ACCENT, LIGHT_BG, WHITE, DARK_RED,
    TEXT_DARK, TEXT_MUTED, BORDER, HOVER,
)

from PyQt5.QtGui import QFont


FONT_FAMILY = "Segoe UI"

FONT_TITLE = lambda size=16: QFont(FONT_FAMILY, size, QFont.Bold)
FONT_HEADER = lambda size=14: QFont(FONT_FAMILY, size, QFont.Bold)
FONT_BODY = lambda size=10: QFont(FONT_FAMILY, size)
FONT_SMALL = lambda size=9: QFont(FONT_FAMILY, size)
FONT_INPUT = lambda size=11: QFont(FONT_FAMILY, size)


BASE_QSS = f"""
    #primaryBtn {{
        background-color: {PRIMARY};
        color: {WHITE};
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
    }}
    #primaryBtn:hover {{
        background-color: {HOVER};
    }}
    #primaryBtn:disabled {{
        background-color: {BORDER};
        color: {TEXT_MUTED};
    }}
    #dangerBtn {{
        background-color: transparent;
        color: {PRIMARY};
        border: 1px solid {PRIMARY};
        border-radius: 4px;
        padding: 8px 16px;
    }}
    #dangerBtn:hover {{
        background-color: {LIGHT_BG};
    }}
    #dangerBtn:disabled {{
        border-color: {BORDER};
        color: {TEXT_MUTED};
    }}
    #actionBtn {{
        background-color: {WHITE};
        color: {TEXT_DARK};
        border: 1px solid {BORDER};
        border-radius: 4px;
        padding: 6px 12px;
    }}
    #actionBtn:hover {{
        background-color: {LIGHT_BG};
    }}
    QTableWidget {{
        border: 1px solid {BORDER};
        border-radius: 4px;
        gridline-color: {BORDER};
        selection-background-color: {LIGHT_BG};
        selection-color: {TEXT_DARK};
    }}
    QTableWidget::item {{
        padding: 6px 8px;
    }}
    QHeaderView::section {{
        background-color: {LIGHT_BG};
        color: {TEXT_DARK};
        font-weight: bold;
        border: none;
        border-bottom: 2px solid {BORDER};
        padding: 8px;
    }}
    QLineEdit {{
        border: 1px solid {BORDER};
        border-radius: 4px;
        padding: 6px 10px;
        background-color: {WHITE};
    }}
    QLineEdit:focus {{
        border-color: {PRIMARY};
    }}
"""


def apply_base_style(widget):
    widget.setStyleSheet(BASE_QSS)
