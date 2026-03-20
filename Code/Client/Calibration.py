# -*- coding: utf-8 -*-
"""Calibration UI (layout-based) + calibrationWindow logic."""
from Command import COMMAND as cmd
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QPushButton, QLineEdit,
    QRadioButton, QGroupBox, QHBoxLayout, QVBoxLayout, QGridLayout,
    QMessageBox, QSizePolicy,
)


# ── UI layout class ──────────────────────────────────────────────────────────
class Ui_calibration(object):
    def setupUi(self, calibration):
        calibration.setObjectName("calibration")
        calibration.resize(720, 420)

        central = QWidget(calibration)
        calibration.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(10)

        # ── Left panel ──────────────────────────────────────────────────────
        left_panel = QVBoxLayout()
        left_panel.setSpacing(8)

        # Select Leg group
        leg_group = QGroupBox("Select Leg")
        leg_layout = QVBoxLayout(leg_group)
        self.radioButton_one   = QRadioButton("One")
        self.radioButton_two   = QRadioButton("Two")
        self.radioButton_three = QRadioButton("Three")
        self.radioButton_four  = QRadioButton("Four")
        self.radioButton_five  = QRadioButton("Five")
        self.radioButton_six   = QRadioButton("Six")
        self.radioButton_one.setObjectName("radioButton_one")
        self.radioButton_two.setObjectName("radioButton_two")
        self.radioButton_three.setObjectName("radioButton_three")
        self.radioButton_four.setObjectName("radioButton_four")
        self.radioButton_five.setObjectName("radioButton_five")
        self.radioButton_six.setObjectName("radioButton_six")
        for rb in (self.radioButton_one, self.radioButton_two,
                   self.radioButton_three, self.radioButton_four,
                   self.radioButton_five, self.radioButton_six):
            leg_layout.addWidget(rb)
        left_panel.addWidget(leg_group)

        # Data grid: header + 6 rows
        data_grid = QGridLayout()
        data_grid.setSpacing(4)
        for col, text in enumerate(("Leg", "X", "Y", "Z")):
            lbl = QLabel(text)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            data_grid.addWidget(lbl, 0, col)

        legs = ("one", "two", "three", "four", "five", "six")
        defaults_y = (72, 72, 72, 72, 72, 72)
        for row, (leg, y_val) in enumerate(zip(legs, defaults_y), start=1):
            leg_lbl = QLabel(leg.capitalize())
            leg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            data_grid.addWidget(leg_lbl, row, 0)
            for col, (attr, default) in enumerate(
                    (("_x", "0"), ("_y", str(y_val)), ("_z", "0")), start=1):
                le = QLineEdit(default)
                le.setObjectName(f"{leg}{attr}")
                le.setAlignment(Qt.AlignmentFlag.AlignCenter)
                le.setFixedWidth(50)
                setattr(self, f"{leg}{attr}", le)
                data_grid.addWidget(le, row, col)
        left_panel.addLayout(data_grid)

        # Adjust group  (X+/X- / Y+/Y- / Z+/Z- + Save in centre)
        adj_group = QGroupBox("Adjust")
        adj_grid = QGridLayout(adj_group)
        adj_grid.setSpacing(4)

        self.Button_X2 = QPushButton("X−")
        self.Button_X1 = QPushButton("X+")
        self.Button_Y2 = QPushButton("Y−")
        self.Button_Save = QPushButton("Save")
        self.Button_Y1 = QPushButton("Y+")
        self.Button_Z2 = QPushButton("Z−")
        self.Button_Z1 = QPushButton("Z+")
        self.Button_X2.setObjectName("Button_X2")
        self.Button_X1.setObjectName("Button_X1")
        self.Button_Y2.setObjectName("Button_Y2")
        self.Button_Save.setObjectName("Button_Save")
        self.Button_Y1.setObjectName("Button_Y1")
        self.Button_Z2.setObjectName("Button_Z2")
        self.Button_Z1.setObjectName("Button_Z1")

        adj_grid.addWidget(self.Button_X2,   0, 0)
        adj_grid.addWidget(QLabel(""),        0, 1)
        adj_grid.addWidget(self.Button_X1,   0, 2)
        adj_grid.addWidget(self.Button_Y2,   1, 0)
        adj_grid.addWidget(self.Button_Save, 1, 1)
        adj_grid.addWidget(self.Button_Y1,   1, 2)
        adj_grid.addWidget(self.Button_Z2,   2, 0)
        adj_grid.addWidget(QLabel(""),        2, 1)
        adj_grid.addWidget(self.Button_Z1,   2, 2)
        left_panel.addWidget(adj_group)
        left_panel.addStretch()

        # ── Right: diagram ───────────────────────────────────────────────────
        self.label_picture = QLabel()
        self.label_picture.setObjectName("label_picture")
        self.label_picture.setFixedSize(320, 320)
        self.label_picture.setScaledContents(True)

        root.addLayout(left_panel)
        root.addWidget(self.label_picture)

        self.retranslateUi(calibration)
        QtCore.QMetaObject.connectSlotsByName(calibration)

    def retranslateUi(self, calibration):
        calibration.setWindowTitle("Calibration")


