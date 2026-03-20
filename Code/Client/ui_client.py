# -*- coding: utf-8 -*-
"""Main window UI — layout-based replacement for the old setGeometry version."""

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QLineEdit, QSlider, QProgressBar,
    QRadioButton, QGroupBox, QHBoxLayout, QVBoxLayout, QGridLayout,
    QSizePolicy,
)
from widgets import JoystickWidget, CrosshairWidget


class Ui_client(object):
    def setupUi(self, client):
        client.setObjectName("client")
        client.setMinimumSize(1000, 800)
        client.resize(1200, 850)

        central = QWidget(client)
        client.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        # ── LEFT PANEL ──────────────────────────────────────────────────────
        left_panel = QVBoxLayout()
        left_panel.setSpacing(6)

        # Video label
        self.Video = QLabel()
        self.Video.setObjectName("Video")
        self.Video.setMinimumSize(400, 300)
        self.Video.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.Video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_panel.addWidget(self.Video, stretch=5)

        # Connection bar
        conn_bar = QHBoxLayout()
        self.lineEdit_IP_Adress = QLineEdit()
        self.lineEdit_IP_Adress.setObjectName("lineEdit_IP_Adress")
        self.lineEdit_IP_Adress.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lineEdit_IP_Adress.setFixedWidth(140)

        self.Button_Connect = QPushButton("Connect")
        self.Button_Connect.setObjectName("Button_Connect")
        self.Button_Connect.setCheckable(True)

        self.Button_Video = QPushButton("Open Video")
        self.Button_Video.setObjectName("Button_Video")

        self.Button_Relax = QPushButton("Relax")
        self.Button_Relax.setObjectName("Button_Relax")

        self.Button_Calibration = QPushButton("Calibration")
        self.Button_Calibration.setObjectName("Button_Calibration")

        conn_bar.addWidget(self.lineEdit_IP_Adress)
        conn_bar.addWidget(self.Button_Connect)
        conn_bar.addWidget(self.Button_Video)
        conn_bar.addWidget(self.Button_Relax)
        conn_bar.addWidget(self.Button_Calibration)
        conn_bar.addStretch()
        left_panel.addLayout(conn_bar)

        # Tools bar
        tools_bar = QHBoxLayout()
        self.Button_LED = QPushButton("LED")
        self.Button_LED.setObjectName("Button_LED")

        self.Button_Face_ID = QPushButton("Face ID")
        self.Button_Face_ID.setObjectName("Button_Face_ID")

        self.Button_Face_Recognition = QPushButton("Face Recog")
        self.Button_Face_Recognition.setObjectName("Button_Face_Recognition")

        self.Button_IMU = QPushButton("Balance")
        self.Button_IMU.setObjectName("Button_IMU")

        self.Button_Sonic = QPushButton("Sonic")
        self.Button_Sonic.setObjectName("Button_Sonic")

        self.Button_Buzzer = QPushButton("Buzzer")
        self.Button_Buzzer.setObjectName("Button_Buzzer")

        self.label_sonic = QLabel("Obstacle: 0 cm")
        self.label_sonic.setObjectName("label_sonic")
        self.label_sonic.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for btn in (self.Button_LED, self.Button_Face_ID,
                    self.Button_Face_Recognition, self.Button_IMU,
                    self.Button_Sonic, self.Button_Buzzer):
            tools_bar.addWidget(btn)
        tools_bar.addWidget(self.label_sonic)
        tools_bar.addStretch()
        left_panel.addLayout(tools_bar)

        # Bottom bar: modes | power | joystick | head/speed
        bottom_bar = QHBoxLayout()
        bottom_bar.setSpacing(8)

        # Mode group
        mode_group = QGroupBox("Mode")
        mode_layout = QVBoxLayout(mode_group)
        self.ButtonGaitMode1   = QRadioButton("Gait Mode 1")
        self.ButtonGaitMode2   = QRadioButton("Gait Mode 2")
        self.ButtonActionMode1 = QRadioButton("Action Mode 1")
        self.ButtonActionMode2 = QRadioButton("Action Mode 2")
        self.ButtonGaitMode1.setObjectName("ButtonGaitMode1")
        self.ButtonGaitMode2.setObjectName("ButtonGaitMode2")
        self.ButtonActionMode1.setObjectName("ButtonActionMode1")
        self.ButtonActionMode2.setObjectName("ButtonActionMode2")
        for rb in (self.ButtonGaitMode1, self.ButtonGaitMode2,
                   self.ButtonActionMode1, self.ButtonActionMode2):
            mode_layout.addWidget(rb)
        bottom_bar.addWidget(mode_group)

        # Power group
        power_group = QGroupBox("Power")
        power_layout = QVBoxLayout(power_group)
        self.label_Load  = QLabel("Load")
        self.label_RasPi = QLabel("RasPi")
        self.label_Load.setObjectName("label_Load")
        self.label_RasPi.setObjectName("label_RasPi")
        self.progress_Power1 = QProgressBar()
        self.progress_Power1.setObjectName("progress_Power1")
        self.progress_Power1.setValue(100)
        self.progress_Power1.setFormat("")
        self.progress_Power2 = QProgressBar()
        self.progress_Power2.setObjectName("progress_Power2")
        self.progress_Power2.setValue(100)
        self.progress_Power2.setFormat("")
        for w in (self.label_Load, self.progress_Power1,
                  self.label_RasPi, self.progress_Power2):
            power_layout.addWidget(w)
        power_layout.addStretch()
        bottom_bar.addWidget(power_group)

        # Joystick
        self.joystick = JoystickWidget()
        self.joystick.setFixedSize(230, 230)
        bottom_bar.addWidget(self.joystick)

        # Head / Speed group
        hs_group = QGroupBox("Head / Speed")
        hs_layout = QHBoxLayout(hs_group)

        # Tilt (slider_head, vertical)
        tilt_col = QVBoxLayout()
        tilt_col.addWidget(QLabel("Tilt"), alignment=Qt.AlignmentFlag.AlignCenter)
        self.slider_head = QSlider(Qt.Orientation.Vertical)
        self.slider_head.setObjectName("slider_head")
        self.slider_head.setMinimum(50)
        self.slider_head.setMaximum(180)
        self.slider_head.setValue(90)
        self.label_head = QLabel("90")
        self.label_head.setObjectName("label_head")
        self.label_head.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tilt_col.addWidget(self.slider_head, alignment=Qt.AlignmentFlag.AlignCenter)
        tilt_col.addWidget(self.label_head,  alignment=Qt.AlignmentFlag.AlignCenter)

        # Pan (slider_head_1, horizontal)
        pan_col = QVBoxLayout()
        pan_col.addWidget(QLabel("Pan"), alignment=Qt.AlignmentFlag.AlignCenter)
        self.slider_head_1 = QSlider(Qt.Orientation.Horizontal)
        self.slider_head_1.setObjectName("slider_head_1")
        self.slider_head_1.setMinimum(0)
        self.slider_head_1.setMaximum(180)
        self.slider_head_1.setValue(90)
        self.label_head_1 = QLabel("90")
        self.label_head_1.setObjectName("label_head_1")
        self.label_head_1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pan_col.addWidget(self.slider_head_1)
        pan_col.addWidget(self.label_head_1, alignment=Qt.AlignmentFlag.AlignCenter)

        # Speed (slider_speed, vertical)
        spd_col = QVBoxLayout()
        spd_col.addWidget(QLabel("Speed"), alignment=Qt.AlignmentFlag.AlignCenter)
        self.slider_speed = QSlider(Qt.Orientation.Vertical)
        self.slider_speed.setObjectName("slider_speed")
        self.slider_speed.setMinimum(2)
        self.slider_speed.setMaximum(10)
        self.slider_speed.setValue(8)
        self.label_speed = QLabel("8")
        self.label_speed.setObjectName("label_speed")
        self.label_speed.setAlignment(Qt.AlignmentFlag.AlignCenter)
        spd_col.addWidget(self.slider_speed, alignment=Qt.AlignmentFlag.AlignCenter)
        spd_col.addWidget(self.label_speed,  alignment=Qt.AlignmentFlag.AlignCenter)

        hs_layout.addLayout(tilt_col)
        hs_layout.addLayout(pan_col)
        hs_layout.addLayout(spd_col)
        bottom_bar.addWidget(hs_group)

        left_panel.addLayout(bottom_bar)

        # ── RIGHT PANEL ─────────────────────────────────────────────────────
        right_panel = QVBoxLayout()
        right_panel.setSpacing(8)

        # Attitude group
        att_group = QGroupBox("Attitude")
        att_layout = QVBoxLayout(att_group)
        self.attitude_crosshair = CrosshairWidget((-15, 15), (-15, 15))
        self.attitude_crosshair.setObjectName("attitude_crosshair")
        att_layout.addWidget(self.attitude_crosshair)

        roll_row = QHBoxLayout()
        roll_row.addWidget(QLabel("Roll:"))
        self.slider_roll = QSlider(Qt.Orientation.Horizontal)
        self.slider_roll.setObjectName("slider_roll")
        self.slider_roll.setMinimum(-15)
        self.slider_roll.setMaximum(15)
        self.slider_roll.setValue(0)
        self.label_roll = QLabel("0")
        self.label_roll.setObjectName("label_roll")
        self.label_roll.setFixedWidth(30)
        self.label_roll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        roll_row.addWidget(self.slider_roll)
        roll_row.addWidget(self.label_roll)
        att_layout.addLayout(roll_row)
        right_panel.addWidget(att_group)

        # Position group
        pos_group = QGroupBox("Position")
        pos_layout = QVBoxLayout(pos_group)
        self.position_crosshair = CrosshairWidget((-40, 40), (-40, 40))
        self.position_crosshair.setObjectName("position_crosshair")
        pos_layout.addWidget(self.position_crosshair)

        z_row = QHBoxLayout()
        z_row.addWidget(QLabel("Z:"))
        self.slider_Z = QSlider(Qt.Orientation.Horizontal)
        self.slider_Z.setObjectName("slider_Z")
        self.slider_Z.setMinimum(-20)
        self.slider_Z.setMaximum(20)
        self.slider_Z.setValue(0)
        self.label_Z = QLabel("0")
        self.label_Z.setObjectName("label_Z")
        self.label_Z.setFixedWidth(30)
        self.label_Z.setAlignment(Qt.AlignmentFlag.AlignCenter)
        z_row.addWidget(self.slider_Z)
        z_row.addWidget(self.label_Z)
        pos_layout.addLayout(z_row)
        right_panel.addWidget(pos_group)
        right_panel.addStretch()

        # ── Assemble root layout ─────────────────────────────────────────────
        root.addLayout(left_panel, stretch=3)

        right_widget = QWidget()
        right_widget.setFixedWidth(280)
        right_widget.setLayout(right_panel)
        root.addWidget(right_widget)

        self.retranslateUi(client)
        QtCore.QMetaObject.connectSlotsByName(client)

    def retranslateUi(self, client):
        client.setWindowTitle("Spider Robot Professional Command Center")
