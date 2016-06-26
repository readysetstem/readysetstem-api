from rstem.led_matrix import FrameBuffer
from rstem.mcpi import minecraft, control
import time

control.show()

mc = minecraft.Minecraft.create()

SCALE = 25
fb = FrameBuffer()

while True:
	pos = mc.player.getTilePos()

	x = round(pos.x/SCALE + (fb.width-1)/2)
	x = min(fb.width-1, max(0, x))

	z = round(pos.z/SCALE + (fb.height-1)/2)
	z = min(fb.height-1, max(0, z))

	fb.erase()
	fb.point(z, x)
	fb.show()

	time.sleep(0.01)
