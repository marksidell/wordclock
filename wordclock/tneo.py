''' test neopixels
'''
import argparse
import time
import board
import neopixel

DIM = 12
BORDER_BEGIN = DIM*DIM
BORDER_DIM_V1 = DIM*4
BORDER_DIM_V2 = DIM*4*2


def parse_args(args, border_dim):
    ''' parse the args
    '''
    do_shift = False

    if args.all:
        begin = 0
        end = begin + DIM
    elif args.strip is not None:
        if args.strip >= DIM:
            begin = BORDER_BEGIN
            end = begin + border_dim
        else:
            begin = args.strip * DIM
            end = begin + DIM
    elif args.begin is not None:
        begin = args.begin
        end = args.end if args.end else begin + DIM
    else:
        begin = end = 0
        do_shift = True

    return (do_shift, begin, end)


def main():
    ''' do it
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('--begin', '-b', type=int)
    parser.add_argument('--end', '-e', type=int)
    parser.add_argument('--strip', '-s', type=int)
    parser.add_argument('--all', '-a', action='store_true')
    parser.add_argument('--v1', action='store_true')

    args = parser.parse_args()

    border_dim = BORDER_DIM_V1 if args.v1 else BORDER_DIM_V2
    n_pixels = BORDER_BEGIN + border_dim

    do_shift, begin, end = parse_args(args, border_dim)
    print(begin, end, do_shift)

    pixels = neopixel.NeoPixel(board.D18, n_pixels, auto_write=False)
    pixels.fill((0, 0, 0))

    try:
        while True:
            if do_shift:
                for i in range(0, n_pixels):
                    pixels[i] = (255, 255, 255)
                    pixels.show()
                    time.sleep(4 / n_pixels)
                    pixels[i] = (0, 0, 0)
                continue

            for color in [(0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255)]:
                for i in range(begin, end):
                    pixels[i] = color

                pixels.show()
                time.sleep(0.5)

            if args.all:
                begin = 0 if begin >= BORDER_BEGIN else begin + DIM
                end = begin + (border_dim if begin == BORDER_BEGIN else DIM)
                pixels.fill((0, 0, 0))

    except KeyboardInterrupt: #pylint: disable=bare-except
        pass
