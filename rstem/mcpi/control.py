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
This module provides functions to control the Minecraft player, by simulating
keystrokes and mouse movements.  In addition, it provides helper functions for
show()ing/hide()ing the Minecraft application.
'''

import os
import time
from subprocess import call, Popen, PIPE
from functools import partial
import uinput
from threading import Timer
from .vec3 import Vec3
from . import block
from math import atan2, degrees, sqrt, floor
import atexit
import signal

shcall = partial(call, shell=True)
shopen = partial(Popen, stdin=PIPE, stderr=PIPE, stdout=PIPE, close_fds=True, shell=True)

MINECRAFT_WIN_NAME = 'Minecraft - Pi edition'
WMCTRL_CMD = 'XAUTHORITY=/home/pi/.Xauthority DISPLAY=:0 wmctrl'
HIDE_WIN_CMD = WMCTRL_CMD + " -r '{:s}' -b add,hidden".format(MINECRAFT_WIN_NAME)
SHOW_WIN_CMD = WMCTRL_CMD + " -a '{:s}'".format(MINECRAFT_WIN_NAME)

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

MIN_DURATION_PRESS = 0.1

def show(show=True, hide_at_exit=True):
    '''Shows (opens and brings to the front) the Minecraft application window.

    Requires that Minecraft is running.

    If `hide_at_exit` is `True`, then when the Python application exits, the
    Minecraft application will be minimized (via `hide()`).
    '''
    ret = shcall(SHOW_WIN_CMD if show else HIDE_WIN_CMD)
    if ret:
        raise IOError('Could not show/hide minecraft window.  Is it running?')

    if hide_at_exit:
        def hide_ignoring_errors():
            try:
                hide()
            except:
                pass
        def hide_and_exit():
            hide_ignoring_errors()
            sys.exit()
        signal.signal(signal.SIGTERM, hide_and_exit)
        atexit.register(hide_ignoring_errors)

def hide():
    '''Hides (minimizes) the Minecraft application.

    Requires that Minecraft is running.
    '''
    show(show=False)

def key_release(key):
    '''Simulate a key release in the Minecraft window.

    See also `key_press()`.
    '''
    key_press(key, release=True)

def key_press(key, duration=None, release=False, wait=True):
    '''Simulate a keyboard key press in the Minecraft window.

    `key` is the keycode of the key to be pressed (keycode values are from the
    uinput module, e.g. `uinput.KEY_A`)

    If `release` is True, then this simulates a key being released instead of
    pressed.

    If `duration` is None, then the key is pressed and the function returns.
    Otherwise, if a `duration` (in seconds) is given, the key is pressed and
    will automatically be released after `duration` seconds in one of two
    ways:

     1. If `wait` is `True`, the function will not return until the `duration`
     has elapsed.
     1. If `wait` is `False`, the function will return immediately, and the key
     will be released after `duration` seconds via a timer.
    '''
    if release:
        device.emit(key, 0)
    else:
        if not duration:
            device.emit(key, 1)
        else:
            if wait:
                device.emit(key, 1)
                time.sleep(duration)
                device.emit(key, 0)
            else:
                device.emit(key, 1)
                Timer(duration, key_release, args=[key]).start()

def backward(duration=None, release=False, wait=True):
    '''Move Steve backward.  Simulates a `key_press()` of `S`.'''
    key_press(uinput.KEY_S, duration, release, wait)

def forward(duration=None, release=False, wait=True):
    '''Move Steve forward.  Simulates a `key_press()` of `W`.'''
    key_press(uinput.KEY_W, duration, release, wait)

def left(duration=None, release=False, wait=True):
    '''Move Steve left.  Simulates a `key_press()` of `A`.'''
    key_press(uinput.KEY_A, duration, release, wait)

def right(duration=None, release=False, wait=True):
    '''Move Steve right.  Simulates a `key_press()` of `D`.'''
    key_press(uinput.KEY_D, duration, release, wait)

def jump(duration=None, release=False, wait=True):
    '''Make Steve jump.  Simulates a `key_press()` of the spacebar.'''
    key_press(uinput.KEY_SPACE, duration, release, wait)

def crouch(duration=None, release=False, wait=True):
    '''Make Steve crouch.  Simulates a `key_press()` of the left shift key.'''
    key_press(uinput.KEY_LEFTSHIFT, duration, release, wait)

def ascend(duration=None, release=False, wait=True):
    '''Move Steve upward in fly mode.

    Equivalent to `jump()`, i.e. will only cause Steve to ascend when in fly
    mode.
    '''
    jump(duration, release, wait)

def descend(duration=None, release=False, wait=True):
    '''Move Steve downward in fly mode.

    Equivalent to `crouch()`, i.e. will only cause Steve to descend when in fly
    mode.
    '''
    crouch(duration, release, wait)

def stop():
    '''Stop all of Steve's current movements, i.e. release all keys.'''
    for key in keys:
        key_release(key)

