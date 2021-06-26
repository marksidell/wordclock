'''
Calibrate the compass
'''

import time
import board
import busio
from wordclock import magnetometer


def main():
    ''' do it
    '''
    i2c = busio.I2C(board.SCL, board.SDA)
    compass = magnetometer.Magnetometer(i2c, verbose=True)

    try:
        while True:
            result = compass.update(do_calibration=True, verbose=True)
            print(result.orientation, int(result.angle))
            time.sleep(1)

    except KeyboardInterrupt:
        print('Done!')
