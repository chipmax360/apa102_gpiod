"""
apa102_gpiod/apa102.py

Contains the definition of the APA102 led driver class, used to drive
APA102 LEDs using libgpiod.

See LICENSE.txt for details.
"""
import gpiod
import typing

import collections
from collections.abc import Sequence

LedOutput = collections.namedtuple('LedOutput', ('brt', 'r', 'g', 'b'))

APA102_START = b'\x00\x00\x00\x00'  # APA102 start sequence, 4 bytes of zeroes


def _check_ledoutput_range(o: LedOutput) -> None:
    """
    Check the values in a LedOutput named tuple for validity.

    :param o: LedOutput named tuple.
    :raises ValueError: on out-of-range values in namedtuple.
    """
    if not ((0 <= o.brt <= 0x1f) and isinstance(o.brt, int)):
        raise ValueError(f'{o.__class__.__name__}: brightness setting invalid '
                         f'got {o.brt!r}, expected integer within [0, 0x1f]')
    if not ((0 <= o.r <= 0xff) and isinstance(o.r, int)):
        raise ValueError(f'{o.__class__.__name__}: red setting invalid: '
                         f'got {o.r!r}, expected integer within [0, 0xff]')
    if not ((0 <= o.g <= 0xff) and isinstance(o.g, int)):
        raise ValueError(f'{o.__class__.__name__}: green setting invalid: '
                         f'got {o.r!r}, expected integer within [0, 0xff]')
    if not ((0 <= o.b <= 0xff) and isinstance(o.b, int)):
        raise ValueError(f'{o.__class__.__name__}: blue setting invalid: '
                         f'got {o.r!r}, expected integer within [0, 0xff]')


