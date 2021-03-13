'''
Manage the magnetometer
'''

import os
from collections import namedtuple, deque
import json
import math
import adafruit_mlx90393
import qwiic_adxl313

COMPASS_SMOOTHING_DEQUE_LEN = 2

RADIAN_TO_DEGREE = 180 / math.pi

_COMPASS_FILE = '/var/wordclock/compass.json'

_KEY_X = 'x'
_KEY_Y = 'y'
_KEY_Z = 'z'

_XYZ = [_KEY_X, _KEY_Y, _KEY_Z]

_COMPASS_VALUE_MIN = 'min'
_COMPASS_VALUE_MAX = 'max'

_COMPASS_DEFAULTS = {
    _KEY_X: {_COMPASS_VALUE_MIN: 100000, _COMPASS_VALUE_MAX: -100000},
    _KEY_Y: {_COMPASS_VALUE_MIN: 100000, _COMPASS_VALUE_MAX: -100000},
    _KEY_Z: {_COMPASS_VALUE_MIN: 100000, _COMPASS_VALUE_MAX: -100000},
    }

AccelCoord = namedtuple('AccelCoord', 'key positive')
CompassAngle = namedtuple('CompassAngle', 'orientation opposite near offset')
Orientation = namedtuple('Orientation', 'angle orientation')

FACE_UP = 'face-up'
BACK_UP = 'back-up'
TOP_UP = 'top-op'
RIGHT_UP = 'right-up'
BOTTOM_UP = 'bottom-up'
LEFT_UP = 'left-up'

_ACCEL_COORD_TOP_UP = AccelCoord(_KEY_Y, False)

_ORIENTATIONS = {
    AccelCoord(_KEY_X, True): CompassAngle(RIGHT_UP, _KEY_Y, _KEY_Z, -180), #
    AccelCoord(_KEY_X, False): CompassAngle(LEFT_UP, _KEY_Z, _KEY_Y, 90), #
    AccelCoord(_KEY_Y, True): CompassAngle(BOTTOM_UP, _KEY_Z, _KEY_X, 90), #
    _ACCEL_COORD_TOP_UP: CompassAngle(TOP_UP, _KEY_X, _KEY_Z, -180), #
    AccelCoord(_KEY_Z, True): CompassAngle(BACK_UP, _KEY_Y, _KEY_X, -90), # from top
    AccelCoord(_KEY_Z, False): CompassAngle(FACE_UP, _KEY_X, _KEY_Y, 0), # from top
    }

XYZ = namedtuple('XYZ', 'x y z')

class Magnetometer():
    ''' Manage the magnetometer
    '''
    #pylint: disable=too-few-public-methods

    def __init__(self, i2c, verbose):
        self._i2c = i2c
        self.verbose = verbose
        self._magnetometer = None
        self._accelerometer = None
        self._orientation = _ORIENTATIONS[_ACCEL_COORD_TOP_UP]
        self._angle_history = deque()

        self._settings = _COMPASS_DEFAULTS

        if os.path.isfile(_COMPASS_FILE):
            with open(_COMPASS_FILE, 'r') as fil:
                try:
                    self._settings.update(json.loads(fil.read()))
                except: #pylint: disable=bare-except
                    pass

        self._init_devices()

    def _init_devices(self):
        ''' Lazy-init the magnetometer and accelerometer
        '''
        if self._magnetometer is None:
            try:
                self._magnetometer = adafruit_mlx90393.MLX90393(
                    self._i2c, gain=adafruit_mlx90393.GAIN_5X)
                if self.verbose:
                    print('Initialized magnetometer', flush=True)
            except Exception as err: #pylint: disable=broad-except
                print('Failed to init the magnetometer:', str(err), flush=True)

        if self._accelerometer is None:
            try:
                self._accelerometer = qwiic_adxl313.QwiicAdxl313()
                self._accelerometer.measureModeOn()
                if self.verbose:
                    print('Initialized accelerometer', flush=True)
            except Exception as err: #pylint: disable=broad-except
                print('Failed to init the accelerometer:', str(err), flush=True)

    def update(self, do_calibration=False, verbose=False):
        ''' Update the compass position
        '''
        angle = None
        self._init_devices()

        if self._accelerometer is not None:
            try:
                if self._accelerometer.dataReady():
                    self._accelerometer.readAccel()

                    values = {
                        abs(self._accelerometer.x): AccelCoord(_KEY_X, self._accelerometer.x >= 0),
                        abs(self._accelerometer.y): AccelCoord(_KEY_Y, self._accelerometer.y >= 0),
                        abs(self._accelerometer.z): AccelCoord(_KEY_Z, self._accelerometer.z >= 0),
                        }

                    max_abs = max(values.keys())
                    self._orientation = _ORIENTATIONS[values[max_abs]]

                    if verbose:
                        print(
                            '{:06d}'.format(self._accelerometer.x),
                            ' {: 06d}'.format(self._accelerometer.y),
                            ' {: 06d}'.format(self._accelerometer.z),
                            flush=True)

                        print(self._orientation, max_abs)

            except Exception as err: #pylint: disable=broad-except
                self._accelerometer = None
                print('Failed to read the accelerometer:', str(err), flush=True)

        if self._magnetometer is not None:
            try:
                mag_coords = self._magnetometer.magnetic

                if do_calibration:
                    self._calibrate(mag_coords, verbose)

                adjusted = {
                    key: self._adjust(key, mag_coords[i])
                    for i, key in enumerate(_XYZ)
                    }

                new_angle = math.atan2(
                    adjusted[self._orientation.opposite],
                    adjusted[self._orientation.near]) * RADIAN_TO_DEGREE

                if new_angle < 0:
                    new_angle += 360

                new_angle = (new_angle + self._orientation.offset) % 360

                if verbose:
                    print(int(new_angle), adjusted, mag_coords, flush=True)

                self._angle_history.append(new_angle)

                if len(self._angle_history) > COMPASS_SMOOTHING_DEQUE_LEN:
                    self._angle_history.popleft()

                angle = round(sum(self._angle_history) / len(self._angle_history))

            except Exception as err: #pylint: disable=broad-except
                self._magnetometer = None
                print('Failed to read the magnetometer:', str(err), flush=True)

        return Orientation(angle, self._orientation.orientation)

    def _calibrate(self, mag_coords, verbose):
        ''' Update calibration
        '''
        changed = [self._calibrate_coord(key, mag_coords[i]) for i, key in enumerate(_XYZ)]

        if any(changed):
            with open(_COMPASS_FILE, 'w') as fil:
                fil.write(json.dumps(self._settings))

            if verbose:
                print('updated calibration', flush=True)

    def _calibrate_coord(self, key, value):
        ''' Calibrate one coordinate
        '''
        changed = False
        coord_setting = self._settings[key]

        if value < coord_setting[_COMPASS_VALUE_MIN]:
            coord_setting[_COMPASS_VALUE_MIN] = value
            changed = True

        if value > coord_setting[_COMPASS_VALUE_MAX]:
            coord_setting[_COMPASS_VALUE_MAX] = value
            changed = True

        return changed

    def _adjust(self, key, value):
        ''' Adjust a compass coordinate value
        '''
        coord_setting = self._settings[key]

        return (
            value -
            (coord_setting[_COMPASS_VALUE_MAX] + coord_setting[_COMPASS_VALUE_MIN]) / 2)
