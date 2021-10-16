''' Display all words
'''

import time
import argparse
import board
import neopixel

from wordclock import config #pylint: disable=configdefs
from wordclock import configdefs

PIN_PIXELS = board.D18
DIM = 12
N_PIXELS = DIM*DIM + 24 * 4

COLOR_OFF = (0, 0, 0)
COLOR_ON = (255, 255, 255)

PIXEL_MAP = [
    [(DIM-1-x) * DIM + (DIM-1-y if x % 2 else y) for y in range(DIM)]
    for x in range(DIM)
    ]


def main():
    ''' do it
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('--auto', '-a', action='store_true')
    args = parser.parse_args()

    all_words_in_grid_order = sorted(configdefs.ALL_WORDS, key=lambda x: (x.y, x.x))
    pixels = neopixel.NeoPixel(PIN_PIXELS, N_PIXELS, auto_write=False)

    def set_pixel(index):
        ''' Set a pixel
        '''
        pixels[index] = COLOR_ON

    def set_word(word):
        ''' Set a word pixels
        '''
        if word.vertical:
            for y_i in range(word.y, word.y + len(word.text)):
                set_pixel(PIXEL_MAP[word.x][y_i])
        else:
            for x_i in range(word.x, word.x + len(word.text)):
                set_pixel(PIXEL_MAP[x_i][word.y])

    try:
        while True:
            for word in all_words_in_grid_order:
                pixels.fill(COLOR_OFF)
                set_word(word)
                pixels.show()
                prompt = f'{word.text} {word.y} {word.x}'

                if args.auto:
                    print(prompt)
                    time.sleep(1)
                else:
                    input(prompt + ': ')

    except KeyboardInterrupt: #pylint: disable=bare-except
        pass
