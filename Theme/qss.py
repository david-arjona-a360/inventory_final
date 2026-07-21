# Shared refined QSS for both Insumos and Equipos apps


def build_stylesheet(colors: dict) -> str:
    P = colors["PRIMARY"]
    S = colors["SECONDARY"]
    A = colors["ACCENT"]
    LB = colors["LIGHT_BG"]
    W = colors["WHITE"]
    DR = colors["DARK_RED"]
    TD = colors["TEXT_DARK"]
    TM = colors["TEXT_MUTED"]
    B = colors["BORDER"]
    H = colors["HOVER"]

    return f"""
QWidget {{
    font-family: "Segoe UI Variable", "Segoe UI", "Arial", sans-serif;
    color: {TD};
    font-size: 10pt;
}}
QMainWindow {{
    background-color: {W};
}}
QDialog {{
    background-color: {W};
}}
QLabel {{
    color: {TD};
    background-color: transparent;
}}
QLineEdit {{
    border: 1px solid {B};
    border-radius: 6px;
    padding: 6px 10px;
    background-color: {W};
    color: {TD};
    font-size: 10pt;
    selection-background-color: {P};
    selection-color: {W};
}}
QLineEdit:focus {{
    border-color: {P};
    border-width: 2px;
}}
QLineEdit:disabled {{
    background-color: {LB};
    color: {TM};
}}
QComboBox {{
    border: 1px solid {B};
    border-radius: 6px;
    padding: 6px 10px;
    background-color: {W};
    color: {TD};
    font-size: 10pt;
}}
QComboBox:focus {{
    border-color: {P};
    border-width: 2px;
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid {TM};
    margin-right: 6px;
}}
QSpinBox {{
    border: 1px solid {B};
    border-radius: 6px;
    padding: 6px 10px;
    background-color: {W};
    color: {TD};
    font-size: 10pt;
}}
QSpinBox:focus {{
    border-color: {P};
    border-width: 2px;
}}
QPushButton {{
    background-color: {W};
    color: {TD};
    border: 1px solid {B};
    border-radius: 6px;
    padding: 8px 20px;
    font-size: 10pt;
    min-height: 36px;
}}
QPushButton:hover {{
    background-color: {LB};
    border-color: {S};
}}
QPushButton:pressed {{
    background-color: {B};
}}
QPushButton:disabled {{
    background-color: {LB};
    color: {TM};
    border-color: {B};
}}
QTableWidget {{
    border: 1px solid {B};
    border-radius: 6px;
    gridline-color: {B};
    background-color: {W};
    alternate-background-color: #f8f4f3;
    selection-background-color: {P};
    selection-color: {W};
    font-size: 10pt;
}}
QTableWidget::item {{
    padding: 6px 10px;
    border: none;
}}
QTableWidget::item:hover {{
    background-color: #f0eae8;
    color: {TD};
}}
QTableWidget::item:selected:hover {{
    background-color: {H};
    color: {W};
}}
QHeaderView::section {{
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {LB}, stop:1 #e5dbd9);
    color: {TD};
    font-weight: bold;
    font-size: 10pt;
    border: none;
    border-bottom: 2px solid {P};
    border-right: 1px solid {B};
    padding: 8px 10px;
}}
QHeaderView::section:hover {{
    background-color: {B};
}}
QGroupBox {{
    font-weight: bold;
    font-size: 11pt;
    border: 1px solid {B};
    border-radius: 8px;
    margin-top: 14px;
    padding-top: 18px;
    padding-right: 12px;
    padding-bottom: 12px;
    padding-left: 12px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 8px;
    color: {TD};
}}
QCheckBox {{
    spacing: 8px;
    color: {TD};
    font-size: 10pt;
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 3px;
    border: 1px solid {B};
}}
QCheckBox::indicator:checked {{
    background-color: {P};
    border-color: {P};
}}
QRadioButton {{
    spacing: 8px;
    font-size: 10pt;
    color: {TD};
}}
QRadioButton::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 9px;
    border: 1px solid {B};
}}
QRadioButton::indicator:checked {{
    background-color: {P};
    border-color: {P};
}}
QScrollBar:vertical {{
    background: {LB};
    width: 8px;
    border: none;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {B};
    border-radius: 4px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: {S};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar:horizontal {{
    background: {LB};
    height: 8px;
    border: none;
    border-radius: 4px;
}}
QScrollBar::handle:horizontal {{
    background: {B};
    border-radius: 4px;
    min-width: 24px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {S};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}
QStatusBar {{
    background-color: {LB};
    color: {TM};
    border-top: 1px solid {B};
    font-size: 10pt;
    padding: 4px 12px;
}}
QFrame#navBar {{
    background-color: {W};
    border-bottom: 2px solid {P};
}}
QPushButton#navBtn {{
    background-color: transparent;
    color: {TD};
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-size: 11pt;
    font-weight: bold;
}}
QPushButton#navBtn:hover {{
    background-color: {LB};
    color: {P};
}}
QPushButton#logoutBtn {{
    background-color: {P};
    color: {W};
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-size: 11pt;
    font-weight: bold;
}}
QPushButton#logoutBtn:hover {{
    background-color: {DR};
}}
QPushButton#primaryBtn {{
    background-color: {P};
    color: {W};
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-size: 10pt;
    font-weight: bold;
}}
QPushButton#primaryBtn:hover {{
    background-color: {H};
}}
QPushButton#primaryBtn:disabled {{
    background-color: {B};
    color: {TM};
}}
QPushButton#dangerBtn {{
    background-color: transparent;
    color: {P};
    border: 1px solid {P};
    border-radius: 6px;
    padding: 8px 20px;
    font-size: 10pt;
}}
QPushButton#dangerBtn:hover {{
    background-color: {LB};
}}
QPushButton#dangerBtn:disabled {{
    border-color: {B};
    color: {TM};
}}
QPushButton#actionBtn {{
    background-color: {W};
    color: {TD};
    border: 1px solid {B};
    border-radius: 6px;
    padding: 6px 16px;
    font-size: 10pt;
}}
QPushButton#actionBtn:hover {{
    background-color: {LB};
    border-color: {S};
}}
QPushButton#cancelBtn {{
    background-color: {W};
    color: {TD};
    border: 1px solid {B};
    border-radius: 6px;
    padding: 8px 20px;
    font-size: 10pt;
}}
QPushButton#cancelBtn:hover {{
    background-color: {LB};
    border-color: {S};
}}
"""
