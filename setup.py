"""
setup.py

Setup file for apa102_gpiod

See LICENSE.txt for more details.

Test examples adapted from PyTest website, under the MIT license.
"""
from setuptools import setup
from setuptools.command.test import test as TestCommand


def readme():
    with open('README.md') as f:
        return f.read()


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ''

    def run_tests(self):
        import shlex
        import pytest
        errno = pytest.main(shlex.split(self.pytest_args))
        exit(errno)


setup(name='apa102_gpiod',
      version='0.1.1',
      description='apa102 driver using userspace gpio character device through '
                  'libgpiod',
      long_description=readme(),
      long_description_content_type='text/markdown',
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.6',
          'Topic :: Software Development :: Libraries',
      ],
      tests_require=['pytest'],
      cmdclass={'test': PyTest},
      url='http://github.com/shenghaoyang/apa102_gpiod',
      author='Shenghao Yang',
      author_email='me@shenghaoyang.info',
      license='MIT',
      packages=['apa102_gpiod'],
      python_requires='>=3.6, <4',
      zip_safe=False)
