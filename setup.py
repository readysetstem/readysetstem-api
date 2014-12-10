#!/usr/bin/env python3
#
# Copyright (c) 2014, Scott Silver Labs, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import sys
from setuptools import setup, find_packages, Extension
from setuptools.command.install import install as _install
import subprocess

def shell(cmd):
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout.decode().strip()

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def _post_install(dir):
    from subprocess import call
    if os.system("grep 'BCM2708' /proc/cpuinfo > /dev/null") == 0:
        call("bash ./pkg/postinstall", shell=True)
    else:
        print("WARNING: GPIO, I2C, and SPI are unsupported on this non-RaspberryPi!")

# Post installation task to setup raspberry pi
class install(_install):
    def run(self):
        _install.run(self)
        self.execute(_post_install, (self.install_lib,), msg="Running post install task...")

# C extension wrappers
led_driver =  Extension('rstem.led_matrix.led_driver', sources = ['rstem/led_matrix/led_driver.c'])
accel = Extension('rstem.accel', sources = ['rstem/accel.c'])

setup(
    name = read('NAME').strip(),
    version = read('VERSION').strip(),
    author = "Brian Silverman",
    author_email = "bri@raspberrystem.com",
    description = ("RaspberrySTEM Test"),
    license = "BSD",
    keywords = ["raspberrypi", "stem"],
    url = "https://raspberrystem.com",
    packages = find_packages(),
    include_package_data = True,
    long_description = read('README.md'),
    # use https://pypi.python.org/pypi?%3Aaction=list_classifiers as help when editing this
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Education",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
    ],
    cmdclass={'install': install},  # overload install command
    ext_modules = [led_driver, accel]  # c extensions defined above

)
