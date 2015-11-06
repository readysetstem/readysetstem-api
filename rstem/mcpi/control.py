#
# Copyright (c) 2015, Scott Silver Labs, LLC.
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
'''
This module provides function to control a Minecraft Pi player.
'''

import os
import time
from subprocess import call, Popen, PIPE
from functools import partial
import uinput
from threading import Timer

shcall = partial(call, shell=True)
shopen = partial(Popen, stdin=PIPE, stderr=PIPE, stdout=PIPE, close_fds=True, shell=True)

MINECRAFT_WIN_NAME = 'Minecraft - Pi edition'
HIDE_WIN_CMD = "DISPLAY=:0 wmctrl -r '{:s}' -b add,hidden".format(MINECRAFT_WIN_NAME)
SHOW_WIN_CMD = "DISPLAY=:0 wmctrl -a '{:s}'".format(MINECRAFT_WIN_NAME)

keys = [
    uinput.KEY_W,
    uinput.KEY_A,
    uinput.KEY_S,
    uinput.KEY_D,
    uinput.KEY_E,
    uinput.KEY_1,
    uinput.KEY_2,
    uinput.KEY_3,
    uinput.KEY_4,
    uinput.KEY_5,
    uinput.KEY_6,
    uinput.KEY_7,
    uinput.KEY_8,
    uinput.KEY_SPACE,
    uinput.KEY_ENTER,
    uinput.KEY_LEFTSHIFT,
    uinput.BTN_LEFT,
    uinput.BTN_RIGHT,
    uinput.REL_X,
    uinput.REL_Y,
    ]
device = uinput.Device(keys)
time.sleep(0.5)

item_keys = [eval('uinput.KEY_{:d}'.format(item+1)) for item in range(8)]

def show(show=True):
    ret = shcall(SHOW_WIN_CMD if show else HIDE_WIN_CMD)
    if ret:
        raise IOError('Could not show/hide minecraft window.  Is it running?')

def hide():
    show(show=False)

def key_release(key):
    key_press(key, release=True)

def key_press(key, duration=None, release=False, wait=True):
    if release:
        device.emit(key, 0)
    else:
        if duration == None:
            device.emit(key, 1)
        elif duration > 0:
            if wait:
                device.emit(key, 1)
                time.sleep(duration)
                device.emit(key, 0)
            else:
                device.emit(key, 1)
                Timer(duration, key_release, args=[key]).start()
                
        else:
            device.emit_click(key)

def backward(duration=None, release=False, wait=True):
    key_press(uinput.KEY_S, duration, release, wait)

def forward(duration=None, release=False, wait=True):
    key_press(uinput.KEY_W, duration, release, wait)

def left(duration=None, release=False, wait=True):
    key_press(uinput.KEY_A, duration, release, wait)

def right(duration=None, release=False, wait=True):
    key_press(uinput.KEY_D, duration, release, wait)

def jump(duration=None, release=False, wait=True):
    key_press(uinput.KEY_SPACE, duration, release, wait)

def crouch(duration=None, release=False, wait=True):
    key_press(uinput.KEY_LEFTSHIFT, duration, release, wait)

def ascend(duration=None, release=False, wait=True):
    jump(duration, release, wait)

def descend(duration=None, release=False, wait=True):
    crouch(duration, release, wait)

def stop():
    for key in keys:
        key_release(key)
        
def smash(duration=None, release=False, wait=True):
    key_press(uinput.BTN_LEFT, duration, release, wait)

def place(duration=0, release=False, wait=True):
    key_press(uinput.BTN_RIGHT, duration, release, wait)

def toggle_fly_mode():
    for i in range(2):
        jump(duration=0.1)
    time.sleep(0.5)

def item(choice):
    if not (1 <= choice <= 8):
        raise ValueError('choice must be from 1 to 8')
    key_press(item_keys[choice-1], duration=0)

def enter():
    key_press(uinput.KEY_ENTER, duration=0)
    
def inventory():
    key_press(uinput.KEY_E, duration=0)
    
def look(left=0, right=0, up=0, down=0):
    device.emit(uinput.REL_X, right-left, syn=False)
    device.emit(uinput.REL_Y, down-up)
    # throttling to prevent key overruns
    time.sleep(0.05)

__all__ = [
    'show',
    'hide',
    ]