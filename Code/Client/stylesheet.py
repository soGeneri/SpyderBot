MODERN_STYLE = """
QMainWindow {
    background-color: #121212;
}

QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
}

/* Group Boxes */
QGroupBox {
    border: 2px solid #333;
    border-radius: 8px;
    margin-top: 15px;
    font-weight: bold;
    color: #008aff;
}

QGroupBox::title {
    subcontrol-position: top left;
    padding: 0 6px;
    color: #008aff;
}

/* Buttons */
QPushButton {
    background-color: #333;
    border: none;
    padding: 8px 15px;
    border-radius: 4px;
    color: white;
}

QPushButton:hover {
    background-color: #444;
}

QPushButton:pressed {
    background-color: #555;
}

QPushButton:checked {
    background-color: #d50000;
}

QPushButton#Button_Connect {
    background-color: #00c853;
    font-weight: bold;
}

QPushButton#Button_Connect:checked {
    background-color: #d50000;
}

/* Radio Buttons */
QRadioButton {
    color: #e0e0e0;
    spacing: 6px;
}

QRadioButton::indicator {
    width: 14px;
    height: 14px;
    border-radius: 7px;
    border: 2px solid #555;
}

QRadioButton::indicator:checked {
    background: #008aff;
    border-color: #008aff;
}

/* Sliders */
QSlider::groove:horizontal,
QSlider::add-page:horizontal {
    height: 3px;
    border-radius: 3px;
    background: #18181a;
}

QSlider::sub-page:horizontal {
    height: 8px;
    border-radius: 3px;
    background: #008aff;
}

QSlider::handle:horizontal {
    background: #008aff;
    width: 14px;
    margin-top: -5px;
    margin-bottom: -4px;
    border-radius: 7px;
}

QSlider::groove:vertical,
QSlider::sub-page:vertical {
    width: 3px;
    border-radius: 3px;
    background: #18181a;
}

QSlider::add-page:vertical {
    width: 8px;
    border-radius: 3px;
    background: #008aff;
}

QSlider::handle:vertical {
    background: #008aff;
    height: 14px;
    margin-left: -5px;
    margin-right: -4px;
    border-radius: 7px;
}

/* Line Edits */
QLineEdit {
    background-color: #252525;
    border: 1px solid #444;
    padding: 5px;
    border-radius: 3px;
}

/* Progress Bars */
QProgressBar {
    border: 1px solid #444;
    border-radius: 3px;
    background: #252525;
    text-align: center;
    color: #e0e0e0;
    height: 16px;
}

QProgressBar::chunk {
    background: #008aff;
    border-radius: 2px;
}
"""
