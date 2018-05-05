apa102_gpiod
------------
A python library for accessing ``APA102`` addressable LEDs using ``libgpiod``,
a library used to access the userspace gpio character device.

Useful for situations where you need to drive LEDs attached to non-SPI capable
I/O lines, or when the in-kernel ``spi-gpio`` driver is not available (example:
Pimoroni Blinkt on the default kernels from mainstream distributions)

The usage of this library is probably frowned upon by virture of
``linux/Documentation/driver-api/gpio/drivers-on-gpio.rst``, so go and pressure
the Raspberry Pi kernel devs to include ``spi-gpio``, so we wouldn't have to
resort to custom out-of-tree kernels or _evil bitbanging in userspace_!

Prerequisites
-------------
- Linux Kernel >= ``4.8``
- ``libgpiod`` >= ``039b301b173c78664775d1ea93493825ef80c9d4``
- Python >= ``3.6``

Installation
------------
- ``libgpiod``
    - ``https://git.kernel.org/pub/scm/libs/libgpiod/libgpiod.git/``
    - Remember to ``--enable-bindings-python`` when configuring.
- ``apa102_gpiod``
    - ``pip install apa102_gpiod``

Tests
-----
- Tests can be found in the ``test`` directory.
    - Only unit tests are present now, more tests welcome.
- Use your favourite test runner to run the tests, or:
    - ``pip install setuptools``
    - ``pip install pytest``
    - ``python setup.py test``


Performance
-----------
Since we're accessing the GPIOs through the character device and not through
some memory-mapped magic, performance is guaranteed to be lower. Here are some
test results:

Device | Software                        | Achieved data rate (``kByte/s``)
-------| --------------------------------| --------------------------------
RPI3 B | Arch Linux ARM Linux 4.14.37    | 13962

Caveats
-------
- No clock rate control is implemented, since the achieved data rates are
  way below the maximum data rates supported by the ``APA102``.
    - File an issue report if needed.

Examples
--------
See the ``examples`` directory.

Licensing
---------
This project is licensed under the *MIT License*.
See ``LICENSE.txt`` for more details.
