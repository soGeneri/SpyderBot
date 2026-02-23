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

/* Control Group Boxes */
QGroupBox {
    border: 2px solid #333;
    border-radius: 8px;
    margin-top: 15px;
    font-weight: bold;
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

QPushButton#Button_Connect {
    background-color: #00c853;
    font-weight: bold;
}

QPushButton#Button_Connect:checked {
    background-color: #d50000;
}

/* Sliders */
QSlider::handle:horizontal {
    background: #008aff;
    width: 14px;
    border-radius: 7px;
}

/* Line Edits */
QLineEdit {
    background-color: #252525;
    border: 1px solid #444;
    padding: 5px;
    border-radius: 3px;
}
"""

