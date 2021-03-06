from rstem.led_matrix import FrameBuffer
from rstem.mcpi import minecraft, control
import time

control.show()

mc = minecraft.Minecraft.create()

SCALE = 25
fb = FrameBuffer()

count = 0
FLASH_COUNT = 3
flash_lit = True
while True:
	pos = mc.player.getTilePos()

	x = round(pos.x/SCALE + (fb.width-1)/2)
	x_out_of_bounds = not 0 <= x < fb.width
	x = min(fb.width-1, max(0, x))

	z = round(pos.z/SCALE + (fb.height-1)/2)
	z_out_of_bounds = not 0 <= z < fb.height
	z = min(fb.height-1, max(0, z))

	fb.erase()
	count += 1
	if count > FLASH_COUNT:
		flash_lit = not flash_lit
		count = 0
	if not x_out_of_bounds and not z_out_of_bounds or flash_lit:
		fb.point(z, x)
	fb.show()

	time.sleep(0.01)
