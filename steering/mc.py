# motor controller -- send serial steering commands to Arduino
# By Neil Nie & Michael Meng
# Jan, 2018
# Copyright (c), All rights reserved

import serial


class MC:

    def __init__(self, device_id=0):

        self.ser = serial.Serial('/dev/ttyUSB%d' % device_id, 115200)


    def turn(self, angle, precision=3):

        ret =  self.ser.write(('b'+str(round(angle,precision)).zfill(5)+'e').encode())

        if (ret == precision+4):
            pass
        else:
            print('Failed to send turning angle %f' % angle)
        return ret

