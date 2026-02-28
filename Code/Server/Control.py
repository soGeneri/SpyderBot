# -*- coding: utf-8 -*-
import time
import math
import smbus
from IMU import *
from PID import *
import threading
from Servo import*
import numpy as np
import RPi.GPIO as GPIO
from Command import COMMAND as cmd
class Control:
    def __init__(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        self.GPIO_4 = 4
        GPIO.setup(self.GPIO_4,GPIO.OUT)
        GPIO.output(self.GPIO_4,False)
        self.imu=IMU()
        self.servo=Servo()
        self.move_flag=0x01
        self.relax_flag=False
        self.pid = Incremental_PID(0.500,0.00,0.0025)
        self.flag=0x00
        self.timeout=0
        self.height=-25
        self.body_point=[[137.1 ,189.4 , self.height], [225, 0, self.height], [137.1 ,-189.4 , self.height], 
                         [-137.1 ,-189.4 , self.height], [-225, 0, self.height], [-137.1 ,189.4 , self.height]]
        self.calibration_leg_point=self.readFromTxt('point')
        self.leg_point=[[140, 0, 0], [140, 0, 0], [140, 0, 0], [140, 0, 0], [140, 0, 0], [140, 0, 0]]
        self.calibration_angle=[[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
        self.angle=[[90,0,0],[90,0,0],[90,0,0],[90,0,0],[90,0,0],[90,0,0]]
        self.order=['','','','','','']
        # Pre-computed sin/cos for each leg's mounting angle (deg): 54,0,-54,-126,180,126
        _angles = [54, 0, -54, -126, 180, 126]
        self._leg_cos = [math.cos(a * math.pi / 180) for a in _angles]
        self._leg_sin = [math.sin(a * math.pi / 180) for a in _angles]
        # Hip x-offsets per leg (mm from body centre to hip pivot)
        self._leg_offset_x = [-94, -85, -94, -94, -85, -94]
        # Constant foot positions used by postureBalance (3×6, columns = legs)
        self._footpoint_struc = np.mat([[137.1,  189.4, 0],
                                        [225,     0,    0],
                                        [137.1, -189.4, 0],
                                        [-137.1,-189.4, 0],
                                        [-225,    0,    0],
                                        [-137.1, 189.4, 0]]).T
        self.calibration()
        self.setLegAngle()
        self.Thread_conditiona=threading.Thread(target=self.condition)
    def readFromTxt(self,filename):
        file1 = open(filename + ".txt", "r")
        list_row = file1.readlines()
        list_source = []
        for i in range(len(list_row)):
            column_list = list_row[i].strip().split("\t")
            list_source.append(column_list)
        for i in range(len(list_source)):
            for j in range(len(list_source[i])):
                list_source[i][j] = int(list_source[i][j])
        file1.close()
        return list_source

    def saveToTxt(self,list, filename):
        file2 = open(filename + '.txt', 'w')
        for i in range(len(list)):
            for j in range(len(list[i])):
                file2.write(str(list[i][j]))
                file2.write('\t')
            file2.write('\n')
        file2.close()
        
    def coordinateToAngle(self,ox,oy,oz,l1=33,l2=90,l3=110):
        a=math.pi/2-math.atan2(oz,oy)
        x_3=0
        x_4=l1*math.sin(a)
        x_5=l1*math.cos(a)
        l23=math.sqrt((oz-x_5)**2+(oy-x_4)**2+(ox-x_3)**2)
        w=self.restriction((ox-x_3)/l23,-1,1)
        v=self.restriction((l2*l2+l23*l23-l3*l3)/(2*l2*l23),-1,1)
        u=self.restriction((l2**2+l3**2-l23**2)/(2*l3*l2),-1,1)
        b=math.asin(round(w,2))-math.acos(round(v,2))
        c=math.pi-math.acos(round(u,2))
        a=round(math.degrees(a))
        b=round(math.degrees(b))
        c=round(math.degrees(c))
        return a,b,c
    def angleToCoordinate(self,a,b,c,l1=33,l2=90,l3=110):
        a=math.pi/180*a
        b=math.pi/180*b
        c=math.pi/180*c
        ox=round(l3*math.sin(b+c)+l2*math.sin(b))
        oy=round(l3*math.sin(a)*math.cos(b+c)+l2*math.sin(a)*math.cos(b)+l1*math.sin(a))
        oz=round(l3*math.cos(a)*math.cos(b+c)+l2*math.cos(a)*math.cos(b)+l1*math.cos(a))
        return ox,oy,oz
    def calibration(self):
        self.leg_point=[[140, 0, 0], [140, 0, 0], [140, 0, 0], [140, 0, 0], [140, 0, 0], [140, 0, 0]]
        for i in range(6):
            self.calibration_angle[i][0],self.calibration_angle[i][1],self.calibration_angle[i][2]=self.coordinateToAngle(-self.calibration_leg_point[i][2],
                                                                                                                          self.calibration_leg_point[i][0],
                                                                                                                          self.calibration_leg_point[i][1])
        for i in range(6):
            self.angle[i][0],self.angle[i][1],self.angle[i][2]=self.coordinateToAngle(-self.leg_point[i][2],
                                                                                      self.leg_point[i][0],
                                                                                      self.leg_point[i][1])
        
        for i in range(6):
            self.calibration_angle[i][0]=self.calibration_angle[i][0]-self.angle[i][0]
            self.calibration_angle[i][1]=self.calibration_angle[i][1]-self.angle[i][1]
            self.calibration_angle[i][2]=self.calibration_angle[i][2]-self.angle[i][2]
    
    def setLegAngle(self):
        if self.checkPoint():
            for i in range(6):
                self.angle[i][0],self.angle[i][1],self.angle[i][2]=self.coordinateToAngle(-self.leg_point[i][2],
                                                                                          self.leg_point[i][0],
                                                                                          self.leg_point[i][1])
            for i in range(3):
                self.angle[i][0]=self.restriction(self.angle[i][0]+self.calibration_angle[i][0],0,180)
                self.angle[i][1]=self.restriction(90-(self.angle[i][1]+self.calibration_angle[i][1]),0,180)
                self.angle[i][2]=self.restriction(self.angle[i][2]+self.calibration_angle[i][2],0,180)
                self.angle[i+3][0]=self.restriction(self.angle[i+3][0]+self.calibration_angle[i+3][0],0,180)
                self.angle[i+3][1]=self.restriction(90+self.angle[i+3][1]+self.calibration_angle[i+3][1],0,180)
                self.angle[i+3][2]=self.restriction(180-(self.angle[i+3][2]+self.calibration_angle[i+3][2]),0,180)
             
            # Write all 18 servos in 4 batched I2C block writes instead of 72 individual writes
            self.servo.setLegServoBatch(self.angle)
        else:
            print("This coordinate point is out of the active range")
    def checkPoint(self):
        flag=True
        leg_lenght=[0,0,0,0,0,0]  
        for i in range(6):
          leg_lenght[i]=math.sqrt(self.leg_point[i][0]**2+self.leg_point[i][1]**2+self.leg_point[i][2]**2)
        for i in range(6):
          if leg_lenght[i] > 248 or leg_lenght[i] < 90:
            flag=False
        return flag
    def condition(self):
        while True:
            if (time.time()-self.timeout)>10 and  self.timeout!=0 and self.order[0]=='':
                self.timeout=time.time()
                self.relax(True)
                self.flag=0x00
            if cmd.CMD_POSITION in self.order and len(self.order)==4:
                if self.flag!=0x01:
                    self.relax(False)
                x=self.restriction(int(self.order[1]),-40,40)
                y=self.restriction(int(self.order[2]),-40,40)
                z=self.restriction(int(self.order[3]),-20,20)
                self.posittion(x,y,z)
                self.flag=0x01
                self.order=['','','','','',''] 
            elif cmd.CMD_ATTITUDE in self.order and len(self.order)==4:
                if self.flag!=0x02:
                    self.relax(False)
                r=self.restriction(int(self.order[1]),-15,15)
                p=self.restriction(int(self.order[2]),-15,15)
                y=self.restriction(int(self.order[3]),-15,15)
                point=self.postureBalance(r,p,y)
                self.coordinateTransformation(point)
                self.setLegAngle()
                self.flag=0x02
                self.order=['','','','','',''] 
            elif cmd.CMD_MOVE in self.order and len(self.order)==6:
                if self.order[2] =="0" and self.order[3] =="0":
                    self.run(self.order)
                    self.order=['','','','','',''] 
                else:
                    if self.flag!=0x03:
                        self.relax(False)
                    self.run(self.order)
                    self.flag=0x03
            elif cmd.CMD_BALANCE in self.order and len(self.order)==2:
                if self.order[1] =="1":
                    self.order=['','','','','',''] 
                    if self.flag!=0x04:
                        self.relax(False)
                    self.flag=0x04
                    self.imu6050()
            elif cmd.CMD_CALIBRATION in self.order:
                self.timeout=0
                self.calibration()
                self.setLegAngle()
                if len(self.order) >=2:
                    if self.order[1]=="one":
                        self.calibration_leg_point[0][0]=int(self.order[2])
                        self.calibration_leg_point[0][1]=int(self.order[3])
                        self.calibration_leg_point[0][2]=int(self.order[4])
                        self.calibration()
                        self.setLegAngle()
                    elif self.order[1]=="two":
                        self.calibration_leg_point[1][0]=int(self.order[2])
                        self.calibration_leg_point[1][1]=int(self.order[3])
                        self.calibration_leg_point[1][2]=int(self.order[4])
                        self.calibration()
                        self.setLegAngle()
                    elif self.order[1]=="three":
                        self.calibration_leg_point[2][0]=int(self.order[2])
                        self.calibration_leg_point[2][1]=int(self.order[3])
                        self.calibration_leg_point[2][2]=int(self.order[4])
                        self.calibration()
                        self.setLegAngle()
                    elif self.order[1]=="four":
                        self.calibration_leg_point[3][0]=int(self.order[2])
                        self.calibration_leg_point[3][1]=int(self.order[3])
                        self.calibration_leg_point[3][2]=int(self.order[4])
                        self.calibration()
                        self.setLegAngle()
                    elif self.order[1]=="five":
                        self.calibration_leg_point[4][0]=int(self.order[2])
                        self.calibration_leg_point[4][1]=int(self.order[3])
                        self.calibration_leg_point[4][2]=int(self.order[4])
                        self.calibration()
                        self.setLegAngle()
                    elif self.order[1]=="six":
                        self.calibration_leg_point[5][0]=int(self.order[2])
                        self.calibration_leg_point[5][1]=int(self.order[3])
                        self.calibration_leg_point[5][2]=int(self.order[4])
                        self.calibration()
                        self.setLegAngle()
                    elif self.order[1]=="save":
                        self.saveToTxt(self.calibration_leg_point,'point')
                self.order=['','','','','',''] 
    def relax(self,flag):
        if flag:
            self.servo.relax()
        else:
            self.setLegAngle()
        
    def coordinateTransformation(self,point):
        for i in range(6):
            c = self._leg_cos[i]
            s = self._leg_sin[i]
            self.leg_point[i][0] =  point[i][0]*c + point[i][1]*s + self._leg_offset_x[i]
            self.leg_point[i][1] = -point[i][0]*s + point[i][1]*c
            self.leg_point[i][2] =  point[i][2] - 14
    
    def restriction(self,var,v_min,v_max):
        if var < v_min:
            return v_min
        elif var > v_max:
            return v_max
        else:
            return var

    def map(self,value,fromLow,fromHigh,toLow,toHigh):
        return (toHigh-toLow)*(value-fromLow) / (fromHigh-fromLow) + toLow
    
    def posittion(self,x,y,z):
        point=[row[:] for row in self.body_point]
        for i in range(6):
            point[i][0]=self.body_point[i][0]-x
            point[i][1]=self.body_point[i][1]-y
            point[i][2]=-30-z
            self.height=point[i][2]
            self.body_point[i][2]=point[i][2]
        self.coordinateTransformation(point)
        self.setLegAngle()
            
    def postureBalance(self,r, p, y):
        pos = np.mat([0.0, 0.0, self.height]).T
        R, P, Y = r * math.pi / 180, p * math.pi / 180, y * math.pi / 180
        rotx = np.mat([[1, 0, 0],
                       [0, math.cos(P), -math.sin(P)],
                       [0, math.sin(P), math.cos(P)]])
        roty = np.asmatrix([[math.cos(R), 0, -math.sin(R)],
                       [0, 1, 0],
                       [math.sin(R), 0, math.cos(R)]])
        rotz = np.asmatrix([[math.cos(Y), -math.sin(Y), 0],
                       [math.sin(Y), math.cos(Y), 0],
                       [0, 0, 1]])
        rot_mat = rotx * roty * rotz
        # Apply rotation to all 6 foot positions at once (3×6 matrix op)
        AB = pos + rot_mat * self._footpoint_struc
        return [[AB[0,i], AB[1,i], AB[2,i]] for i in range(6)]
         
    def imu6050(self):
        old_r=0
        old_p=0
        i=0
        point=self.postureBalance(0,0,0)
        self.coordinateTransformation(point)
        self.setLegAngle()
        time.sleep(2)
        self.imu.Error_value_accel_data,self.imu.Error_value_gyro_data=self.imu.average_filter()
        time.sleep(1)
        while True:
            if self.order[0]!="":
                break
            _t = time.time()
            r,p,y=self.imu.imuUpdate()
            #r=self.restriction(self.pid.PID_compute(r),-15,15)
            #p=self.restriction(self.pid.PID_compute(p),-15,15)
            r=self.pid.PID_compute(r)
            p=self.pid.PID_compute(p)
            point=self.postureBalance(r,p,0)
            self.coordinateTransformation(point)
            self.setLegAngle()
            # Sleep only the remaining time to maintain ~50 Hz update rate
            time.sleep(max(0.0, 0.02 - (time.time() - _t)))
 
    def run(self,data,Z=40,F=64):#example : data=['CMD_MOVE', '1', '0', '25', '10', '0']
        gait=data[1]
        x=self.restriction(int(data[2]),-35,35)
        y=self.restriction(int(data[3]),-35,35)
        if gait=="1" :
            F=round(self.map(int(data[4]),2,10,126,22))
        else:
            F=round(self.map(int(data[4]),2,10,171,45))
        angle=int(data[5])
        z=Z/F
        delay=0.008  # 8 ms — keeps ~2 updates per servo PWM cycle (50 Hz = 20 ms period)
        point=[row[:] for row in self.body_point]
        #if y < 0:
        #   angle=-angle
        if angle!=0:
            x=0
        xy=[[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]
        for i in range(6):
            xy[i][0]=((point[i][0]*math.cos(angle/180*math.pi)+point[i][1]*math.sin(angle/180*math.pi)-point[i][0])+x)/F
            xy[i][1]=((-point[i][0]*math.sin(angle/180*math.pi)+point[i][1]*math.cos(angle/180*math.pi)-point[i][1])+y)/F
        if x == 0 and y == 0 and angle==0:
            self.coordinateTransformation(point)
            self.setLegAngle()
        elif gait=="1" :
            # Pre-compute phase boundaries once instead of re-dividing every frame
            F_8  = F / 8
            F_4  = F / 4
            F3_8 = 3 * F / 8
            F5_8 = 5 * F / 8
            F3_4 = 3 * F / 4
            F7_8 = 7 * F / 8
            for j in range (F):
                for i in range(3):
                    if j< F_8:
                        point[2*i][0]=point[2*i][0]-4*xy[2*i][0]
                        point[2*i][1]=point[2*i][1]-4*xy[2*i][1]
                        point[2*i+1][0]=point[2*i+1][0]+8*xy[2*i+1][0]
                        point[2*i+1][1]=point[2*i+1][1]+8*xy[2*i+1][1]
                        point[2*i+1][2]=Z+self.height
                    elif j< F_4:
                        point[2*i][0]=point[2*i][0]-4*xy[2*i][0]
                        point[2*i][1]=point[2*i][1]-4*xy[2*i][1]
                        point[2*i+1][2]=point[2*i+1][2]-z*8
                    elif j< F3_8:
                        point[2*i][2]=point[2*i][2]+z*8
                        point[2*i+1][0]=point[2*i+1][0]-4*xy[2*i+1][0]
                        point[2*i+1][1]=point[2*i+1][1]-4*xy[2*i+1][1]
                    elif j< F5_8:
                        point[2*i][0]=point[2*i][0]+8*xy[2*i][0]
                        point[2*i][1]=point[2*i][1]+8*xy[2*i][1]

                        point[2*i+1][0]=point[2*i+1][0]-4*xy[2*i+1][0]
                        point[2*i+1][1]=point[2*i+1][1]-4*xy[2*i+1][1]
                    elif j< F3_4:
                        point[2*i][2]=point[2*i][2]-z*8
                        point[2*i+1][0]=point[2*i+1][0]-4*xy[2*i+1][0]
                        point[2*i+1][1]=point[2*i+1][1]-4*xy[2*i+1][1]
                    elif j< F7_8:
                        point[2*i][0]=point[2*i][0]-4*xy[2*i][0]
                        point[2*i][1]=point[2*i][1]-4*xy[2*i][1]
                        point[2*i+1][2]=point[2*i+1][2]+z*8
                    else:
                        point[2*i][0]=point[2*i][0]-4*xy[2*i][0]
                        point[2*i][1]=point[2*i][1]-4*xy[2*i][1]
                        point[2*i+1][0]=point[2*i+1][0]+8*xy[2*i+1][0]
                        point[2*i+1][1]=point[2*i+1][1]+8*xy[2*i+1][1]
                self.coordinateTransformation(point)
                self.setLegAngle()
                time.sleep(delay)
                
        elif gait=="2":
            aa=0
            number=[5,2,1,0,3,4]
            for i in range(6):
                for j in range(int(F/6)):
                    for k in range(6):
                        if number[i] == k:
                            if j <int(F/18):
                                point[k][2]+=18*z
                            elif j <int(F/9):
                                point[k][0]+=30*xy[k][0]
                                point[k][1]+=30*xy[k][1]
                            elif j <int(F/6):
                                point[k][2]-=18*z
                        else:
                            point[k][0]-=2*xy[k][0]
                            point[k][1]-=2*xy[k][1]
                    self.coordinateTransformation(point)
                    self.setLegAngle()
                    time.sleep(delay) 
                    aa+=1
                  
                             
if __name__=='__main__':
    pass
    




   
   

            
        
        
        
            
        
            

  
