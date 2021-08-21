'''
Word Clock

CSS source:
https://www.w3schools.com/w3css/4/w3.css

jquery source:
https://ajax.googleapis.com/ajax/libs/jquery/1.10.1/jquery.min.js
'''
#pylint: disable=too-many-lines

import os
from enum import Enum
from collections import namedtuple, deque
import subprocess
import re
import datetime
import time
from argparse import ArgumentParser
import random
import math
from bisect import bisect_left
import json
import traceback
import asyncio
import pytz
import astral
from astral import sun
from aiohttp import web
from timezonefinder import TimezoneFinder
import neopixel
import RPi.GPIO as GPIO
import board
import busio
import adafruit_veml7700

from wordclock import __version__, config, magnetometer

DO_CALIBRATION = False

HOTSPOT_IP = '10.0.0.1'

COMPASS_JITTER_THRESHOLD = 10
AMBIENT_SMOOTHING_DEQUE_LEN = 5

LONG_PRESS_DURATION = 3

SETTINGS_TITLE = '{} Clock'.format(config.CLOCK_NAME)

def scale_color(color, factor):
    ''' Return a color tuple scaled by a factor
    '''
    return tuple(int(x * factor) for x in color)


COLOR_LIGHTSKY = scale_color((135, 206, 250), 0.20)
#COLOR_NIGHTSKY = (43//8, 47//8, 119//8)
COLOR_NIGHTSKY = scale_color((25, 25, 112), 0.4)
COLOR_GROUND = scale_color((46, 139, 87), 0.7)
COLOR_MINUTE = scale_color((180, 0, 128), 0.4)
COLOR_DAY = scale_color((22, 0, 255), 1.00)
COLOR_DAY_OFF = scale_color((255, 255, 255), 0.10)
COLOR_WORD = (255, 255, 255)
COLOR_OFF = (0, 0, 0)
COLOR_BORDER_LIGHT1 = (128, 0, 255)
COLOR_BORDER_LIGHT2 = (255, 0, 128)
COLOR_SUN = (255, 255, 0)
COLOR_GOLDEN_HOUR_START = (255, 90, 34) # from IMG_3850.JPG sunrise
COLOR_RANDOM_BORDER = scale_color((180, 0, 128), 0.125)
COLOR_BUTTON_PRESS = (0, 0, 255)
COLOR_HOTSPOT_MODE = (255, 0, 64)
COLOR_LONG_BUTTON_PRESS = COLOR_HOTSPOT_MODE

DELTAS = [
    None, config.T_FIVE, config.T_TEN,
    config.T_QUARTER, config.T_TWENTY, config.T_TWENTYFIVE,
    config.T_HALF, config.T_TWENTYFIVE, config.T_TWENTY,
    config.T_QUARTER, config.T_TEN, config.T_FIVE]

HOURS = [
    config.H_TWELVE, config.H_ONE, config.H_TWO, config.H_THREE, config.H_FOUR, config.H_FIVE,
    config.H_SIX, config.H_SEVEN, config.H_EIGHT, config.H_NINE, config.H_TEN, config.H_ELEVEN,
]


RANDOM_COLORS = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (0, 255, 255),
    (255, 0, 255),
    (255, 255, 255),
    ]


def is_after(word0, word1):
    ''' Is word1 after word0 on the grid?
    '''
    l_word0 = len(word0.text)

    if word0.vertical:
        word0_end = word0.y + l_word0

        return (
            word1.y >= word0.y and word1.y <= word0_end and word1.x > word0.x + 1
            or word1.y > word0_end)

    return word1.y == word0.y and word1.x > word0.x + l_word0 or word1.y > word0.y


def init_poems(all_words_in_grid_order):
    ''' Calculate poems.
        Store a list of poems that start with each word.
        Return a list of all poems.
    '''
    for word0 in all_words_in_grid_order:
        word0.after = [word1 for word1 in all_words_in_grid_order if is_after(word0, word1)]

    for word0 in all_words_in_grid_order:
        word0.poems = [
            (word0, word1, word2)
            for word1 in word0.after
            for word2 in word1.after
            if word0.after and word1.after]

    return [poem for word in all_words_in_grid_order for poem in word.poems]

# All words ordered by their position in the grid, left to right, top to bottom.
ALL_WORDS_IN_GRID_ORDER = sorted(config.ALL_WORDS, key=lambda x: (x.y, x.x))

# All four-word poems
ALL_POEMS = init_poems(ALL_WORDS_IN_GRID_ORDER)

class State(Enum):
    ''' The operational state
    '''
    STARTING = 1
    HOTSPOT = 2
    WIFI_INIT = 3
    WIFI_ACTIVE = 4
    ERROR = 5


class DisplayMode(Enum):
    ''' What we are displaying
    '''
    CLOCK = 1
    RANDOM_WORDS = 2
    DEMO = 3
    DEMO_BIRTHDAY = 4

StatePixel = namedtuple('StatePixel', 'index color')

STATE_DISPLAY = {
    State.STARTING: StatePixel(0, (0, 0, 255)),
    State.HOTSPOT: StatePixel(1, COLOR_HOTSPOT_MODE),
    State.WIFI_INIT: StatePixel(2, (64, 0, 255)),
    State.ERROR: StatePixel(3, (255, 0, 0)),
    }

PORT_HTTP = 80

FILES_DIR = '/var/wordclock'
PARAMS_FILE = os.path.join(FILES_DIR, 'params.json')
WIFI_PARAMS_FILE = os.path.join(FILES_DIR, 'wifi.json')
BODY_FILE = os.path.join(FILES_DIR, 'website', 'body.html')

# These keys must agree with the corresponding controls on the web page.
PARAM_SSID = 'ssid'
PARAM_PASSWORD = 'password'
PARAM_LAT = 'lat'
PARAM_LON = 'lon'
PARAM_MIN_LIGHT = 'min_light'
PARAM_MIN_BRIGHTNESS = 'min_brightness'
PARAM_MAX_LIGHT = 'max_light'
PARAM_MAX_BRIGHTNESS = 'max_brightness'
PARAM_SUNRISE = 'sunrise'

WIFI_PARAMS = [PARAM_SSID, PARAM_PASSWORD]

SUNRISE_LEFT = "left"
SUNRISE_RIGHT = "right"
SUNRISE_COMPASS = "compass"
DEFAULT_SUNRISE = SUNRISE_COMPASS

