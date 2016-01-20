from rstem.accel import Accel
from rstem.button import Button
from rstem.mcpi import minecraft, control
from rstem.led_matrix import FrameBuffer
import time

control.show()
mc = minecraft.Minecraft.create()

keymap = {
    Button(18) : control.left,
    Button(14) : control.right,
    Button(15) : control.forward,
    Button(23) : control.backward,
    Button(7)  : control.smash,
    Button(24) : control.jump,
    }

accel = Accel()

fb = FrameBuffer()
flash_count = 0
FLASH_COUNT = 3
table = 0
TABLE_THRESH = 10
EPSILON = 0.03
flash_lit = True
while True:
    pos = mc.player.getTilePos()
    flashing = False
    x = round(pos.x/10 + 3.5)
    if not 0 <= x <= 7:
        flashing = True
    x = min(7, max(0, x))
    z = round(pos.z/10 + 3.5)
    if not 0 <= z <= 7:
        flashing = True
    z = min(7, max(0, z))

    fb.erase()
    flash_count += 1
    if flash_count > FLASH_COUNT:
        flash_lit = not flash_lit
        flash_count = 0
    if not flashing or flashing and flash_lit:
        fb.point(z, x)
    fb.show()

    for button, action in keymap.items():
        action(release=(not button.is_pressed()))

    x, y, z = accel.forces()
    prev_table = table
    table += -1 if abs(x) < EPSILON and abs(y) < EPSILON else +1
    table = max(0, min(100, table))
    if prev_table >= TABLE_THRESH and table < TABLE_THRESH:
        pos = mc.player.getTilePos()
        mc.player.setTilePos(0, 100, 0)

    y -= 0.3
    control.look(up=150*y*abs(y), left=150*x*abs(x))
    
    time.sleep(0.01)
