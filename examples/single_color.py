"""
examples/spectrum.py

Commands the LEDs to all output a single color.

See LICENSE.txt for more details.
"""
import argparse
import sys

sys.path.append('..')  # Not required if running with apa102_gpiod installed
import apa102_gpiod.apa102 as apa102

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Output a single color '
                                                 'on all the LEDs')
    parser.add_argument('chip', action='store',
                        help='gpiochip used to control I/O lines connected to '
                             'the LEDs')
    parser.add_argument('clk', action='store',
                        type=int, help='gpio line offset of the gpio line '
                                       'corresponding to the clock line')
    parser.add_argument('data', action='store',
                        type=int, help='gpio line offset of the gpio line '
                                       'corresponding to the data line')
    parser.add_argument('leds', action='store',
                        type=int, help='number of LEDs to drive')
    parser.add_argument('brightness', action='store',
                        type=int, choices=range(32),
                        help='led brightness setting')
    parser.add_argument('r', action='store',
                        type=int, help='red component of the color, '
                                       '[0, 255]')
    parser.add_argument('g', action='store',
                        type=int, help='green component of the color, '
                                       '[0, 255]')
    parser.add_argument('b', action='store',
                        type=int, help='blue component of the color, '
                                       '[0, 255]')
    args = parser.parse_args()

    leds = apa102.APA102(args.chip, args.leds, args.clk, args.data,
                         True)
    for led in range(len(leds)):
        leds[led] = apa102.LedOutput(args.brightness,
                                     args.r,
                                     args.g,
                                     args.b)
    leds.commit()
    leds.close()
