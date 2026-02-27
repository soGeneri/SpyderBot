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
    def setLegServoBatch(self, angle):
        """Write all 18 leg servo angles in 4 I2C block writes instead of 72 individual writes.
        angle: 6×3 list indexed [leg][joint] — same layout as Control.angle.
        Channel mapping mirrors the setLegAngle() servo calls exactly."""
        def d(a):
            return int(_SERVO_SCALE * a + _SERVO_OFFSET)

        # PCA9685 @ 0x41 — channels 8-15 (all 8 leg servos on this chip, contiguous)
        # ch8=leg3 femur, ch9=leg3 coxa, ch10=leg2 tibia, ch11=leg2 femur,
        # ch12=leg2 coxa, ch13=leg1 tibia, ch14=leg1 femur, ch15=leg1 coxa
        self.pwm_41.setChannelsPWM(8, [
            d(angle[2][1]),  # ch8:  leg3 femur
            d(angle[2][0]),  # ch9:  leg3 coxa
            d(angle[1][2]),  # ch10: leg2 tibia
            d(angle[1][1]),  # ch11: leg2 femur
            d(angle[1][0]),  # ch12: leg2 coxa
            d(angle[0][2]),  # ch13: leg1 tibia
            d(angle[0][1]),  # ch14: leg1 femur
            d(angle[0][0]),  # ch15: leg1 coxa
        ])

        # PCA9685 @ 0x40 — channels 0-7 (legs 6, 5, 4 coxa+femur, contiguous)
        # ch0=leg6 coxa, ch1=leg6 femur, ch2=leg6 tibia,
        # ch3=leg5 coxa, ch4=leg5 femur, ch5=leg5 tibia,
        # ch6=leg4 coxa, ch7=leg4 femur
        self.pwm_40.setChannelsPWM(0, [
            d(angle[5][0]),  # ch0: leg6 coxa
            d(angle[5][1]),  # ch1: leg6 femur
            d(angle[5][2]),  # ch2: leg6 tibia
            d(angle[4][0]),  # ch3: leg5 coxa
            d(angle[4][1]),  # ch4: leg5 femur
            d(angle[4][2]),  # ch5: leg5 tibia
            d(angle[3][0]),  # ch6: leg4 coxa
            d(angle[3][1]),  # ch7: leg4 femur
        ])

        # PCA9685 @ 0x40 — non-contiguous channels (individual 4-byte block writes)
        self.pwm_40.setChannelsPWM(11, [d(angle[3][2])])  # ch11: leg4 tibia  (servo 27)
        self.pwm_40.setChannelsPWM(15, [d(angle[2][2])])  # ch15: leg3 tibia  (servo 31)

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


