#coding:utf-8
from PCA9685 import PCA9685
import time 
import math
import smbus
def mapNum(value,fromLow,fromHigh,toLow,toHigh):
    return (toHigh-toLow)*(value-fromLow) / (fromHigh-fromLow) + toLow

# Pre-computed constants: angle(0–180) → pulse(500–2500 µs) → duty(0–4095)
# duty = angle * (4095*2000)/(20000*180) + (4095*500)/20000
_SERVO_SCALE  = 4095.0 * 2000.0 / (20000.0 * 180.0)  # ≈ 2.275 counts/degree
_SERVO_OFFSET = 4095.0 * 500.0  / 20000.0             # ≈ 102.375 counts

class Servo:
    def __init__(self):
        self.pwm_40 = PCA9685(0x40, debug=True)
        self.pwm_41 = PCA9685(0x41, debug=True)
        # Set the cycle frequency of PWM  
        self.pwm_40.setPWMFreq(50) 
        time.sleep(0.01) 
        self.pwm_41.setPWMFreq(50) 
        time.sleep(0.01)             

    #Convert the input angle to the value of pca9685
    def setServoAngle(self,channel, angle):
        date = int(_SERVO_SCALE * angle + _SERVO_OFFSET)  # angle→duty in one step
        if channel < 16:
            self.pwm_41.setPWM(channel, 0, date)
        elif channel >= 16 and channel < 32:
            self.pwm_40.setPWM(channel - 16, 0, date)
        #time.sleep(0.0001)
    def relax(self):
        for i in range(8):
            self.pwm_41.setPWM(i+8, 4096, 4096)
            self.pwm_40.setPWM(i, 4096, 4096)
            self.pwm_40.setPWM(i+8, 4096, 4096)
            
def servo_installation_position():
    S=Servo()     
    for i in range(32):
        if (i == 10 or i == 13 or i == 31):
            S.setServoAngle(i,0)
        elif (i == 18 or i == 21 or i == 27):
            S.setServoAngle(i,180)
        else:
            S.setServoAngle(i,90)
    time.sleep(3)
# Main program logic follows:
if __name__ == '__main__':
    print("Now servos will rotate to certain angles.") 
    print("Please keep the program running when installing the servos.")
    print("After that, you can press ctrl-C to end the program.")
    while True:
        try:        
            servo_installation_position()
        except KeyboardInterrupt:
            print ("\nEnd of program")
            break