def smash(duration=None, release=False, wait=True):
    '''Make Steve smash a block.  Simulates a `key_press()` of the left mouse button.'''
    key_press(uinput.BTN_LEFT, duration, release, wait)

def place(duration=None, release=False, wait=True):
    '''Make Steve place a block.  Simulates a `key_press()` of the right mouse button.'''
    key_press(uinput.BTN_RIGHT, duration, release, wait)

def hit(*args, **kwargs):
    '''Make Steve hit a block.  Simulates a `key_press()` of the right mouse button.

    Note that Steve must be holding a sword for him to actually 'hit'.  If he's
    holding a block, this function is equivalent to `place()`.
    '''
    place(*args, **kwargs)

def toggle_fly_mode():
    '''Toggle fly mode.  Simulates two `jump()`s.'''
    for i in range(2):
        jump(duration=MIN_DURATION_PRESS)
        time.sleep(MIN_DURATION_PRESS)

def item(choice):
    '''Select an item.  Simulates a `key_press()` of `1` thru `8` (the `choice`).

    `choice` is the number of the item (shown on the bar at the bottom of the
    Minecraft window).
    '''
    if not (1 <= choice <= 8):
        raise ValueError('choice must be from 1 to 8')
    key_press(item_keys[choice-1], duration=MIN_DURATION_PRESS)

def enter():
    '''Simulates a `key_press()` of the ENTER key.

    Can be useful to select an item in the inventory.'''
    key_press(uinput.KEY_ENTER, duration=MIN_DURATION_PRESS)

def inventory():
    '''Open Steve's inventory.  Simulates a `key_press()` of `E`.'''
    key_press(uinput.KEY_E, duration=MIN_DURATION_PRESS)

def look(left=0, right=0, up=0, down=0):
    '''Look around - simulate a mouse movement.

    Looks left/right/up/down the integer amount given.  The integer represents
    the amount of incremental mouse movement.
    '''
    device.emit(uinput.REL_X, int(right-left), syn=False)
    device.emit(uinput.REL_Y, int(down-up))

def _wait_until_stopped(mc):
    prev = None
    cur = mc.player.getPos()
    tries = 40
    while cur != prev and tries > 0:
        prev = cur
        cur = mc.player.getPos()
        time.sleep(0.05)
        tries -= 1
    return cur

def _make_platform(mc, erase=False, height=58, half_width=3):
    mc.setBlocks(
        Vec3(-half_width-1, height+0, -half_width-1),
        Vec3(half_width+1, height+4, half_width+1),
        block.AIR if erase else block.STONE)
    mc.setBlocks(
        Vec3(-half_width, height+1, -half_width),
        Vec3(half_width, height+3, half_width),
        block.AIR if erase else block.COBWEB)

    return Vec3(0, height+1, 0)

def get_heading(mc):
    '''Get the heading (compass direction) that Steve is facing.

    `mc` is the Minecraft object (returned by `minecraft.Minecraft.create()`).

    Returns the angle (in degrees) from the z-axis (i.e., when facing the
    z-axis, the angle is zero).  The angle increases counter-clockwise when the
    ground is viewed from above.  The angle is from -180 to 180 degress.

    The Minecraft application does not provide any way to directly get the
    heading, so this function uses some tricks that have their own quirks.  The
    heading is determined by:

     - Transporting Steve to a platform high above the world.  The platform is
       covered, so when Steve gets there, it'll be dark.
     - Have Steve walk forward a short distance.
     - Use Steve's starting point and end point to determine the heading.

    Some quirks of using the above method:

     - The Minecraft world will go black (it's dark) while running the above
       procedures.
     - If Steve is looking around or moving while getting the heading, the
       computed heading can be way off.
     - The platform is created far above the world, but if there are other
       blocks already there, they will be erased.
    '''
    original_pos = mc.player.getPos()
    center_of_platform = _make_platform(mc)

    #
    # move forward for a brief moment to record direction of motion via
    # start/end positions.  We do this as briefly as possible, which sometimes
    # can fail - so we allow some retries.
    #
    end = center_of_platform
    tries = 3
    while center_of_platform == end and tries:
        mc.player.setPos(center_of_platform)
        forward(0.1)
        end = _wait_until_stopped(mc)
        tries -= 1

    _make_platform(mc, erase=True)
    mc.player.setPos(original_pos)

    angle_to_z = degrees(atan2((end.x - center_of_platform.x),(end.z - center_of_platform.z)))
    return angle_to_z