MAX_LAT = 90
MAX_LON = 180

LatLonConfig = namedtuple('LatLonConfig', 'name param max')

LAT_CONFIG = LatLonConfig('Latitude', PARAM_LAT, MAX_LAT)
LON_CONFIG = LatLonConfig('Longitude', PARAM_LON, MAX_LON)

FUTZ_DISPLAY_NOON = 'noon'
FUTZ_DISPLAY_MIDNIGHT = 'midnight'

ABS_MIN_LIGHT = 0
ABS_MAX_LIGHT = 30000
DEFAULT_MIN_LIGHT = 500
DEFAULT_MAX_LIGHT = 2000
DEFAULT_MIN_BRIGHTNESS = 15
DEFAULT_MAX_BRIGHTNESS = 100

DisplayConfig = namedtuple('DisplayConfig', 'name param min max')

MIN_LIGHT_CONFIG = DisplayConfig('Min Ambient Light', PARAM_MIN_LIGHT, ABS_MIN_LIGHT, ABS_MAX_LIGHT)
MAX_LIGHT_CONFIG = DisplayConfig('Max Ambient Light', PARAM_MAX_LIGHT, ABS_MIN_LIGHT, ABS_MAX_LIGHT)
MIN_BRIGHTNESS_CONFIG = DisplayConfig('Min Brightness', PARAM_MIN_BRIGHTNESS, 0, 100)
MAX_BRIGHTNESS_CONFIG = DisplayConfig('Max Brightness', PARAM_MAX_BRIGHTNESS, 0, 100)

DISPLAY_ERROR_FMT = '<li>The {param} must be between {min} and {max}</li>'

PIN_BUTTON = 23
PIN_PIXELS = board.D18

DIM = 12
BORDER_DIM = 24 if config.VERSION_2 else 12
N_PIXELS = DIM*DIM + BORDER_DIM*4

PIXEL_MAP = [
    [(DIM-1-x) * DIM + (DIM-1-y if x % 2 else y) for y in range(DIM)]
    for x in range(DIM)
    ]

MARQEE_PIXELS = (
    [PIXEL_MAP[x_i][0] for x_i in range(DIM - 1)] +
    [PIXEL_MAP[DIM-1][y_i] for y_i in range(DIM - 1)] +
    [PIXEL_MAP[x_i][DIM-1] for x_i in range(DIM - 1, 0, -1)] +
    [PIXEL_MAP[0][y_i] for y_i in range(DIM - 1, 0, -1)])


DOW_PIXELS_X = 0
DOW_PIXELS_Y = DIM - 1

NUMERIC_PIXELS_X = 7
NUMERIC_PIXELS_Y = DIM - 1

BORDER_PIXELS_BASE = DIM * DIM
BORDER_PIXELS_LEN = BORDER_DIM * 4
BORDER_PIXELS_END = BORDER_PIXELS_BASE + BORDER_PIXELS_LEN
SKY_PIXELS_LEN = BORDER_DIM * 3
ASTRAL_PIXELS_BASE = BORDER_PIXELS_BASE
ASTRAL_PIXELS_SUNSET = ASTRAL_PIXELS_BASE + SKY_PIXELS_LEN - 1
ASTRAL_PIXELS_RANGE = range(
    BORDER_PIXELS_BASE, BORDER_PIXELS_BASE + SKY_PIXELS_LEN)
GROUND_PIXELS_RANGE = range(
    BORDER_PIXELS_BASE + SKY_PIXELS_LEN, BORDER_PIXELS_BASE + BORDER_PIXELS_LEN)

MARQEE_LIGHT_DELTA = 4

SR_BEGIN = 'sr_begin'
SR_END = 'sr_end'
SS_BEGIN = 'ss_begin'
SS_END = 'ss_end'

#======================================================================
# In millimeters
MASK_WIDTH = 406.4
if config.VERSION_2:
    PIXEL_SPACING = 16.61
    PIXEL_TO_EDGE = 15
else:
    PIXEL_SPACING = 33.22
    PIXEL_TO_EDGE = 12.95 + 7.5

# Offests of pixels relative to corner of one edge
PIXEL_OFFSETS = [PIXEL_TO_EDGE + PIXEL_SPACING * i for i in range(BORDER_DIM)]

RADIAN_TO_DEGREE = 180 / math.pi

def calc_angle(opposite, adjacent):
    ''' Calculate the angle of a right triangle
    '''
    return math.atan(opposite / adjacent) * RADIAN_TO_DEGREE


