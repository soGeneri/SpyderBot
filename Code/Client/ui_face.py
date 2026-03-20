# -*- coding: utf-8 -*-
"""Face ID window UI — layout-based."""

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QLineEdit,
    QHBoxLayout, QVBoxLayout, QSizePolicy,
)


class Ui_Face(object):
    def setupUi(self, Face):
        Face.setObjectName("Face")
        Face.resize(650, 320)

        central = QWidget(Face)
        Face.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        # Video label (left, large)
        self.label_video = QLabel("Video")
        self.label_video.setObjectName("label_video")
        self.label_video.setMinimumSize(400, 300)
        self.label_video.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.label_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.label_video, stretch=2)

        # Right column: photo + name + button
        right_col = QVBoxLayout()

        self.label_photo = QLabel("Photo")
        self.label_photo.setObjectName("label_photo")
        self.label_photo.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.label_photo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_col.addWidget(self.label_photo, stretch=1)

        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("Name:"))
        self.lineEdit = QLineEdit()
        self.lineEdit.setObjectName("lineEdit")
        name_row.addWidget(self.lineEdit)
        right_col.addLayout(name_row)

        self.Button_Read_Face = QPushButton("Read Face")
        self.Button_Read_Face.setObjectName("Button_Read_Face")
        right_col.addWidget(self.Button_Read_Face)

        root.addLayout(right_col, stretch=1)

        self.retranslateUi(Face)
        QtCore.QMetaObject.connectSlotsByName(Face)

    def retranslateUi(self, Face):
        Face.setWindowTitle("Face ID")