# ── Window logic ─────────────────────────────────────────────────────────────
class calibrationWindow(QMainWindow, Ui_calibration):
    def __init__(self, client):
        super(calibrationWindow, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon('Picture/logo_Mini.png'))
        self.label_picture.setPixmap(QPixmap('Picture/Spider_calibration.png'))
        self.client = client
        self.leg = 'one'
        self.x = self.y = self.z = 0

        # Dict for clean get/set without if-elif chains
        self._leg_fields = {
            "one":   (self.one_x,   self.one_y,   self.one_z),
            "two":   (self.two_x,   self.two_y,   self.two_z),
            "three": (self.three_x, self.three_y, self.three_z),
            "four":  (self.four_x,  self.four_y,  self.four_z),
            "five":  (self.five_x,  self.five_y,  self.five_z),
            "six":   (self.six_x,   self.six_y,   self.six_z),
        }

        self.point = self.Read_from_txt('point')
        self.set_point(self.point)

        self.radioButton_one.setChecked(True)
        for rb in (self.radioButton_one, self.radioButton_two,
                   self.radioButton_three, self.radioButton_four,
                   self.radioButton_five, self.radioButton_six):
            rb.toggled.connect(lambda checked, b=rb: self.leg_point(b))

        self.Button_Save.clicked.connect(self.save)
        self.Button_X1.clicked.connect(self.X1)
        self.Button_X2.clicked.connect(self.X2)
        self.Button_Y1.clicked.connect(self.Y1)
        self.Button_Y2.clicked.connect(self.Y2)
        self.Button_Z1.clicked.connect(self.Z1)
        self.Button_Z2.clicked.connect(self.Z2)

    # ── Axis buttons ─────────────────────────────────────────────────────────
    def _send(self):
        command = (cmd.CMD_CALIBRATION + '#' + self.leg + '#' +
                   str(self.x) + '#' + str(self.y) + '#' + str(self.z) + '\n')
        self.client.send_data(command)
        self.set_point()

    def X1(self):
        self.get_point(); self.x += 1; self._send()
    def X2(self):
        self.get_point(); self.x -= 1; self._send()
    def Y1(self):
        self.get_point(); self.y += 1; self._send()
    def Y2(self):
        self.get_point(); self.y -= 1; self._send()
    def Z1(self):
        self.get_point(); self.z += 1; self._send()
    def Z2(self):
        self.get_point(); self.z -= 1; self._send()

    # ── Data management ───────────────────────────────────────────────────────
    def set_point(self, data=None):
        if data is None:
            x_f, y_f, z_f = self._leg_fields[self.leg]
            x_f.setText(str(self.x))
            y_f.setText(str(self.y))
            z_f.setText(str(self.z))
            idx = list(self._leg_fields.keys()).index(self.leg)
            self.point[idx] = [self.x, self.y, self.z]
        else:
            for i, (name, (x_f, y_f, z_f)) in enumerate(self._leg_fields.items()):
                x_f.setText(str(data[i][0]))
                y_f.setText(str(data[i][1]))
                z_f.setText(str(data[i][2]))

    def get_point(self):
        x_f, y_f, z_f = self._leg_fields[self.leg]
        self.x = int(x_f.text())
        self.y = int(y_f.text())
        self.z = int(z_f.text())

    def save(self):
        command = cmd.CMD_CALIBRATION + '#save\n'
        self.client.send_data(command)
        for i, (name, (x_f, y_f, z_f)) in enumerate(self._leg_fields.items()):
            self.point[i] = [x_f.text(), y_f.text(), z_f.text()]
        self.Save_to_txt(self.point, 'point')
        QMessageBox.information(self, "Message", "Saved successfully",
                                QMessageBox.StandardButton.Yes)

    def leg_point(self, leg):
        name_map = {
            "One": "one", "Two": "two", "Three": "three",
            "Four": "four", "Five": "five", "Six": "six",
        }
        if leg.isChecked() and leg.text() in name_map:
            self.leg = name_map[leg.text()]

    # ── File I/O ─────────────────────────────────────────────────────────────
    def Read_from_txt(self, filename):
        with open(filename + ".txt", "r") as f:
            lines = f.readlines()
        result = []
        for line in lines:
            cols = line.strip().split("\t")
            row = [int(c) for c in cols if c]
            if row:
                result.append(row)
        return result

    def Save_to_txt(self, data, filename):
        with open(filename + '.txt', 'w') as f:
            for row in data:
                for val in row:
                    f.write(str(val) + '\t')
                f.write('\n')