def _generate_end_sequence(leds: int) -> bytes:
    """
    Generate a byte sequence, that, when sent to the APA102 leds, ends a
    led update message.

    :param leds: number of chained LEDs.
    :return: terminating byte sequence.
    """
    edges_required = ((leds - 1) if leds else 0)
    bytes_required = 0
    output = bytearray()

    # Each byte provides 16 clock edges, each LED except the first requires
    # one clock edge to latch in the newly sent data.

    if edges_required:
        bytes_required = (((edges_required // 16) + 1) if (edges_required % 16)
                          else edges_required // 16)
    for i in range(bytes_required):
        output.append(0x00)

    return bytes(output)


def _pack_brgb_direct(seq: typing.MutableSequence[int],
                      brt: int, r: int, g: int, b: int) -> None:
    """
    Pack the brt, r, g, b, values to be sent to a LED into a pre-existing
    sequence of integer values representing individual bytes, to be sent to the
    LEDs.

    Packing is done from the start of the sequence.

    :param seq: sequence of integer values
    :param brt: brightness desired for the LED.
    :param r: desired red channel output for the LED.
    :param g: desired green channel output for the LED.
    :param b: desired blue channel output for the LED.
    """
    seq[0] = (brt | 0xe0)
    seq[1] = b
    seq[2] = g
    seq[3] = r


def _pack_brgb(o: LedOutput) -> bytes:
    """
    Pack the brt, r, g, b values to be sent to a LED into a new
    bytes object to be sent to the LED.

    :param o: output desired from the LED.
    :return: bytes object to be sent to the LED.
    """
    arr = bytearray(4)
    _pack_brgb_direct(arr, *o)
    return arr


def _ledoutput_from_led_command(command: typing.Sequence[int]) -> LedOutput:
    """
    Convert a 4-byte LED output command sequence to a LedOutput object.

    :param command: 4-byte LED output command sequence
    :return: LedOutput object representing the command sequence
    """
    return LedOutput(command[0] & 0x1f, command[3], command[2], command[1])


class APA102(Sequence):
    """
    Class used to control APA102 leds using libgpiod.
    """

    def __init__(self, chip: str, leds: int, clk: int, data: int, reset=False):
        """
        Initialize a APA102 led controller.

        :param chip: path to the gpiochip device used to control
                     the signalling lines of the LEDs.
        :param leds: number of LEDs.
        :param clk: clock gpio line.
        :param data: data gpio line.
        :param reset: whether to reset LEDs to the off state on startup.
        :raises OSError: on inability to acquire control of I/O lines.
        """
        self._leds = leds

        self._chip = gpiod.Chip(chip, gpiod.Chip.OPEN_BY_PATH)
        self._lines = self._chip.get_lines((clk, data))
        self._lines.request(f'apa102_gpiod',
                            gpiod.LINE_REQ_DIR_OUT, 0, (0, 0))

        self._data = bytearray(APA102_START)
        self._data.extend(_pack_brgb(LedOutput(0, 0, 0, 0)) * len(self))
        self._data.extend(_generate_end_sequence(self._leds))
        self._view = memoryview(self._data)
        self._wrgb_buffer = bytearray(4)

        if reset:
            self.commit()

    def __getitem__(self, i: int) -> LedOutput:
        """
        Obtain the LedOutput named tuple representing the output of an LED at
        a specific index.

        :param i: index of the LED. ``0`` represents the first LED in the chain,
                  the LED that receives data directly from the control lines.
        :return: LedOutput named tuple representing the output of the LED
        :raises IndexError: on attempt to access an LED at an invalid index.
        """
        if not (0 <= i < self._leds):
            raise IndexError(f'{self.__class__.__name__}: '
                             'out-of-range LED index')
        return _ledoutput_from_led_command(self._view[4 + (i * 4):8 + (i * 4)])

    def __setitem__(self, i: int, o: LedOutput):
        """
        Set the output of an LED.

        :param i: index of the LED. ``0`` represents the first LED in the chain,
                  the LED that receives data directly from the control lines.
        :param o: LedOutput named tuple representing the desired.
                  output of the LED.
        :raises IndexError: on attempt to access an LED at an invalid index.
        :raises ValueError: on invalid values in LedOutput.
        """
        _check_ledoutput_range(o)
        if not (0 <= i < self._leds):
            raise IndexError(f'{self.__class__.__name__}: '
                             'out-of-range LED index')
        self.set_brgb_unchecked(i, *o)

    def __len__(self) -> int:
        """
        Obtain the number of LEDs controlled by this APA102 object.

        :return: number of LEDs controlled.
        """
        return self._leds

    def __contains__(self, o: LedOutput) -> bool:
        """
        Obtain whether any LED in the chain controlled has a specific
        output setting.

        :param o: output setting to test for.
        :return: test result.
        """
        for i in range(len(self)):
            if _pack_brgb(o) == self._view[4 + (i * 4):8 + (i * 4)]:
                return True
        else:
            return False

    def commit(self) -> None:
        """
        Commits the output states to the actual LEDs

        :raises OSError: on commit failure

        .. note::

            Undefined once the object has been ``close()``'d
        """
        set_values = self._lines.set_values
        data = self._data
        for i in range(len(data)):
            byte = data[i]
            bit = ((byte >> 7) & 0x01)
            set_values((0, bit))
            set_values((1, bit))
            bit = ((byte >> 6) & 0x01)
            set_values((0, bit))
            set_values((1, bit))
            bit = ((byte >> 5) & 0x01)
            set_values((0, bit))
            set_values((1, bit))
            bit = ((byte >> 4) & 0x01)
            set_values((0, bit))
            set_values((1, bit))
            bit = ((byte >> 3) & 0x01)
            set_values((0, bit))
            set_values((1, bit))
            bit = ((byte >> 2) & 0x01)
            set_values((0, bit))
            set_values((1, bit))
            bit = ((byte >> 1) & 0x01)
            set_values((0, bit))
            set_values((1, bit))
            bit = ((byte >> 0) & 0x01)
            set_values((0, bit))
            set_values((1, bit))

    def close(self) -> None:
        """
        Closes the APA102 object and relinquish control of the I/O lines.
        """
        self._view.release()
        self._lines.release()
        self._chip.close()

    def set_brgb_unchecked(self,
                           i: int, brt: int, r: int, g: int, b: int) -> None:
        """
        Directly set the BRGB values for a particular LED, without any bounds
        checking on the LED index.

        Provided to avoid the overhead of bounds checking and the creation of
        new objects when using ``__setitem__()`` to alter the output of an
        LED.

        Please use only when arguments are coming from a trusted source.

        :param i: index of the LED to set the WRGB valeus for.
        :param brt: desired brightness of the LED.
        :param r: desired LED red channel intensity.
        :param g: desired LED green channel intensity.
        :param b: desired LED blue channel intensity.
        """
        _pack_brgb_direct(self._view[4 + (i * 4):8 + (i * 4)],
                          brt, r, g, b)
