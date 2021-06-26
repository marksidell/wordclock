'''
Test sensors
'''

import time
import board
import busio
import adafruit_mlx90393
import qwiic_adxl313
import adafruit_veml7700


def main():
    ''' do it
    '''
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        magnetometer = None
        accelerometer = None
        light_sensor = None

        while True:
            if magnetometer is None:
                try:
                    magnetometer = adafruit_mlx90393.MLX90393(
                        i2c, gain=adafruit_mlx90393.GAIN_5X)
                    print('Initialized magnetometer')
                except Exception as err: #pylint: disable=broad-except
                    print('Failed to init the magnetometer:', str(err))

            if accelerometer is None:
                try:
                    accelerometer = qwiic_adxl313.QwiicAdxl313()
                    accelerometer.measureModeOn()
                    print('Initialized accelerometer')
                except Exception as err: #pylint: disable=broad-except
                    print('Failed to init the accelerometer:', str(err))
                time.sleep(1)

            if light_sensor is None:
                try:
                    light_sensor = adafruit_veml7700.VEML7700(i2c)
                    print('Initialized light sensor')

                except Exception as err: #pylint: disable=broad-except
                    print('Failed to init light sensor:', str(err))

            if magnetometer is not None:
                print('compass;', magnetometer.magnetic)

            if accelerometer is not None:
                if accelerometer.dataReady():
                    accelerometer.readAccel()

                print('accel:  ', accelerometer.x, accelerometer.y, accelerometer.z)

            if light_sensor is not None:
                print('light:  ', light_sensor.light)

            time.sleep(1)

    except KeyboardInterrupt: #pylint: disable=bare-except
        pass