# angle = arctan(opposite/adjacent)
#
HALF_ANGLES = (
    # The vertical pixels up the side.
    #   opposite is iterating up the vertical edge
    #   adjacent is half the width of the bottom edge
    #
    [calc_angle(PIXEL_OFFSETS[y_i], MASK_WIDTH / 2)
     for y_i in range(len(PIXEL_OFFSETS))] +

    # The horizontal pixels across the top
    #   oppsite is height of the side edge
    #   adjacent is iterating halfway across the top edge
    #
    [calc_angle(MASK_WIDTH, PIXEL_OFFSETS[(BORDER_DIM - 1) - x_i] - MASK_WIDTH / 2)
     for x_i in range(len(PIXEL_OFFSETS) // 2)])

ALL_ANGLES = HALF_ANGLES + [180 - HALF_ANGLES[::-1][i] for i in range(len(HALF_ANGLES))]

def angle_interpolate(index):
    ''' Return the angle at half the distance between pixel i and i+1
    '''
    angle_i = ALL_ANGLES[index]
    return angle_i + (ALL_ANGLES[index+1] - angle_i) / 2

ASTRAL_ANGLES = [angle_interpolate(i) for i in range(len(ALL_ANGLES) - 1)] + [180]


def angle_to_pixel(angle):
    ''' Return the astral pixel closest to the specified astral angle
    '''
    return bisect_left(ASTRAL_ANGLES, angle)


WPA_SUPPLICANT_CONF_FILE = '/etc/wpa_supplicant/wpa_supplicant.conf'

WPA_SUPPLICATION_CONF_FMT = '''ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US

network={{
\tssid="{ssid}"
\tpsk="{password}"
\tkey_mgmt=WPA-PSK
}}
'''

SunTimes = namedtuple('SunTimes', 'blue_start blue_end golden_start golden_end')
Sun = namedtuple('Sun', 'sun_pixel, sun_color, sky_color ground_color')

# The altitude of the sun at the end/start of golden hour
DAYLIGHT_ANGLE = 6

class AstralInfo():
    ''' Everything about the sun
    '''
    def __init__(self, lat, lon, timezone, debug):
        self.debug = debug
        self.observer = astral.LocationInfo(latitude=lat, longitude=lon).observer
        self.timezone = timezone

        self.morning_times = None
        self.evening_times = None
        self.daylight_seconds = None

        self.set_day(datetime.datetime.now(timezone).date())

    def set_day(self, today):
        ''' Set astral info for the specified day
        '''
        self.morning_times = self.get_times(today, astral.SunDirection.RISING)
        self.evening_times = self.get_times(today, astral.SunDirection.SETTING)

        self.daylight_seconds = self.evening_times.golden_start - self.morning_times.golden_end

        if self.debug:
            print('daylight seconds', self.daylight_seconds, flush=True)

    def get_sun(self, timestamp, orientation):
        ''' Given a timestamp, return the params for drawing the clock border
        '''
        if orientation == SUNRISE_LEFT:
            sunrise_pixel = ASTRAL_PIXELS_BASE
            sunset_pixel = ASTRAL_PIXELS_SUNSET
        else:
            sunrise_pixel = ASTRAL_PIXELS_SUNSET
            sunset_pixel = ASTRAL_PIXELS_BASE

        # nighttime
        if (timestamp < self.morning_times.blue_start or
                timestamp >= self.evening_times.blue_end):
            return Sun(None, None, COLOR_NIGHTSKY, COLOR_NIGHTSKY)

        # daytime
        if self.morning_times.golden_end <= timestamp < self.evening_times.golden_start:
            index = angle_to_pixel(self._sun_angle(timestamp))
            sun_pixel = (
                ASTRAL_PIXELS_BASE + index if orientation == SUNRISE_LEFT
                else ASTRAL_PIXELS_SUNSET - index)

            return Sun(
                sun_pixel,
                COLOR_SUN,
                COLOR_LIGHTSKY,
                COLOR_GROUND)

        # morning blue hour
        if self.morning_times.blue_start <= timestamp < self.morning_times.golden_start:
            return Sun(
                sunrise_pixel,
                interpolate_color(
                    COLOR_NIGHTSKY, COLOR_GOLDEN_HOUR_START,
                    self.morning_times.blue_start,
                    self.morning_times.golden_start,
                    timestamp),
                COLOR_NIGHTSKY,
                COLOR_NIGHTSKY)

        # morning golden hour
        if self.morning_times.golden_start <= timestamp < self.morning_times.golden_end:
            return Sun(
                sunrise_pixel,
                interpolate_color(
                    COLOR_GOLDEN_HOUR_START, COLOR_SUN,
                    self.morning_times.golden_start,
                    self.morning_times.golden_end,
                    timestamp),
                interpolate_color(
                    COLOR_NIGHTSKY, COLOR_LIGHTSKY,
                    self.morning_times.golden_start,
                    self.morning_times.golden_end,
                    timestamp),
                interpolate_color(
                    COLOR_NIGHTSKY, COLOR_GROUND,
                    self.morning_times.golden_start,
                    self.morning_times.golden_end,
                    timestamp))


        # evening golden hour
        if self.evening_times.golden_start <= timestamp < self.evening_times.golden_end:
            return Sun(
                sunset_pixel,
                interpolate_color(
                    COLOR_SUN, COLOR_GOLDEN_HOUR_START,
                    self.evening_times.golden_start,
                    self.evening_times.golden_end,
                    timestamp),
                interpolate_color(
                    COLOR_LIGHTSKY, COLOR_NIGHTSKY,
                    self.evening_times.golden_start,
                    self.evening_times.golden_end,
                    timestamp),
                interpolate_color(
                    COLOR_GROUND, COLOR_NIGHTSKY,
                    self.evening_times.golden_start,
                    self.evening_times.golden_end,
                    timestamp))

        # evening blue hour
        #
        return Sun(
            sunset_pixel,
            interpolate_color(
                COLOR_GOLDEN_HOUR_START, COLOR_NIGHTSKY,
                self.evening_times.blue_start,
                self.evening_times.blue_end,
                timestamp),
            COLOR_NIGHTSKY,
            COLOR_NIGHTSKY)

    def _sun_angle(self, timestamp):
        ''' Return the sun's angle
        '''
        return (
            DAYLIGHT_ANGLE +
            ((timestamp - self.morning_times.golden_end) / self.daylight_seconds) *
            (180 - DAYLIGHT_ANGLE * 2))

    def get_times(self, today, direction):
        ''' Get sunrise/sunset times
        '''
        blue = sun.blue_hour(
            observer=self.observer, date=today, direction=direction, tzinfo=self.timezone)

        golden = sun.golden_hour(
            observer=self.observer, date=today, direction=direction, tzinfo=self.timezone)

        if self.debug:
            if direction == astral.SunDirection.RISING:
                print('blue start', blue[0], flush=True)
                print('gold start', golden[0], flush=True)
                print('gold end  ', golden[1], flush=True)
            else:
                print()
                print('gold start', golden[0])
                print('blue start', blue[0])
                print('blue end  ', blue[1], flush=True)

        return SunTimes(
            blue[0].timestamp(), blue[1].timestamp(),
            golden[0].timestamp(), golden[1].timestamp())


async def get_request_data(request):
    ''' Obtain http request json data
    '''
    try:
        data = await request.json()
    except: #pylint: disable=bare-except
        print('invalid mode received from browser')
        data = dict()

    return data


def parse_args():
    ''' Parse command line args
    '''
    parser = ArgumentParser(
        prog='wc',
        description='The Word Clock')

    parser.add_argument(
        '--daemon',
        action='store_true',
        default=False,
        help='Run in daemon mode')

    parser.add_argument(
        '--debug',
        action='store_true',
        default=False,
        help='Print verbose debugging statements')

    return parser.parse_args()


class Main():
    ''' do everything here
    '''
    #pylint: disable=too-many-instance-attributes,too-many-public-methods

    def __init__(self):
        self.args = parse_args()
        self.state = State.STARTING
        self.display_mode = DisplayMode.CLOCK
        self.is_on = True
        self.timezone = pytz.utc
        self.today = None
        self.astral_info = None
        self.birthday_name = None
        self.do_birthday = False
        self.light_sensor = None
        self.server_ip = 'unknown'

        self.futzing = False
        self.last_ping = None

        self.loop = asyncio.get_event_loop()
        self.start_hotspot_event = asyncio.Event()
        self.http_runner = None

        self.button_down_time = None # Time when the button was last pressed (None if not pressed)
        self.button_up_time = None   # Time when the button was last released
        self.button_presses = 0
        self.button_duration = 0     # The duration of the last button press

        #pylint: disable=no-member
        GPIO.setup(PIN_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(PIN_BUTTON, GPIO.BOTH, callback=self.handle_button, bouncetime=100)
        #pylint: enable=no-member

        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.init_light_sensor()
        self.compass = magnetometer.Magnetometer(self.i2c, not self.args.daemon)

        self.cur_ambient = 0
        self.brightness_factor = 1
        self.orientation = magnetometer.Orientation(0, magnetometer.TOP_UP)
        self.cur_angle = self.orientation.angle
        self.sunrise = SUNRISE_LEFT

        self.read_params()

        self.pixels = neopixel.NeoPixel(PIN_PIXELS, N_PIXELS, auto_write=False)

    def main(self):
        ''' do it
        '''
        self.loop.run_until_complete(self.run_http_server())
        self.loop.create_task(self.manage_button())
        self.loop.create_task(self.co_check_wifi())
        self.loop.create_task(self.display_status())
        self.loop.create_task(self.update_compass())
        self.loop.create_task(self.display_clock())
        self.loop.create_task(self.handle_start_hotspot_event())

        if self.params.get(PARAM_SSID):
            self.state = State.WIFI_INIT
        else:
            self.state = State.HOTSPOT if start_hotspot(not self.args.daemon) else State.ERROR

        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass

        self.loop.run_until_complete(self.http_runner.cleanup())

    def init_light_sensor(self):
        ''' Initialize the ambient light sensor
        '''
        if self.light_sensor is None:
            try:
                self.light_sensor = adafruit_veml7700.VEML7700(self.i2c)

                if not self.args.daemon:
                    print('Initialized light sensor', flush=True)

            except Exception as err: #pylint: disable=broad-except
                print('Failed to init light sensor:', str(err), flush=True)

    def read_params(self):
        ''' Read our parameters
        '''
        self.params = {
            PARAM_SSID: '',
            PARAM_PASSWORD: '',
            PARAM_LAT: config.LAT,
            PARAM_LON: config.LON,
            PARAM_MIN_LIGHT: DEFAULT_MIN_LIGHT,
            PARAM_MIN_BRIGHTNESS: DEFAULT_MIN_BRIGHTNESS,
            PARAM_MAX_LIGHT: DEFAULT_MAX_LIGHT,
            PARAM_MAX_BRIGHTNESS: DEFAULT_MAX_BRIGHTNESS,
            PARAM_SUNRISE: DEFAULT_SUNRISE,
        }

        try:
            self.read_params_file(PARAMS_FILE)
            self.read_params_file(WIFI_PARAMS_FILE)

            self.set_timezone()

            if self.args.debug:
                print(self.params)

        except Exception as err: #pylint: disable=broad-except
            print('Error reading params:', str(err), flush=True)
            traceback.print_exc()

    def read_params_file(self, path):
        ''' Read a params file
        '''
        if os.path.isfile(path):
            with open(path, 'r') as fil:
                self.params.update(json.loads(fil.read()))

    def write_params_file(self, path, filter_func):
        ''' Write a params file
        '''
        with open(path, 'w') as fil:
            fil.write(
                json.dumps(
                    {key: value for key, value in self.params.items()
                     if filter_func(key)},
                    indent=2, sort_keys=True))

    async def run_http_server(self):
        ''' Run our web server.
        '''
        app = web.Application()
        app.add_routes([
            web.static('/static', '/var/wordclock/website/static'),
            web.get('/', self.handle_get_body),
            web.get('/vars.js', self.handle_get_vars),
            web.post('/save', self.handle_post_save),
            web.post('/mode', self.handle_post_mode),
            web.get('/state', self.handle_get_state),
            web.post('/futz', self.handle_post_futz),
            web.get('/ping', self.handle_get_ping),
            ])

        self.http_runner = web.AppRunner(app)
        await self.http_runner.setup()
        site = web.TCPSite(self.http_runner, host=None, port=PORT_HTTP)
        await site.start()

    async def handle_get_body(self, _request):
        ''' handle web get main body
        '''
        if self.args.debug:
            print('send body')

        with open(BODY_FILE, 'r') as fil:
            body = fil.read()

        return web.Response(
            text=body.format(title=SETTINGS_TITLE),
            content_type='text/html')

    async def handle_get_vars(self, _request):
        ''' handle web get javascript vars
        '''
        params_sans_password = self.params.copy()
        params_sans_password[PARAM_PASSWORD] = ''
        is_hotspot = self.state == State.HOTSPOT

        js_vars = (
            'var curSettings = {settings};\n'
            'var newSettings = {settings};\n'
            'var State = {state};\n'
            'var isHotspot = {is_hotspot}\n'
            'var serverIp = "{server_ip}"\n'
            'var version = "{version}"\n'
            '\n'.format(
                settings=json.dumps(params_sans_password),
                state=json.dumps(
                    dict(
                        ambient=self.cur_ambient,
                    )
                ),
                is_hotspot='true' if is_hotspot else 'false',
                server_ip=HOTSPOT_IP if is_hotspot else self.server_ip,
                version=__version__,
            ))

        if self.args.debug:
            print('send vars:\n{}'.format(js_vars))

        return web.Response(content_type='text/javascript', text=js_vars)

    async def handle_post_save(self, request):
        ''' handle web ajax post save changes
        '''
        data = await get_request_data(request)

        if data:
            if self.args.debug:
                print('save:', data)

            return self.do_config_save(data)

        raise web.HTTPBadRequest()

    async def handle_post_mode(self, request):
        ''' handle web ajax post change clock mode
        '''
        data = await get_request_data(request)

        if data:
            if self.args.debug:
                print('mode:', data)

            new_mode = DisplayMode[data.get('display_mode')]

            if self.display_mode != new_mode:
                self.is_on = True
                self.set_display_mode(new_mode)
                self.update_clock()

        return  web.json_response(dict())

    async def handle_get_state(self, _request):
        ''' handle web ajax get current clock state
        '''
        state = dict(
            cur_ambient=int(self.cur_ambient),
            cur_brightness=round(self.brightness_factor * 100),
            cur_angle=round(self.orientation.angle),
            cur_orientation=self.orientation.orientation,
            display_mode=self.display_mode.name,
            sunrise_orientation=self.get_compass_sunrise())

        if self.args.debug:
            print('state:', state)

        return web.json_response(state)

    async def handle_post_futz(self, request):
        ''' handle web ajax post turn futz mode on/off
        '''
        data = await get_request_data(request)

        if bool(data):
            if self.args.debug:
                print('futz:', data)

            self.futzing = True
            self.last_ping = time.time()
            self.brightness_factor = max(0, min(100, data.get('brightness', 100))) / 100

            self.write_clock(
                datetime.datetime(
                    2021, 3, 7,
                    hour=0 if data.get('display') == FUTZ_DISPLAY_MIDNIGHT else 12,
                    tzinfo=self.timezone))
        else:
            self.stop_futzing()

        return web.json_response(dict())

    async def handle_get_ping(self, _request):
        ''' handle web ajax get ping request (to keep futz mode alive)
        '''
        self.last_ping = time.time()

        if self.args.debug:
            print('ping', self.futzing, self.last_ping)

        # Tell the browser to stop, except on the very first ping
        return web.json_response(dict(ok=self.futzing or self.last_ping is None))

    def stop_futzing(self):
        ''' stop futzing with brightness
        '''
        self.futzing = False
        self.last_ping = None
        self.set_brightness_factor()
        self.update_clock()

    def do_config_save(self, data):
        ''' Save config
        '''
        try:
            new_ssid = data[PARAM_SSID]
            new_password = data[PARAM_PASSWORD]
            password_changed = bool(new_password)

            if not password_changed:
                new_password = data[PARAM_PASSWORD] = self.params[PARAM_PASSWORD]

            changed_wifi = self.params[PARAM_SSID] != new_ssid or password_changed

            changed_latlon = any(
                self.params[key] != data[key] for key in [PARAM_LAT, PARAM_LON])

            self.params.update(data)

            self.write_params_file(PARAMS_FILE, lambda x: x not in WIFI_PARAMS)
            self.write_params_file(WIFI_PARAMS_FILE, lambda x: x in WIFI_PARAMS)

            running_hotspot = self.state == State.HOTSPOT
            activating_wifi = changed_wifi or running_hotspot

            response = dict(
                ok=True,
                wifi_changed=activating_wifi,
                msg=(
                    'Activating WiFi connection. '
                    'If it doesn\'t work, press the clock settings button '
                    'for 3 seconds to revert to hotspot mode and try '
                    'entering the settings again.'
                    if activating_wifi
                    else 'Settings saved'))

           # wifi changed below don't happen until after we've sent the response

            if changed_wifi:
                self.configure_wifi(new_ssid, new_password)

            elif running_hotspot:
                if not self.args.daemon:
                    print('hotspot -> starting wifi', flush=True)
                self.loop.create_task(self.co_start_wifi())

            if changed_latlon:
                self.set_timezone()

            self.set_brightness_factor()
            self.set_sunrise_orientation()
            self.update_clock()

        except Exception as err: #pylint: disable=broad-except
            traceback.print_exc()
            response = dict(ok=False, wifi_changed=False, msg='Error: {}'.format(err))

        return web.Response(text=json.dumps(response), content_type='text/json')

    async def manage_button(self):
        ''' Monitor button presses
        '''
        while True:
            if (not self.button_down_time and self.button_presses and
                    time.time() - self.button_up_time > 1):

                if self.args.debug:
                    print('button presses', self.button_presses, flush=True)

                if self.button_presses == 1:
                    self.do_button_press_1()
                else:
                    self.is_on = True

                    if self.button_presses == 2:
                        self.set_display_mode(DisplayMode.RANDOM_WORDS)
                    elif self.button_presses == 3:
                        self.set_display_mode(DisplayMode.DEMO)
                    elif self.button_presses == 4:
                        self.set_display_mode(DisplayMode.DEMO_BIRTHDAY)

                self.button_presses = 0
                self.do_birthday = False
                self.update_clock()

            await asyncio.sleep(0.1)

    def set_display_mode(self, mode):
        ''' Set the display mode
        '''
        self.display_mode = mode

        if mode == DisplayMode.RANDOM_WORDS:
            self.loop.create_task(self.display_random())
        elif mode == DisplayMode.DEMO:
            self.loop.create_task(self.display_demo())
        elif mode == DisplayMode.DEMO_BIRTHDAY:
            self.loop.create_task(self.display_birthday_demo())

    def do_button_press_1(self):
        ''' Handle a single button press
        '''
        if self.button_duration >= LONG_PRESS_DURATION:
            if self.args.debug:
                print('long press', flush=True)
            self.display_mode = DisplayMode.CLOCK
            self.start_hotspot_event.set()
        else:
            if self.state == State.HOTSPOT:
                self.loop.create_task(self.co_start_wifi())

            elif self.is_on:
                if self.display_mode != DisplayMode.CLOCK:
                    self.display_mode = DisplayMode.CLOCK
                else:
                    self.is_on = False
                    self.pixels.fill(COLOR_OFF)
                    self.pixels.show()
            else:
                self.is_on = True

    async def co_check_wifi(self):
        ''' Check the wifi connection every 10 seconds
        '''
        n_failures = 0

        while True:
            if self.state in [State.WIFI_INIT, State.WIFI_ACTIVE]:

                if self.args.debug:
                    print('checking wifi', self.state, flush=True)

                self.server_ip = await self.loop.run_in_executor(None, check_wifi, self.args.debug)

                if self.server_ip:
                    new_state = State.WIFI_ACTIVE
                    n_failures = 0

                else:
                    if self.state == State.WIFI_ACTIVE:
                        n_failures += 1

                        if not self.args.daemon:
                            print(
                                str(datetime.datetime.now()),
                                'wifi failures:', n_failures, flush=True)

                        if n_failures == 6:
                            new_state = State.WIFI_INIT
                            n_failures = 0
                        else:
                            new_state = self.state
                    else:
                        if not self.args.daemon:
                            print(str(datetime.datetime.now()), 'wifi still down', flush=True)

                if self.state != new_state:
                    if not self.args.daemon:
                        print(
                            str(datetime.datetime.now()),
                            'wifi -> {}'.format(new_state), flush=True)
                    self.state = new_state
                    self.update_clock()
            else:
                n_failures = 0

            await asyncio.sleep(10)

    async def display_status(self):
        ''' Display status lights when not running the clock.
            Also monitor ambient light and compass
        '''
        light_history = deque()

        while True:
            now = time.time()
            now_quarter_second = round(now * 4) / 4
            at_second = now_quarter_second % 1 == 0

            if at_second:
                if self.update_ambient(light_history) and not self.futzing:
                    self.update_clock()

                if self.futzing and self.last_ping and now - self.last_ping > 5:
                    self.stop_futzing()

            if (self.button_down_time or self.button_presses or
                    self.is_on and self.state != State.WIFI_ACTIVE):

                self.pixels.fill(COLOR_OFF)

                if self.button_down_time and self.button_presses == 0:
                    is_long = now - self.button_down_time >= LONG_PRESS_DURATION
                elif not self.button_down_time and self.button_presses == 1:
                    is_long = self.button_duration >= LONG_PRESS_DURATION
                else:
                    is_long = False

                if self.button_down_time or self.button_presses:
                    for i in range(self.button_presses + (1 if self.button_down_time else 0)):
                        self.set_numeric_pixel(
                            i+1,
                            COLOR_LONG_BUTTON_PRESS if is_long else COLOR_BUTTON_PRESS)

                else:
                    # If not first quarter of quarter-second
                    if not at_second:
                        state_display = STATE_DISPLAY[self.state]
                        self.set_numeric_pixel(state_display.index, state_display.color)

                self.pixels.show()

            await asyncio.sleep(now_quarter_second + 0.25 - now)

    async def update_compass(self):
        ''' Update the compass
        '''
        while True:
            self.orientation = await self.loop.run_in_executor(None, self.do_update_compass)

            # This is to prevent is from jittering between left and right sunrises.
            if (self.orientation.angle is not None and
                    abs(self.cur_angle - self.orientation.angle) > COMPASS_JITTER_THRESHOLD):
                self.cur_angle = self.orientation.angle

            self.set_sunrise_orientation()
            await asyncio.sleep(2)

    def do_update_compass(self):
        ''' Update the compass
        '''
        return self.compass.update(
            verbose=self.args.debug,
            lat=self.params.get(PARAM_LAT),
            lon=self.params.get(PARAM_LON))

    def set_sunrise_orientation(self):
        ''' Set the sunrise orientation
        '''
        self.sunrise = self.params[PARAM_SUNRISE]

        if self.sunrise == SUNRISE_COMPASS:
            self.sunrise = self.get_compass_sunrise()

    def get_compass_sunrise(self):
        ''' Return the sunrise orientation for the current compass direction
        '''
        return (
            SUNRISE_LEFT
            if self.cur_angle > 270 or self.cur_angle <= 90
            else SUNRISE_RIGHT)

    async def display_clock(self):
        ''' Update the clock
        '''
        while True:
            await asyncio.sleep(self.update_clock())

    async def display_demo(self):
        ''' Update the clock in demo mode
        '''
        state = "sunrise"
        # A Sunday
        start_day = datetime.date(2021, 3, 7)

        # Start 15 minutes before the blue hour
        sunrise_times = self.astral_info.get_times(start_day, astral.SunDirection.RISING)
        sunset_times = self.astral_info.get_times(start_day, astral.SunDirection.SETTING)

        baseline = {
            SR_BEGIN: self.round_up_5(sunrise_times.blue_start, -14),
            SR_END: self.round_up_5(sunrise_times.golden_end, 9),
            SS_BEGIN: self.round_up_5(sunset_times.golden_start, -14),
            SS_END: self.round_up_5(sunset_times.blue_end, 9),
            }

        if not self.args.daemon:
            print(baseline)

        cur = baseline
        demo_now = cur[SR_BEGIN]
        sleep = 0.1

        def _do_sunrise():
            nonlocal demo_now, sleep, state, cur

            if demo_now == cur[SR_BEGIN]:
                sleep = 2
            elif demo_now >= cur[SR_END]:
                sleep = 1

            if demo_now > cur[SR_END]:
                state = 'day'
                demo_now = demo_now.replace(hour=demo_now.hour+1, minute=0)

        def _do_day():
            nonlocal demo_now, sleep, state, cur

            sleep = 1
            demo_now = demo_now.replace(hour=demo_now.hour + 1, minute=0)

            if demo_now.hour == cur[SS_BEGIN].hour:
                state = 'before_sunset'

        def _do_before_sunset():
            nonlocal demo_now, sleep, state, cur

            demo_now = cur[SS_BEGIN]
            state = 'sunset'
            sleep = 1

        def _do_sunset():
            nonlocal demo_now, sleep, state, cur

            if demo_now == cur[SS_END]:
                sleep = 5

            elif demo_now > cur[SS_END]:
                state = 'sunrise'
                sleep = 1

                if demo_now.day >= cur[SR_BEGIN].day + 6:
                    cur = baseline
                else:
                    for key, value in cur.items():
                        cur[key] = value.replace(day=value.day+1)

                demo_now = cur[SR_BEGIN]

        do_switch = dict(
            sunrise=_do_sunrise,
            day=_do_day,
            before_sunset=_do_before_sunset,
            sunset=_do_sunset,
            )

        while self.display_mode == DisplayMode.DEMO:
            sleep = 0.1
            do_switch[state]()

            if not self.args.daemon:
                print(state, demo_now, sleep)

            if self.should_run(DisplayMode.DEMO):
                self.write_clock(demo_now)

            demo_now = demo_now + datetime.timedelta(minutes=1)
            await asyncio.sleep(sleep)

    async def display_random(self):
        ''' Update random workds
        '''
        random_words = config.ALL_WORDS.copy()
        random.shuffle(random_words)
        random_index = 0

        while self.display_mode == DisplayMode.RANDOM_WORDS:
            if self.should_run(DisplayMode.RANDOM_WORDS):
                word = random_words[random_index]
                random_index = (random_index + 1) % len(random_words)

                if self.args.debug:
                    print(word.text)

                self.pixels.fill(COLOR_OFF)
                self.set_word(word, color=random.choice(RANDOM_COLORS))

                for i in range(BORDER_PIXELS_BASE, BORDER_PIXELS_END):
                    self.set_pixel(i, COLOR_RANDOM_BORDER)

                self.pixels.show()

            await asyncio.sleep(1)

    async def display_birthday_demo(self):
        ''' Update the clock in demo mode
        '''
        self.do_birthday = True
        self.loop.create_task(self.display_birthday())

        birthday_names = list(config.BIRTHDAYS.values())
        index = 0

        while self.display_mode == DisplayMode.DEMO_BIRTHDAY:
            if self.should_run(DisplayMode.DEMO_BIRTHDAY):
                self.birthday_name = birthday_names[index]
                index = (index + 1) % len(birthday_names)

            await asyncio.sleep(2)

        self.do_birthday = False

    def update_ambient(self, light_history):
        ''' Update ambient light settings
        '''
        self.init_light_sensor()

        if self.light_sensor is not None:
            try:
                light_history.append(self.light_sensor.light)
            except Exception as err: #pylint: disable=broad-except
                self.light_sensor = None
                print('Exception reading light sensor: {}'.format(err), flush=True)

        if self.light_sensor is None:
            changed = False
        else:
            if len(light_history) > AMBIENT_SMOOTHING_DEQUE_LEN:
                light_history.popleft()

            self.cur_ambient = round(sum(light_history) / len(light_history))
            changed = self.set_brightness_factor()

        return changed

    def set_brightness_factor(self):
        ''' Set the current brightness
        '''
        min_light = self.params[PARAM_MIN_LIGHT]
        max_light = self.params[PARAM_MAX_LIGHT]

        min_brightness = self.params[PARAM_MIN_BRIGHTNESS]
        max_brightness = self.params[PARAM_MAX_BRIGHTNESS]

        bounded_light = max(min_light, min(max_light, self.cur_ambient))
        light_range = max_light - min_light
        light_factor = (bounded_light - min_light) / light_range if light_range else 1

        cur_factor = self.brightness_factor

        self.brightness_factor = (
            (min_brightness + light_factor * (max_brightness - min_brightness)) / 100)

        if self.args.debug:
            print(
                'min lt', min_light,
                'max lt', max_light,
                'min br', min_brightness,
                'max br', max_brightness)
            print(
                'amb', round(self.cur_ambient, 2),
                'bound', round(bounded_light, 2),
                'lightfactor', round(light_factor, 2),
                'brightfactor', round(self.brightness_factor, 2),
                flush=True)

        return abs(cur_factor - self.brightness_factor) > 0.05

    def update_clock(self):
        ''' Update the clock display
        '''
        now = datetime.datetime.now(self.timezone)
        now_minute = now.replace(second=0, microsecond=0)

        if self.args.debug:
            print('clock', now, now_minute, flush=True)

        if self.should_run(DisplayMode.CLOCK):
            self.write_clock(now_minute)

        return (now_minute + datetime.timedelta(minutes=1) - now).total_seconds()

    def write_clock(self, now_minute):
        ''' display the clock
        '''
        self.set_day(now_minute)

        if (self.display_mode == DisplayMode.CLOCK
                and self.birthday_name
                and now_minute.minute == 0):

            if not self.do_birthday:
                self.do_birthday = True
                self.loop.create_task(self.display_birthday())
        else:
            self.do_birthday = False

            self.pixels.fill(COLOR_OFF)
            self.write_time(now_minute)
            self.write_minute(now_minute)
            self.write_weekday(now_minute)
            self.write_sun(now_minute)
            self.pixels.show()

    def write_time(self, now_minute):
        ''' Write the time sentence
        '''
        hour = now_minute.hour
        delta = now_minute.minute // 5

        self.set_word(config.IT)
        self.set_word(config.IS)

        minute_word = DELTAS[delta]

        if minute_word:
            self.set_word(minute_word)

            if delta < 7:
                self.set_word(config.PAST)
            else:
                self.set_word(config.TO)
                hour += 1
        else:
            self.set_word(config.OCLOCK)

        self.set_word(HOURS[hour % len(HOURS)])

    def write_minute(self, now_minute):
        ''' Write the minute digit
        '''
        min_part = now_minute.minute % 5
        for i in range(5):
            self.set_face_pixel(
                NUMERIC_PIXELS_X+i,
                NUMERIC_PIXELS_Y,
                COLOR_MINUTE if min_part == i else COLOR_OFF)

    def write_weekday(self, now_minute):
        ''' Write the weekday
        '''
        # weekday() returns mon==0, sun==6
        weekday = (now_minute.weekday() + 1) % 7

        for i in range(7):
            self.set_face_pixel(
                DOW_PIXELS_X+i,
                DOW_PIXELS_Y,
                COLOR_DAY if weekday == i else COLOR_DAY_OFF)

    def write_sun(self, now_minute):
        ''' Write the sun border
        '''
        sun_params = self.astral_info.get_sun(now_minute.timestamp(), self.sunrise)

        for i in ASTRAL_PIXELS_RANGE:
            self.set_pixel(i, sun_params.sky_color)

        for i in GROUND_PIXELS_RANGE:
            self.set_pixel(i, sun_params.ground_color)

        if sun_params.sun_pixel:
            self.set_pixel(sun_params.sun_pixel, sun_params.sun_color)

    async def display_birthday(self):
        ''' Display the birthday message
        '''
        offset = 0

        while self.do_birthday:
            if not self.button_presses:
                self.pixels.fill(COLOR_OFF)

                self.set_word(config.HAPPY)
                self.set_word(config.BIRTHDAY)
                self.set_word(self.birthday_name)

                for i in range(
                        BORDER_PIXELS_BASE + MARQEE_LIGHT_DELTA - offset - 1,
                        BORDER_PIXELS_BASE + BORDER_PIXELS_LEN,
                        MARQEE_LIGHT_DELTA):
                    self.set_pixel(i, COLOR_BORDER_LIGHT1)

                for i in range(
                        offset,
                        len(MARQEE_PIXELS),
                        MARQEE_LIGHT_DELTA):
                    self.set_pixel(MARQEE_PIXELS[i], COLOR_BORDER_LIGHT2)

                self.pixels.show()
                offset = (offset + 1) % MARQEE_LIGHT_DELTA

            await asyncio.sleep(0.1)

    def set_day(self, now_minute):
        ''' bump the day
        '''
        today = now_minute.date()

        if today != self.today:
            self.today = today
            self.astral_info.set_day(today)

        # Always set the birthday_name, because the birthday demo mode overwrites it
        #
        if (config.SPECIAL_BIRTHDAY and
                config.SPECIAL_BIRTHDAY.begin <= today < config.SPECIAL_BIRTHDAY.end):
            self.birthday_name = config.SPECIAL_BIRTHDAY.name
        else:
            self.birthday_name = config.BIRTHDAYS.get(
                config.BirthDate(now_minute.month, now_minute.day))

    def set_word(self, word, color=None):
        ''' Set a word pixels
        '''
        if color is None:
            color = COLOR_WORD

        if word.vertical:
            for y_i in range(word.y, word.y + len(word.text)):
                self.set_pixel(PIXEL_MAP[word.x][y_i], color)
        else:
            for x_i in range(word.x, word.x + len(word.text)):
                self.set_pixel(PIXEL_MAP[x_i][word.y], color)

    def set_numeric_pixel(self, index, color):
        ''' Set a numeric pixel
        '''
        self.set_face_pixel(NUMERIC_PIXELS_X + index, NUMERIC_PIXELS_Y, color, full=True)

    def set_face_pixel(self, index_x, index_y, color, full=False):
        ''' Set a face pixel
        '''
        self.set_pixel(PIXEL_MAP[index_x][index_y], color, full)

    def set_pixel(self, index, color, full=False):
        ''' Set a pixel
        '''
        self.pixels[index] = (
            color if full or self.brightness_factor == 1
            else (
                round(color[0] * self.brightness_factor),
                round(color[1] * self.brightness_factor),
                round(color[2] * self.brightness_factor)))

    def handle_button(self, _channel):
        ''' Handle button events. This function runs in a separate thread.
        '''
        asyncio.run_coroutine_threadsafe(self.co_handle_button(), self.loop)

    async def co_handle_button(self):
        ''' Handle button events in a coroutine
        '''
        self.stop_futzing()
        now = time.time()
        await asyncio.sleep(0.050)

        if GPIO.input(PIN_BUTTON): #pylint: disable=no-member
            self.button_up_time = now
            self.button_duration = now - self.button_down_time if self.button_down_time else 0
            self.button_down_time = None

            if self.button_presses < 4:
                self.button_presses += 1

            if self.args.debug:
                print('up', self.button_presses, now, self.button_duration, flush=True)
        else:
            self.button_down_time = now
            if self.args.debug:
                print('down', self.button_down_time, flush=True)

    async def handle_start_hotspot_event(self):
        ''' Start the hotspot in a background thread
        '''
        while True:
            await self.start_hotspot_event.wait()
            self.start_hotspot_event.clear()

            if not self.state == State.HOTSPOT:
                self.state = State.HOTSPOT

                if not await self.loop.run_in_executor(None, start_hotspot, not self.args.daemon):
                    self.state = State.ERROR

    def configure_wifi(self, ssid, password):
        ''' Configure and start wifi
        '''
        if not self.args.daemon:
            print('new wifi settings', ssid, password, flush=True)

        with open(WPA_SUPPLICANT_CONF_FILE, 'w') as fil:
            fil.write(WPA_SUPPLICATION_CONF_FMT.format(ssid=ssid, password=password))

        self.loop.create_task(self.co_start_wifi())

    async def co_start_wifi(self):
        ''' Wait a couple of seconds and then start wifi
        '''
        old_state = self.state
        self.state = State.WIFI_INIT
        await asyncio.sleep(2)
        self.loop.run_in_executor(None, start_wifi, old_state)

    def set_timezone(self):
        ''' Set the timezone, based on lat/lon
        '''
        self.timezone = pytz.utc
        tz_name = None

        try:
            lat = self.params.get(PARAM_LAT)
            lon = self.params.get(PARAM_LON)

            if lat and lon:
                tz_name = TimezoneFinder().timezone_at(lat=lat, lng=lon)
                self.timezone = pytz.timezone(tz_name)
                self.astral_info = AstralInfo(lat, lon, self.timezone, not self.args.daemon)

        except Exception as err: #pylint: disable=broad-except
            print('Exception setting timezone: {}'.format(err))
            traceback.print_exc()

        if not self.args.daemon:
            print(lat, lon, tz_name, self.timezone, flush=True)

    def should_run(self, mode):
        ''' Should we run this mode?
        '''
        return (
            self.state == State.WIFI_ACTIVE
            and self.is_on
            and self.display_mode == mode
            and not (self.button_down_time or self.button_presses)
            and not self.futzing)


    def round_up_5(self, timestamp, offset):
        ''' Add an offset to a timestamp and round the result up to the nearest 5-minute point.
            Return a datetime.
        '''
        return datetime.datetime.fromtimestamp(
            round((timestamp + offset*60) / (5*60)) * 5*60,
            tz=self.timezone)


def check_wifi(debug):
    ''' Check wifi status in background
    '''
    matcher = re.compile(r'\s*inet\s+(?P<ip>\d+\.\d+\.\d+\.\d+).*broadcast')
    output = subprocess.check_output(['ifconfig', 'wlan0']).decode()

    for line in output.splitlines():
        match = matcher.match(line)

        if match:
            if debug:
                print(line)

            return match.group('ip')

    if debug:
        print('-- ifconfig output --')
        print(output, flush=True)

    return None


def interpolate1(start, end, factor):
    ''' Interpolote two points
    '''
    return int(start + (end - start) * factor)


def interpolate_color(color_start, color_end, start, end, timestamp):
    ''' Interpolate a color tuple
    '''
    factor = (timestamp - start) / (end - start)

    return (
        interpolate1(color_start[0], color_end[0], factor),
        interpolate1(color_start[1], color_end[1], factor),
        interpolate1(color_start[2], color_end[2], factor))


def start_hotspot(debug):
    ''' Switch to hotspot mode
    '''
    if debug:
        print('starting hotspot', flush=True)

    try:
        subprocess.check_call(['hotspot', 'start'])
        result = True
    except Exception as err: #pylint: disable=broad-except
        print('Failed to start hotspot: {}'.format(err), flush=True)
        result = False

    return result


def start_wifi(state):
    ''' Start wifi
    '''
    try:
        if state == State.HOTSPOT:
            subprocess.check_call(['hotspot', 'stop'])

        subprocess.check_call(['wpa_cli', '-i', 'wlan0', 'reconfigure'])

    except Exception as err: #pylint: disable=broad-except
        print('Exception starting wifi: {}'.format(err), flush=True)


def main():
    ''' do it
    '''
    Main().main()
