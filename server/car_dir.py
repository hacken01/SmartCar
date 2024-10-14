#!/usr/bin/env python3
import Sunfounder_PWM_Servo_Driver.Servo_init as servo
import time                # Import necessary modules

FILE_CONFIG = "/home/pi/Sunfounder_Smart_Video_Car_Kit_for_RaspberryPi/server/config"

def Map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def setup():
    global leftPWM, rightPWM, homePWM, pwm
    leftPWM = 400
    homePWM = 450
    rightPWM = 500
    offset = 0
    try:
        with open(FILE_CONFIG) as f:
            for line in f:
                if line[0:8] == 'offset =':
                    offset = int(line[9:-1])
    except:
        print('config error')
    leftPWM += offset
    homePWM += offset
    rightPWM += offset
    pwm = servo.init()         # Initialize the servo controller.

def turn_left():
    global leftPWM
    pwm.setPWM(0, 0, leftPWM)  # CH0

def turn_right():
    global rightPWM
    pwm.setPWM(0, 0, rightPWM)

def turn(angle):
    angle = Map(angle, 0, 255, leftPWM, rightPWM)
    pwm.setPWM(0, 0, angle)

def home():
    global homePWM
    pwm.setPWM(0, 0, homePWM)

def calibrate(x):
    pwm.setPWM(0, 0, 450+x)

def test():
    while True:
        turn_left()
        time.sleep(1)
        home()
        time.sleep(1)
        turn_right()
        time.sleep(1)
        home()

if __name__ == '__main__':
    setup()
    home()
