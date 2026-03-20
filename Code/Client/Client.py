# -*- coding: utf-8 -*-
import math
import socket
import struct
import threading
from PID import *
from Face import *
import numpy as np
from Thread import *
from Command import COMMAND as cmd
class Client:
    def __init__(self):
        self.face=Face()
        self.pid=Incremental_PID(1,0,0.0025)
        self.tcp_flag=False
        self.video_flag=True
        self.fece_id=False
        self.fece_recognition_flag = False
        self.image=''
    def turn_on_client(self,ip):
        self.client_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print (ip)
    def turn_off_client(self):
        try:
            self.client_socket.shutdown(2)
            self.client_socket1.shutdown(2)
            self.client_socket.close()
            self.client_socket1.close()
        except Exception as e:
            print(e)
    def is_valid_image_4_bytes(self,buf):
        return len(buf) > 2 and buf[:2] == b'\xff\xd8' and buf[-2:] == b'\xff\xd9'
    def receiving_video(self,ip):
        try:
            self.client_socket.connect((ip, 8002))
            self.connection = self.client_socket.makefile('rb')
        except:
            #print ("command port connect failed")
            pass
        while True:
            try:
                stream_bytes= self.connection.read(4)
                leng=struct.unpack('<L', stream_bytes[:4])
                jpg=self.connection.read(leng[0])
                if self.is_valid_image_4_bytes(jpg):
                    if self.video_flag:
                        self.image = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                        if self.fece_id == False and self.fece_recognition_flag:
                            self.face.face_detect(self.image)
                        self.video_flag=False
            except BaseException as e:
                print (e)
                break
    def send_data(self,data):
        if self.tcp_flag:
            try:
                self.client_socket1.send(data.encode('utf-8'))
            except Exception as e:
                print(e)
    def receive_data(self):
        data=""
        data=self.client_socket1.recv(1024).decode('utf-8')
        return data

if __name__ == '__main__':
    c=Client()
    c.face_recognition()
