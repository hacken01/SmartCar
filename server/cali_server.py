#!/usr/bin/env python3
import RPi.GPIO as GPIO
import video_dir
import car_dir
import motor
from socket import *
from time import ctime          # Import necessary modules   

HOST = ''           # The variable of HOST is null, so the function bind( ) can be bound to all valid addresses.
PORT = 21567
BUFSIZ = 1024       # Size of the buffer
ADDR = (HOST, PORT)

tcpSerSock = socket(AF_INET, SOCK_STREAM)    # Create a socket.
tcpSerSock.bind(ADDR)    # Bind the IP address and port number of the server. 
tcpSerSock.listen(5)     # The parameter of listen() defines the number of connections permitted at one time. Once the 
                         # connections are full, others will be rejected. 

busnum = 1          # Edit busnum to 0, if you uses Raspberry Pi 1 or 0

def setup():
    global offset_x,  offset_y, offset, forward0, forward1
    offset_x = 0
    offset_y = 0
    offset = 0
    forward0 = 'True'
    forward1 = 'False'
    try:
        with open('config') as f:
            for line in f:
                if line[0:8] == 'offset_x':
                    offset_x = int(line[11:-1])
                    print('offset_x =', offset_x)
                if line[0:8] == 'offset_y':
                    offset_y = int(line[11:-1])
                    print('offset_y =', offset_y)
                if line[0:8] == 'offset =':
                    offset = int(line[9:-1])
                    print('offset =', offset)
                if line[0:8] == "forward0":
                    forward0 = line[11:-1]
                    print('turning0 =', forward0)
                if line[0:8] == "forward1":
                    forward1 = line[11:-1]
                    print('turning1 =', forward1)
    except:
        print('no config file, set config to original')
    video_dir.setup(busnum=busnum)
    car_dir.setup(busnum=busnum)
    motor.setup(busnum=busnum) 
    video_dir.calibrate(offset_x, offset_y)
    car_dir.calibrate(offset)

def REVERSE(x):
    return 'False' if x == 'True' else 'True'

def loop():
    global offset_x, offset_y, offset, forward0, forward1
    while True:
        print('Waiting for connection...')
        tcpCliSock, addr = tcpSerSock.accept() 
        print('...connected from :', addr)

        while True:
            data = tcpCliSock.recv(BUFSIZ).decode()    # Receive data sent from the client. 
            if not data:
                break
            if data == 'motor_run':
                print('motor moving forward')
                motor.setSpeed(50)
                motor.motor0(forward0)
                motor.motor1(forward1)
            elif data[0:9] == 'leftmotor':
                forward0 = data[9:]
                motor.motor0(forward0)
            elif data[0:10] == 'rightmotor':
                forward1 = data[10:]
                motor.motor1(forward1)
            elif data == 'leftreverse':
                forward0 = REVERSE(forward0)
                print("left motor reversed to", forward0)
                motor.motor0(forward0)
            elif data == 'rightreverse':
                forward1 = REVERSE(forward1)
                print("right motor reversed to", forward1)
                motor.motor1(forward1)
            elif data == 'motor_stop':
                print('motor stop')
                motor.stop()
            elif data[0:7] == 'offset=':
                offset = int(data[7:])
                car_dir.calibrate(offset)
            elif data[0:8] == 'offsetx=':
                offset_x = int(data[8:])
                print('Mount offset x', offset_x)
                video_dir.calibrate(offset_x, offset_y)
            elif data[0:8] == 'offsety=':
                offset_y = int(data[8:])
                print('Mount offset y', offset_y)
                video_dir.calibrate(offset_x, offset_y)
            elif data[0:7] == 'offset+':
                offset += int(data[7:])
                print('Turning offset', offset)
                car_dir.calibrate(offset)
            elif data[0:7] == 'offset-':
                offset -= int(data[7:])
                print('Turning offset', offset)
                car_dir.calibrate(offset)
            elif data[0:8] == 'offsetx+':
                offset_x += int(data[8:])
                print('Mount offset x', offset_x)
                video_dir.calibrate(offset_x, offset_y)
            elif data[0:8] == 'offsetx-':
                offset_x -= int(data[8:])
                print('Mount offset x', offset_x)
                video_dir.calibrate(offset_x, offset_y)
            elif data[0:8] == 'offsety+':
                offset_y += int(data[8:])
                print('Mount offset y', offset_y)
                video_dir.calibrate(offset_x, offset_y)
            elif data[0:8] == 'offsety-':
                offset_y -= int(data[8:])
                print('Mount offset y', offset_y)
                video_dir.calibrate(offset_x, offset_y)
            elif data == 'confirm':
                config = f'offset_x = {offset_x}\noffset_y = {offset_y}\noffset = {offset}\nforward0 = {forward0}\nforward1 = {forward1}\n'
                print('\n*********************************')
                print(' You are setting config file to:')
                print('*********************************')
                print(config)
                print('*********************************\n')
                with open('config', 'w') as fd:
                    fd.write(config)
                motor.stop()
                tcpCliSock.close()
                return
            else:
                print('Command Error! Cannot recognize command:', data)

if __name__ == "__main__":
    try:
        setup()
        loop()
    except KeyboardInterrupt:
        tcpSerSock.close()