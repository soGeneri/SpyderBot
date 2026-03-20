# -*- coding: utf-8 -*-
"""LED window UI — layout-based."""

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QLineEdit, QDial,
    QRadioButton, QGroupBox, QHBoxLayout, QVBoxLayout,
)
from widgets import ColorPreviewWidget


class Ui_led(object):
    def setupUi(self, led):
        led.setObjectName("led")
        led.resize(640, 320)

        central = QWidget(led)
        led.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(12)

        # ── LEFT: LED mode + HSL ────────────────────────────────────────────
        left_group = QGroupBox("LED Mode")
        left_layout = QVBoxLayout(left_group)

        self.radioButtonOne   = QRadioButton("Mode 1")
        self.radioButtonTwo   = QRadioButton("Mode 2")
        self.radioButtonThree = QRadioButton("Mode 3")
        self.radioButtonFour  = QRadioButton("Mode 4")
        self.radioButtonFive  = QRadioButton("Mode 5")
        self.radioButtonOne.setObjectName("radioButtonOne")
        self.radioButtonTwo.setObjectName("radioButtonTwo")
        self.radioButtonThree.setObjectName("radioButtonThree")
        self.radioButtonFour.setObjectName("radioButtonFour")
        self.radioButtonFive.setObjectName("radioButtonFive")
        for rb in (self.radioButtonOne, self.radioButtonTwo,
                   self.radioButtonThree, self.radioButtonFour,
                   self.radioButtonFive):
            left_layout.addWidget(rb)

        self.pushButtonLightsOut = QPushButton("Turn off")
        self.pushButtonLightsOut.setObjectName("pushButtonLightsOut")
        left_layout.addWidget(self.pushButtonLightsOut)

        # Color preview swatch
        self.color_preview = ColorPreviewWidget()
        self.color_preview.setObjectName("color_preview")
        left_layout.addWidget(self.color_preview)

        # HSL row
        hsl_row = QHBoxLayout()
        hsl_row.addWidget(QLabel("H:"))
        self.lineEdit_H = QLineEdit("0")
        self.lineEdit_H.setObjectName("lineEdit_H")
        self.lineEdit_H.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lineEdit_H.setFixedWidth(45)
        hsl_row.addWidget(self.lineEdit_H)

        hsl_row.addWidget(QLabel("S:"))
        self.lineEdit_S = QLineEdit("0")
        self.lineEdit_S.setObjectName("lineEdit_S")
        self.lineEdit_S.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lineEdit_S.setFixedWidth(45)
        hsl_row.addWidget(self.lineEdit_S)

        hsl_row.addWidget(QLabel("L:"))
        self.lineEdit_L = QLineEdit("1")
        self.lineEdit_L.setObjectName("lineEdit_L")
        self.lineEdit_L.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lineEdit_L.setFixedWidth(45)
        hsl_row.addWidget(self.lineEdit_L)
        left_layout.addLayout(hsl_row)
        left_layout.addStretch()

        root.addWidget(left_group)

        # ── RIGHT: RGB + color picker + dial ────────────────────────────────
        right_layout = QVBoxLayout()

        # RGB row
        rgb_row = QHBoxLayout()
        rgb_row.addWidget(QLabel("R:"))
        self.lineEdit_R = QLineEdit("255")
        self.lineEdit_R.setObjectName("lineEdit_R")
        self.lineEdit_R.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lineEdit_R.setFixedWidth(45)
        rgb_row.addWidget(self.lineEdit_R)

        rgb_row.addWidget(QLabel("G:"))
        self.lineEdit_G = QLineEdit("255")
        self.lineEdit_G.setObjectName("lineEdit_G")
        self.lineEdit_G.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lineEdit_G.setFixedWidth(45)
        rgb_row.addWidget(self.lineEdit_G)

        rgb_row.addWidget(QLabel("B:"))
        self.lineEdit_B = QLineEdit("255")
        self.lineEdit_B.setObjectName("lineEdit_B")
        self.lineEdit_B.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lineEdit_B.setFixedWidth(45)
        rgb_row.addWidget(self.lineEdit_B)
        rgb_row.addStretch()
        right_layout.addLayout(rgb_row)

        # Placeholder widget for ColorDialog embedding
        self.widget = QWidget()
        self.widget.setObjectName("widget")
        right_layout.addWidget(self.widget, stretch=1)

        # Dial
        self.dial_color = QDial()
        self.dial_color.setObjectName("dial_color")
        self.dial_color.setRange(0, 360)
        self.dial_color.setWrapping(True)
        self.dial_color.setNotchesVisible(True)
        self.dial_color.setFixedSize(140, 140)
        right_layout.addWidget(
            self.dial_color, alignment=Qt.AlignmentFlag.AlignCenter)

        root.addLayout(right_layout)

        self.retranslateUi(led)
        QtCore.QMetaObject.connectSlotsByName(led)

    def retranslateUi(self, led):
        led.setWindowTitle("LED Control")
