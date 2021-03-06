from rstem.button import Button
from rstem.mcpi import minecraft, control, block
import time

control.show(hide_at_exit=True)
mc = minecraft.Minecraft.create()
button = Button(7)

def dig(mc, pos):
    mc.setBlock(hit.pos, block.AIR)

while True:
    if button.presses():
        control.hit()

    hits = mc.events.pollBlockHits()
    for hit in hits:
        dig(mc, hit)

    time.sleep(0.01)

