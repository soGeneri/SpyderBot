# -*- coding: utf-8 -*-
import sys
import math
import threading
from ui_client import Ui_client
import stylesheet
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QImage, QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow
from Client import *
from Calibration import calibrationWindow
from Led import ledWindow
from Face import faceWindow


class MyWindow(QMainWindow, Ui_client):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setupUi(self)
        self.setStyleSheet(stylesheet.MODERN_STYLE)
        self.setWindowTitle("Spider Robot Professional Command Center")
        self.setWindowIcon(QIcon('Picture/logo_Mini.png'))
        self.Video.setScaledContents(True)
        self.Video.setStyleSheet(
            "border: 2px solid #008aff; border-radius: 10px; background: black;")
        self.Video.setPixmap(QPixmap('Picture/Spider_client.png'))

        self.client = Client()
        with open('IP.txt', 'r') as f:
            self.lineEdit_IP_Adress.setText(f.readline().strip())

        # Key state tracking (for reliable release detection)
        self.Key_W = self.Key_A = self.Key_S = self.Key_D = False

        # Last crosshair values (needed when slider changes trigger resend)
        self._att_r = self._att_p = 0.0
        self._pos_x = self._pos_y = 0.0

        self.action_flag = 1
        self.gait_flag   = 1
        self.power_value = [100, 100]

        # ── Button signals ───────────────────────────────────────────────────
        self.Button_Connect.clicked.connect(self.connect)
        self.Button_Video.clicked.connect(self.video)
        self.Button_IMU.clicked.connect(self.imu)
        self.Button_Calibration.clicked.connect(self.showCalibrationWindow)
        self.Button_LED.clicked.connect(self.showLedWindow)
        self.Button_Face_ID.clicked.connect(self.showFaceWindow)
        self.Button_Face_Recognition.clicked.connect(self.faceRecognition)
        self.Button_Sonic.clicked.connect(self.sonic)
        self.Button_Relax.clicked.connect(self.relax)
        self.Button_Buzzer.pressed.connect(self.buzzer)
        self.Button_Buzzer.released.connect(self.buzzer)

        # ── Joystick signals ─────────────────────────────────────────────────
        self.joystick.moved.connect(self._on_joystick_moved)
        self.joystick.released.connect(self._on_joystick_released)

        # ── Crosshair signals ─────────────────────────────────────────────────
        self.attitude_crosshair.changed.connect(self._on_attitude_changed)
        self.position_crosshair.changed.connect(self._on_position_changed)

        # ── Sliders ──────────────────────────────────────────────────────────
        self.slider_head.setSingleStep(1)
        self.slider_head.valueChanged.connect(self.headUpAndDown)

        self.slider_head_1.setSingleStep(1)
        self.slider_head_1.valueChanged.connect(self.headLeftAndRight)

        self.slider_speed.setSingleStep(1)
        self.slider_speed.valueChanged.connect(self.speed)
        self.client.move_speed = str(self.slider_speed.value())

        self.slider_roll.setSingleStep(1)
        self.slider_roll.valueChanged.connect(self.setRoll)

        self.slider_Z.setSingleStep(1)
        self.slider_Z.valueChanged.connect(self.setZ)

        # ── Mode radio buttons ────────────────────────────────────────────────
        self.ButtonActionMode1.setChecked(True)
        self.ButtonActionMode1.toggled.connect(
            lambda: self.actionMode(self.ButtonActionMode1))
        self.ButtonActionMode2.setChecked(False)
        self.ButtonActionMode2.toggled.connect(
            lambda: self.actionMode(self.ButtonActionMode2))
        self.ButtonGaitMode1.setChecked(True)
        self.ButtonGaitMode1.toggled.connect(
            lambda: self.gaitMode(self.ButtonGaitMode1))
        self.ButtonGaitMode2.setChecked(False)
        self.ButtonGaitMode2.toggled.connect(
            lambda: self.gaitMode(self.ButtonGaitMode2))

        # ── Timers ────────────────────────────────────────────────────────────
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_image)

        self.timer_power = QTimer(self)
        self.timer_power.timeout.connect(self.power)

        self.timer_sonic = QTimer(self)
        self.timer_sonic.timeout.connect(self.getSonicData)

    # ── Keyboard ─────────────────────────────────────────────────────────────
    def keyPressEvent(self, event):
        k = event.key()
        if k == Qt.Key.Key_C:
            self.connect()
        elif k == Qt.Key.Key_V:
            self.video()
        elif k == Qt.Key.Key_R:
            self.relax()
        elif k == Qt.Key.Key_L:
            self.showLedWindow()
        elif k == Qt.Key.Key_B:
            self.imu()
        elif k == Qt.Key.Key_F:
            self.faceRecognition()
        elif k == Qt.Key.Key_U:
            self.sonic()
        elif k == Qt.Key.Key_I:
            self.showFaceWindow()
        elif k == Qt.Key.Key_T:
            self.showCalibrationWindow()
        elif k == Qt.Key.Key_Y:
            self.buzzer()

        if not event.isAutoRepeat():
            if k == Qt.Key.Key_W:
                self.Key_W = True
                self.joystick.set_knob(0.0, -1.0)
            elif k == Qt.Key.Key_S:
                self.Key_S = True
                self.joystick.set_knob(0.0, 1.0)
            elif k == Qt.Key.Key_A:
                self.Key_A = True
                self.joystick.set_knob(-1.0, 0.0)
            elif k == Qt.Key.Key_D:
                self.Key_D = True
                self.joystick.set_knob(1.0, 0.0)

    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            return
        k = event.key()
        if k == Qt.Key.Key_W and self.Key_W:
            self.Key_W = False
            self.joystick.set_knob(0.0, 0.0)
        elif k == Qt.Key.Key_S and self.Key_S:
            self.Key_S = False
            self.joystick.set_knob(0.0, 0.0)
        elif k == Qt.Key.Key_A and self.Key_A:
            self.Key_A = False
            self.joystick.set_knob(0.0, 0.0)
        elif k == Qt.Key.Key_D and self.Key_D:
            self.Key_D = False
            self.joystick.set_knob(0.0, 0.0)

    # ── Joystick handlers ─────────────────────────────────────────────────────
    def _on_joystick_moved(self, dx: float, dy: float):
        try:
            x = round(dx * 35)
            y = round(-dy * 35)
            if self.action_flag == 1:
                angle = 0
            else:
                if x != 0 or y != 0:
                    angle = math.degrees(math.atan2(x, y))
                    if -180 <= angle < -90:
                        angle += 360
                    if -90 <= angle <= 90:
                        angle = self._map(angle, -90, 90, -10, 10)
                    else:
                        angle = self._map(angle, 270, 90, 10, -10)
                else:
                    angle = 0
            speed = self.client.move_speed
            command = (cmd.CMD_MOVE + '#' + str(self.gait_flag) + '#' +
                       str(x) + '#' + str(y) + '#' + str(speed) + '#' +
                       str(round(angle)) + '\n')
            self.client.send_data(command)
        except Exception as e:
            print(e)

    def _on_joystick_released(self):
        self._on_joystick_moved(0.0, 0.0)

    # ── Crosshair handlers ────────────────────────────────────────────────────
    def _on_attitude_changed(self, r: float, p: float):
        try:
            self._att_r, self._att_p = r, p
            y = self.slider_roll.value()
            command = (cmd.CMD_ATTITUDE + '#' + str(round(r)) + '#' +
                       str(round(p)) + '#' + str(round(y)) + '\n')
            self.client.send_data(command)
        except Exception as e:
            print(e)

    def _on_position_changed(self, x: float, y: float):
        try:
            self._pos_x, self._pos_y = x, y
            z = self.slider_Z.value()
            command = (cmd.CMD_POSITION + '#' + str(round(x)) + '#' +
                       str(round(y)) + '#' + str(round(z)) + '\n')
            self.client.send_data(command)
        except Exception as e:
            print(e)

    # ── Slider handlers ───────────────────────────────────────────────────────
    def speed(self):
        self.client.move_speed = str(self.slider_speed.value())
        self.label_speed.setText(str(self.slider_speed.value()))

    def setRoll(self):
        self.label_roll.setText(str(self.slider_roll.value()))
        self._on_attitude_changed(self._att_r, self._att_p)

    def setZ(self):
        self.label_Z.setText(str(self.slider_Z.value()))
        self._on_position_changed(self._pos_x, self._pos_y)

    def headUpAndDown(self):
        try:
            angle = str(self.slider_head.value())
            self.label_head.setText(angle)
            command = cmd.CMD_HEAD + '#0#' + angle + '\n'
            self.client.send_data(command)
        except Exception as e:
            print(e)

    def headLeftAndRight(self):
        try:
            angle = str(180 - self.slider_head_1.value())
            self.label_head_1.setText(angle)
            command = cmd.CMD_HEAD + '#1#' + angle + '\n'
            self.client.send_data(command)
        except Exception as e:
            print(e)

    # ── Mode buttons ──────────────────────────────────────────────────────────
    def actionMode(self, mode):
        if mode.text() == "Action Mode 1" and mode.isChecked():
            self.ButtonActionMode1.setChecked(True)
            self.ButtonActionMode2.setChecked(False)
            self.action_flag = 1
        elif mode.text() == "Action Mode 2" and mode.isChecked():
            self.ButtonActionMode1.setChecked(False)
            self.ButtonActionMode2.setChecked(True)
            self.action_flag = 2

    def gaitMode(self, mode):
        if mode.text() == "Gait Mode 1" and mode.isChecked():
            self.ButtonGaitMode1.setChecked(True)
            self.ButtonGaitMode2.setChecked(False)
            self.gait_flag = 1
        elif mode.text() == "Gait Mode 2" and mode.isChecked():
            self.ButtonGaitMode1.setChecked(False)
            self.ButtonGaitMode2.setChecked(True)
            self.gait_flag = 2

    # ── Control actions ───────────────────────────────────────────────────────
    def relax(self):
        try:
            if self.Button_Relax.text() == "Relax":
                self.Button_Relax.setText("Relaxed")
                command = cmd.CMD_SERVOPOWER + '#0\n'
            else:
                self.Button_Relax.setText("Relax")
                command = cmd.CMD_SERVOPOWER + '#1\n'
            self.client.send_data(command)
        except Exception as e:
            print(e)

    def faceRecognition(self):
        try:
            if self.Button_Face_Recognition.text() == "Face Recog":
                self.client.fece_recognition_flag = True
                self.Button_Face_Recognition.setText("Close")
            else:
                self.client.fece_recognition_flag = False
                self.Button_Face_Recognition.setText("Face Recog")
        except Exception as e:
            print(e)

    def buzzer(self):
        if self.Button_Buzzer.text() == 'Buzzer':
            self.client.send_data(cmd.CMD_BUZZER + '#1\n')
            self.Button_Buzzer.setText('Noise')
        else:
            self.client.send_data(cmd.CMD_BUZZER + '#0\n')
            self.Button_Buzzer.setText('Buzzer')

    def imu(self):
        if self.Button_IMU.text() == 'Balance':
            self.client.send_data(cmd.CMD_BALANCE + '#1\n')
            self.Button_IMU.setText("Close")
        else:
            self.client.send_data(cmd.CMD_BALANCE + '#0\n')
            self.Button_IMU.setText('Balance')

    def sonic(self):
        if self.Button_Sonic.text() == 'Sonic':
            self.timer_sonic.start(100)
            self.Button_Sonic.setText('Close')
        else:
            self.timer_sonic.stop()
            self.Button_Sonic.setText('Sonic')

    def getSonicData(self):
        self.client.send_data(cmd.CMD_SONIC + '\n')

    # ── Connection ────────────────────────────────────────────────────────────
    def connect(self):
        try:
            with open('IP.txt', 'w') as f:
                f.write(self.lineEdit_IP_Adress.text())
            if self.Button_Connect.text() == 'Connect':
                self.IP = self.lineEdit_IP_Adress.text()
                self.client.turn_on_client(self.IP)
                self.videoThread = threading.Thread(
                    target=self.client.receiving_video, args=(self.IP,))
                self.instructionThread = threading.Thread(
                    target=self.receive_instruction, args=(self.IP,))
                self.videoThread.start()
                self.instructionThread.start()
                self.Button_Connect.setText('Disconnect')
                self.Button_Connect.setChecked(True)
                self.timer_power.start(3000)
            else:
                try:
                    stop_thread(self.videoThread)
                except Exception:
                    pass
                try:
                    stop_thread(self.instructionThread)
                except Exception:
                    pass
                self.client.tcp_flag = False
                self.client.turn_off_client()
                self.Button_Connect.setText('Connect')
                self.Button_Connect.setChecked(False)
                self.timer_power.stop()
        except Exception as e:
            print(e)

    def receive_instruction(self, ip):
        try:
            self.client.client_socket1.connect((ip, 5002))
            self.client.tcp_flag = True
            print("Connection Successful!")
        except Exception:
            print("Connect to server Failed! Server IP is right? Server is open?")
            self.client.tcp_flag = False
        while True:
            try:
                alldata = self.client.receive_data()
            except Exception:
                self.client.tcp_flag = False
                break
            if alldata == '':
                break
            cmdArray = alldata.split('\n')
            if cmdArray[-1] != "":
                cmdArray = cmdArray[:-1]
            for oneCmd in cmdArray:
                data = oneCmd.split("#")
                if data == "":
                    self.client.tcp_flag = False
                    break
                elif data[0] == cmd.CMD_SONIC:
                    self.label_sonic.setText('Obstacle:' + data[1] + 'cm')
                elif data[0] == cmd.CMD_POWER:
                    try:
                        if len(data) == 3:
                            self.power_value[0] = data[1]
                            self.power_value[1] = data[2]
                    except Exception as e:
                        print(e)

    # ── Video & power ─────────────────────────────────────────────────────────
    def video(self):
        if self.Button_Video.text() == 'Open Video':
            self.timer.start(33)
            self.Button_Video.setText('Close Video')
        else:
            self.timer.stop()
            self.Button_Video.setText('Open Video')

    def power(self):
        try:
            self.client.send_data(cmd.CMD_POWER + '\n')
            self.progress_Power1.setFormat(str(self.power_value[0]) + "V")
            self.progress_Power2.setFormat(str(self.power_value[1]) + "V")
            self.progress_Power1.setValue(
                self._restrict(round((float(self.power_value[0]) - 5.00) / 3.40 * 100), 0, 100))
            self.progress_Power2.setValue(
                self._restrict(round((float(self.power_value[1]) - 7.00) / 1.40 * 100), 0, 100))
        except Exception as e:
            print(e)

    def refresh_image(self):
        if not self.client.video_flag:
            h, w, _ = self.client.image.shape
            cv2.cvtColor(self.client.image, cv2.COLOR_BGR2RGB, self.client.image)
            QImg = QImage(self.client.image.data.tobytes(), w, h,
                          3 * w, QImage.Format.Format_RGB888)
            self.Video.setPixmap(QPixmap.fromImage(QImg))
            self.client.video_flag = True

    # ── Sub-windows ───────────────────────────────────────────────────────────
    def showCalibrationWindow(self):
        self.client.send_data(cmd.CMD_CALIBRATION + '\n')
        self.calibrationWindow = calibrationWindow(self.client)
        self.calibrationWindow.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.calibrationWindow.show()

    def showLedWindow(self):
        try:
            self.ledWindow = ledWindow(self.client)
            self.ledWindow.setWindowModality(Qt.WindowModality.ApplicationModal)
            self.ledWindow.show()
        except Exception as e:
            print(e)

    def showFaceWindow(self):
        try:
            self.faceWindow = faceWindow(self.client)
            self.faceWindow.setWindowModality(Qt.WindowModality.ApplicationModal)
            self.faceWindow.show()
            self.client.fece_id = True
        except Exception as e:
            print(e)

    # ── Lifecycle ─────────────────────────────────────────────────────────────
    def closeEvent(self, event):
        try:
            self.timer.stop()
            self.timer_power.stop()
        except Exception:
            pass
        try:
            stop_thread(self.videoThread)
        except Exception:
            pass
        try:
            stop_thread(self.instructionThread)
        except Exception:
            pass
        self.client.turn_off_client()
        QApplication.instance().quit()

    # ── Utilities ─────────────────────────────────────────────────────────────
    def _map(self, value, from_low, from_high, to_low, to_high):
        return (to_high - to_low) * (value - from_low) / (from_high - from_low) + to_low

    def _restrict(self, var, v_min, v_max):
        return max(v_min, min(v_max, var))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myshow = MyWindow()
    myshow.show()
    sys.exit(app.exec())
