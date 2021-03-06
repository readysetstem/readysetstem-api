from rstem.button import Button
from rstem.mcpi import minecraft, control, block
from rstem.mcpi.vec3 import Vec3
from itertools import cycle
import time

control.show(hide_at_exit=True)
mc = minecraft.Minecraft.create()

left = Button(23)
right = Button(14)
up = Button(18)
down = Button(15)
place = Button(24)
select = Button(7)

block_types = [
    block.STONE,
    block.BRICK_BLOCK,
    block.OBSIDIAN,
    block.DIAMOND_BLOCK,
    ]
block_types = cycle(block_types)
blk = next(block_types)

cursor = mc.player.getTilePos()
cursor.y = mc.getHeight(cursor.x, cursor.z)

BLINK_TIME = 0.3
start = time.time()
cursor_on = True
while True:
    if select.presses():
        blk = next(block_types)

    if place.presses():
        mc.setBlock(cursor, blk)
        cursor.y += 1

    old_cursor = cursor.clone()
    cursor += Vec3(0, 0, right.presses())
    cursor += Vec3(0, 0, -left.presses())
    cursor += Vec3(up.presses(), 0, 0)
    cursor += Vec3(-down.presses(), 0, 0)
    if old_cursor != cursor:
        mc.setBlock(old_cursor, block.AIR)
        cursor.y = mc.getHeight(cursor.x, cursor.z)
        start = 0
        cursor_on = True

    if time.time() - start > BLINK_TIME:
        mc.setBlock(cursor, block.STONE if cursor_on else block.AIR)
        start = time.time()
        cursor_on = not cursor_on

    time.sleep(0.01)
