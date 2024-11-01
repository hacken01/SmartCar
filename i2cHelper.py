#!/usr/bin/env python3

import smbus
import time
import os

RPI_REVISION_0 = ["900092"]
RPI_REVISION_1 = ["0002", "0003", "0004", "0005", "0006", "0007", "0008", "0009", "000d", "000e", "000f", "0010", "0011", "0012", "0013"]
RPI_REVISION_2 = ["a01041", "a21041"]
RPI_REVISION_3 = ["a02082", "a22082"]

CPU_Number = ''

def getPiRevision():
    global CPU_Number
    try:
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line.startswith('Revision'):
                    CPU_Number = line[11:-1]
                    if CPU_Number in RPI_REVISION_0:
                        return 0
                    elif CPU_Number in RPI_REVISION_1:
                        return 1
                    elif CPU_Number in RPI_REVISION_2:
                        return 2
                    elif CPU_Number in RPI_REVISION_3:
                        return 3
                    else:
                        return CPU_Number
    except Exception as e:
        print(f"Error: {e}")
        return 'open file error'

def getPiI2CBusNumber():
    # get I2C bus number from /proc/cpuinfo
    revision = getPiRevision()
    if revision in [2, 3]:
        return 1 
    elif revision in [0, 1]:
        return 0
    else:
        raise ValueError(f"Error occur while getting Pi Revision. Revision: {revision}")

def remove_line(tfile, sstr):
    try:
        with open(tfile, 'r') as file:
            lines = file.readlines()
        
        with open(tfile, 'w') as file:
            for line in lines:
                if sstr not in line:
                    file.write(line)
    except Exception as e:
        print('remove_line:', e)

def add_line(tfile, sstr):
    try:
        with open(tfile, 'a') as file:
            file.write(sstr)
    except Exception as e:
        print('add line:', e)

def setting_i2c():
    remove_line('/boot/config.txt', 'dtparam=i2c_arm=')
    add_line('/boot/config.txt', '\ndtparam=i2c_arm=on\n')

def main():
    global CPU_Number
    print('')
    print('   ====================================')
    print('   ||                                ||')
    print('   ||     Raspberry Pi I2C check     ||')
    print('   ||        and setup tools         ||')
    print('   ||                                ||')
    print('   ||                     SunFounder ||')
    print('   ====================================')
    print('')
    time.sleep(2)
    print("   Checking your Pi's information.")
    your_pi_revision = getPiRevision()
    you_i2c_bus_number = getPiI2CBusNumber()
    time.sleep(1)
    print('   Your cpu revision:', CPU_Number)
    time.sleep(1)
    print('   Your Raspberry Pi is Revision', your_pi_revision)
    time.sleep(1)
    print('   Your I2C bus number is:', you_i2c_bus_number)
    time.sleep(1)
    print('')
    time.sleep(1)
    print('   Checking your device...')
    
    device = f'i2c-{you_i2c_bus_number}'
    flag = device in os.listdir('/dev/')

    time.sleep(1)
    if flag:
        print('   I2C setting is fine.')
        time.sleep(1)
        print('   Running i2cdetect..')
        time.sleep(1)
        print('')
        command = f'i2cdetect -y {you_i2c_bus_number}'
        os.system(command)
    else:
        print('   I2C has not been set up.')
        time.sleep(1)
        print('')
        time.sleep(1)
        print('   Backup...', end=' ')
        os.system('cp /boot/config.txt /boot/config.bak')
        print('done')
        time.sleep(1)
        print('   Setting i2c...', end=' ')
        setting_i2c()
        print('done')
        time.sleep(1)
        print('   I2C has been set. It will change after reboot.')
        time.sleep(1)
        check = input('   Do you want to reboot now?(y/n) ')
        flag = True
        while flag:
            if check in ['y', 'Y']:
                print(' Your Raspberry Pi will be reboot in 5 seconds.')
                for i in range(6):
                    time.sleep(1)
                    print(' ', 5-i)
                print(' Rebooting...')
                flag = False
                os.system('reboot')
            elif check in ['n', 'N']:
                time.sleep(1)
                print(' Done.')
                flag = False
            else:
                print(' It should be "Y" or "N", in capital or not. Try again.')

if __name__ == '__main__':
    main()

