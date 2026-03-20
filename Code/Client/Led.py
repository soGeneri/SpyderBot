# -*- coding: utf-8 -*-
"""LED sub-window and ColorDialog — moved from Main.py."""
import numpy as np
from ui_led import Ui_led
from Command import COMMAND as cmd
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout


class ColorDialog(QtWidgets.QColorDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setOptions(
            self.options() | QtWidgets.QColorDialog.ColorDialogOption.DontUseNativeDialog)
        for child in self.findChildren(QtWidgets.QWidget):
            classname = child.metaObject().className()
            if classname not in ("QColorPicker", "QColorLuminancePicker"):
                child.hide()


class ledWindow(QMainWindow, Ui_led):
    def __init__(self, client):
        super(ledWindow, self).__init__()
        self.setupUi(self)
        self.client = client
        self.setWindowIcon(QIcon('Picture/logo_Mini.png'))
        self.hsl = [0, 0, 1]
        self.rgb = [0, 0, 0]

        self.dial_color.setPageStep(10)
        self.dial_color.setNotchTarget(10)
        self.dial_color.valueChanged.connect(self.dialValueChanged)

        composite_2f = lambda f, g: lambda t: g(f(t))
        self.hsl_to_rgb255  = composite_2f(self.hsl_to_rgb01,   self.rgb01_to_rgb255)
        self.hsl_to_rgbhex  = composite_2f(self.hsl_to_rgb255,  self.rgb255_to_rgbhex)
        self.rgb255_to_hsl  = composite_2f(self.rgb255_to_rgb01, self.rgb01_to_hsl)
        self.rgbhex_to_hsl  = composite_2f(self.rgbhex_to_rgb255, self.rgb255_to_hsl)

        self.colordialog = ColorDialog()
        self.colordialog.currentColorChanged.connect(self.onCurrentColorChanged)
        lay = QVBoxLayout(self.widget)
        lay.addWidget(self.colordialog, alignment=Qt.AlignmentFlag.AlignCenter)

        self.pushButtonLightsOut.clicked.connect(self.lightsOut)
        self.radioButtonOne.setChecked(True)
        self.radioButtonOne.toggled.connect(
            lambda: self.ledMode(self.radioButtonOne))
        self.radioButtonTwo.setChecked(False)
        self.radioButtonTwo.toggled.connect(
            lambda: self.ledMode(self.radioButtonTwo))
        self.radioButtonThree.setChecked(False)
        self.radioButtonThree.toggled.connect(
            lambda: self.ledMode(self.radioButtonThree))
        self.radioButtonFour.setChecked(False)
        self.radioButtonFour.toggled.connect(
            lambda: self.ledMode(self.radioButtonFour))
        self.radioButtonFive.setChecked(False)
        self.radioButtonFive.toggled.connect(
            lambda: self.ledMode(self.radioButtonFive))

    def lightsOut(self):
        command = cmd.CMD_LED_MOD + '#0\n'
        self.client.send_data(command)

    def ledMode(self, index):
        mode_map = {
            "Mode 1": '1', "Mode 2": '2', "Mode 3": '3',
            "Mode 4": '4', "Mode 5": '5',
        }
        if index.isChecked() and index.text() in mode_map:
            command = cmd.CMD_LED_MOD + '#' + mode_map[index.text()] + '\n'
            self.client.send_data(command)

    def mode1Color(self):
        if self.radioButtonOne.isChecked() or self.radioButtonThree.isChecked():
            command = (cmd.CMD_LED + '#' + str(self.rgb[0]) +
                       '#' + str(self.rgb[1]) + '#' + str(self.rgb[2]) + '\n')
            self.client.send_data(command)

    def onCurrentColorChanged(self, color):
        try:
            self.rgb = self.rgbhex_to_rgb255(color.name())
            self.hsl = self.rgb255_to_hsl(self.rgb)
            self.changeHSLText()
            self.changeRGBText()
            self.mode1Color()
            self._update_preview()
        except Exception as e:
            print(e)

    def dialValueChanged(self):
        try:
            self.lineEdit_H.setText(str(self.dial_color.value()))
            self.changeHSL()
            self.hex = self.hsl_to_rgbhex((self.hsl[0], self.hsl[1], self.hsl[2]))
            self.rgb = self.rgbhex_to_rgb255(self.hex)
            self.changeRGBText()
            self.mode1Color()
            self._update_preview()
        except Exception as e:
            print(e)

    def _update_preview(self):
        self.color_preview.setColor(
            int(self.rgb[0]), int(self.rgb[1]), int(self.rgb[2]))

    def changeHSL(self):
        self.hsl[0] = float(self.lineEdit_H.text())
        self.hsl[1] = float(self.lineEdit_S.text())
        self.hsl[2] = float(self.lineEdit_L.text())

    def changeHSLText(self):
        self.lineEdit_H.setText(str(int(self.hsl[0])))
        self.lineEdit_S.setText(str(round(self.hsl[1], 1)))
        self.lineEdit_L.setText(str(round(self.hsl[2], 1)))

    def changeRGBText(self):
        self.lineEdit_R.setText(str(int(self.rgb[0])))
        self.lineEdit_G.setText(str(int(self.rgb[1])))
        self.lineEdit_B.setText(str(int(self.rgb[2])))

    # ── Color math ──────────────────────────────────────────────────────────
    def rgb255_to_rgbhex(self, rgb) -> str:
        f = lambda n: 0 if n < 0 else 255 if n > 255 else int(n)
        return '#%02x%02x%02x' % (f(rgb[0]), f(rgb[1]), f(rgb[2]))

    def rgbhex_to_rgb255(self, rgbhex: str):
        if rgbhex[0] == '#':
            rgbhex = rgbhex[1:]
        return np.array((int(rgbhex[0:2], 16),
                         int(rgbhex[2:4], 16),
                         int(rgbhex[4:6], 16)))

    def rgb01_to_rgb255(self, rgb):
        return rgb * 255

    def rgb255_to_rgb01(self, rgb):
        return rgb / 255

    def rgb01_to_hsl(self, rgb):
        r, g, b = rgb
        lmin, lmax = min(r, g, b), max(r, g, b)
        if lmax == lmin:
            h = 0
        elif lmin == b:
            h = 60 + 60 * (g - r) / (lmax - lmin)
        elif lmin == r:
            h = 180 + 60 * (b - g) / (lmax - lmin)
        elif lmin == g:
            h = 300 + 60 * (r - b) / (lmax - lmin)
        else:
            h = 0
        s = lmax - lmin
        l = (lmax + lmin) / 2
        return np.array((h, s, l))

    def hsl_to_rgb01(self, hsl):
        h, s, l = hsl
        lmin = l - s / 2
        lmax = l + s / 2
        ldif = lmax - lmin
        if h < 60:
            r, g, b = lmax, lmin + ldif * h / 60, lmin
        elif h < 120:
            r, g, b = lmin + ldif * (120 - h) / 60, lmax, lmin
        elif h < 180:
            r, g, b = lmin, lmax, lmin + ldif * (h - 120) / 60
        elif h < 240:
            r, g, b = lmin, lmin + ldif * (240 - h) / 60, lmax
        elif h < 300:
            r, g, b = lmin + ldif * (h - 240) / 60, lmin, lmax
        else:
            r, g, b = lmax, lmin, lmin + ldif * (360 - h) / 60
        return np.array((r, g, b))
