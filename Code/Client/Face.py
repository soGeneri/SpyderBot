import os
import sys
import cv2
import time
import numpy as np
from ui_face import Ui_Face
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon, QImage, QPixmap
from PyQt6.QtWidgets import QMainWindow, QMessageBox


class Face:
    def __init__(self):
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.recognizer.read('Face/face.yml')
        self.detector = cv2.CascadeClassifier("Face/haarcascade_frontalface_default.xml")
        self.name = self.Read_from_txt('Face/name')

    def Read_from_txt(self, filename):
        file1 = open(filename + ".txt", "r")
        list_row = file1.readlines()
        list_source = []
        for i in range(len(list_row)):
            column_list = list_row[i].strip().split("\t")
            list_source.append(column_list)
        for i in range(len(list_source)):
            for j in range(len(list_source[i])):
                list_source[i][j] = str(list_source[i][j])
        file1.close()
        return list_source

    def Save_to_txt(self, list, filename):
        file2 = open(filename + '.txt', 'w')
        for i in range(len(list)):
            for j in range(len(list[i])):
                file2.write(str(list[i][j]))
                file2.write('\t')
            file2.write('\n')
        file2.close()

    def getImagesAndLabels(self, path='Face'):
        imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
        faceSamples = []
        labels = []
        for imagePath in imagePaths:
            if os.path.split(imagePath)[-1].split(".")[1] == "jpg":
                id = int(os.path.split(imagePath)[-1].split(".")[0])
                img = cv2.imread(imagePath)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = self.detector.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)
                for (x, y, w, h) in faces:
                    faceSamples.append(gray[y:y + h, x:x + w])
                    labels.append(id)
        return faceSamples, labels

    def trainImage(self):
        faces, labels = self.getImagesAndLabels()
        self.recognizer.train(faces, np.array(labels))
        self.recognizer.write('Face/face.yml')
        self.recognizer.read('Face/face.yml')
        print("\n  {0} faces trained.".format(len(np.unique(labels))))

    def face_detect(self, img):
        try:
            if sys.platform.startswith('win') or sys.platform.startswith('darwin'):
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = self.detector.detectMultiScale(gray, 1.2, 5)
                if len(faces) > 0:
                    for (x, y, w, h) in faces:
                        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        id, confidence = self.recognizer.predict(gray[y:y + h, x:x + w])
                        if confidence > 100:
                            cv2.putText(img, str("unknow"), (x + 5, y + h + 30),
                                        cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)
                        else:
                            cv2.putText(img, self.name[int(id)][1], (x + 5, y + h + 30),
                                        cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)
        except Exception as e:
            print(e)


class faceWindow(QMainWindow, Ui_Face):
    def __init__(self, client):
        super(faceWindow, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon('Picture/logo_Mini.png'))
        self.Button_Read_Face.clicked.connect(self.readFace)
        self.client = client
        self.face_image = ''
        self.photoCount = 0
        self.timeout = 0
        self.name = ''
        self.readFaceFlag = False

        self.timer1 = QTimer(self)
        self.timer1.timeout.connect(self.faceDetection)
        self.timer1.start(10)

        self.timer2 = QTimer(self)
        self.timer2.timeout.connect(self.facePhoto)

    def closeEvent(self, event):
        self.timer1.stop()
        self.client.fece_id = False

    def readFace(self):
        try:
            if self.Button_Read_Face.text() == "Read Face":
                self.Button_Read_Face.setText("Reading")
                self.timer2.start(10)
                self.timeout = time.time()
            else:
                self.timer2.stop()
                if self.photoCount != 0:
                    self.Button_Read_Face.setText("Waiting ")
                    self.client.face.trainImage()
                    QMessageBox.information(self, "Message", "success",
                                            QMessageBox.StandardButton.Yes)
                self.Button_Read_Face.setText("Read Face")
                self.name = self.lineEdit.setText("")
                self.photoCount == 0
        except Exception as e:
            print(e)

    def facePhoto(self):
        try:
            if self.photoCount == 30:
                self.photoCount == 0
                self.timer2.stop()
                self.Button_Read_Face.setText("Waiting ")
                self.client.face.trainImage()
                QMessageBox.information(self, "Message", "success",
                                        QMessageBox.StandardButton.Yes)
                self.Button_Read_Face.setText("Read Face")
                self.name = self.lineEdit.setText("")
            if len(self.face_image) > 0:
                self.name = self.lineEdit.text()
                if len(self.name) > 0:
                    height, width = self.face_image.shape[:2]
                    QImg = QImage(self.face_image.data.tobytes(), width, height,
                                  3 * width, QImage.Format.Format_RGB888)
                    self.label_photo.setPixmap(QPixmap.fromImage(QImg))
                    second = int(time.time() - self.timeout)
                    if second > 1:
                        self.saveFcaePhoto()
                        self.timeout = time.time()
                    else:
                        self.Button_Read_Face.setText(
                            "Reading " + str(1 - second) + "S   " + str(self.photoCount) + "/30")
                    self.face_image = ''
                else:
                    QMessageBox.information(self, "Message", "Please enter your name",
                                            QMessageBox.StandardButton.Yes)
                    self.timer2.stop()
                    self.Button_Read_Face.setText("Read Face")
        except Exception as e:
            print(e)

    def saveFcaePhoto(self):
        cv2.cvtColor(self.face_image, cv2.COLOR_BGR2RGB, self.face_image)
        cv2.imwrite('Face/' + str(len(self.client.face.name)) + '.jpg', self.face_image)
        self.client.face.name.append(
            [str(len(self.client.face.name)), str(self.name)])
        self.client.face.Save_to_txt(self.client.face.name, 'Face/name')
        self.client.face.name = self.client.face.Read_from_txt('Face/name')
        self.photoCount += 1
        self.Button_Read_Face.setText(
            "Reading " + str(0) + " S " + str(self.photoCount) + "/30")

    def faceDetection(self):
        try:
            if len(self.client.image) > 0:
                gray = cv2.cvtColor(self.client.image, cv2.COLOR_BGR2GRAY)
                faces = self.client.face.detector.detectMultiScale(gray, 1.2, 5)
                if len(faces) > 0:
                    for (x, y, w, h) in faces:
                        self.face_image = self.client.image[y - 5:y + h + 5, x - 5:x + w + 5]
                        cv2.rectangle(self.client.image,
                                      (x - 20, y - 20), (x + w + 20, y + h + 20),
                                      (0, 255, 0), 2)
                if self.client.video_flag == False:
                    height, width, bytesPerComponent = self.client.image.shape
                    cv2.cvtColor(self.client.image, cv2.COLOR_BGR2RGB, self.client.image)
                    QImg = QImage(self.client.image.data.tobytes(), width, height,
                                  3 * width, QImage.Format.Format_RGB888)
                    self.label_video.setPixmap(QPixmap.fromImage(QImg))
                    self.client.video_flag = True
        except Exception as e:
            print(e)


if __name__ == '__main__':
    f = Face()
    f.trainImage()