def _circle(mc, origin, radius, blk):
    for delta_x in range(-int(radius), int(radius)+1):
        z_vector = Vec3(0, 0, floor(sqrt(radius**2 - delta_x**2)))
        v = origin + Vec3(delta_x,0,0)
        mc.setBlocks(v - z_vector, v + z_vector, blk)

def _sphere(mc, origin, radius, blk):
    for delta_y in range(-int(radius), int(radius)+1):
        _circle(mc, origin + Vec3(0,delta_y,0), sqrt(radius**2 - delta_y**2), blk)

def get_direction(mc):
    '''Get the direction (in 3 dimensions) that Steve is facing.

    `mc` is the Minecraft object (returned by `minecraft.Minecraft.create()`).

    Steve must be holding the sword for this function to work correctly.

    Returns the direction, `(theta, phi)`, from a spherical coordinate
    system.  `theta` is the angle from the z-axis (equivalent to the angle
    returned from `get_heading()`, from -180 to 180 degress.  `phi` is the
    angle looking up/down (from -90 to 90 degrees), where -90 is looking
    straight down, 0 is looking level, and 90 is looking straight up.

    The Minecraft application does not provide any way to directly get the
    direction, so this function uses some tricks that have their own quirks.
    The direction is determined by:

     - Transporting Steve to the center of a sphere high above the world.  The
       sphere is completely enclosed, so when Steve gets there, it'll be dark.
     - Have Steve hit one of the blocks of the sphere.
     - Using `pollBlockHits()`, record which block Steve hit.  Using a little
       trigonometry, we can determine the direction he is facing.

    Some quirks of using the above method:

     - It's not nearly as accurate as `get_heading()`.  It's limited because
       Steve can only 'hit' blocks that are close to him.
     - The Minecraft world will go black (it's dark) while running the above
       procedures.
     - If Steve is looking around or moving while getting the direction, the
       computed direction can be way off.
     - The sphere is created far above the world, but if there are other
       blocks already there, they will be erased.
     - Because it uses `pollBlockHits()`, Steve must be holding the sword for
       this function to work correctly.  You'll notice Steve finish swinging
       his sword right after he returns from the darkness.
    '''
    origin = Vec3(0,58,0)
    radius = 3.9
    box_offset = Vec3(radius+1, radius+1, radius+1)
    mc.setBlocks(origin - box_offset, origin + box_offset, block.STONE)
    _sphere(mc, origin, radius, block.AIR)
    mc.setBlocks(origin, origin + Vec3(0, radius, 0), block.AIR)
    mc.setBlock(origin + Vec3(0, -2, 0), block.STONE)

    pos = mc.player.getPos()
    mc.player.setTilePos(origin + Vec3(0, -1, 0))
    tries = 3
    while tries:
        time.sleep(0.1)
        hit(0.2)
        hits = mc.events.pollBlockHits()
        if hits:
            break
        look(left=1)
        tries -= 1
    mc.player.setPos(pos)
    mc.setBlocks(origin - box_offset, origin + box_offset, block.AIR)
    hit_pos = hits[0].pos
    direction = hit_pos - origin
    theta = degrees(atan2(direction.x, direction.z))
    phi = degrees(atan2(direction.y, sqrt(direction.z**2 + direction.x**2)))
    return (theta, phi)

__all__ = [
    'show',
    'hide',
    'key_release',
    'key_press',
    'backward',
    'forward',
    'left',
    'right',
    'jump',
    'crouch',
    'ascend',
    'descend',
    'stop',
    'smash',
    'place',
    'hit',
    'toggle_fly_mode',
    'item',
    'enter',
    'inventory',
    'look',
    'get_heading',
    'get_direction',
    ]
