"""
examples/spectrum.py

Commands the LEDs to output colors of increaasing hue, starting from a hue of
zero.

See LICENSE.txt for more details.
"""
import argparse
import colorsys
import sys

sys.path.append('..')  # Not required if running with apa102_gpiod installed
import apa102_gpiod.apa102 as apa102

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Output colors of increasing'
                                                 ' hue on the LEDs')
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
                        type=int, choices=range(32), help='led brightness'
                                                          ' setting')
    args = parser.parse_args()

    leds = apa102.APA102(args.chip, args.leds, args.clk, args.data,
                         True)
    for led in range(len(leds)):
        rgb = colorsys.hsv_to_rgb(led / len(leds), 1, 1)
        leds[led] = apa102.LedOutput(args.brightness,
                                     round(rgb[0] * 255),
                                     round(rgb[1] * 255),
                                     round(rgb[2] * 255))
    leds.commit()
    leds.close()
