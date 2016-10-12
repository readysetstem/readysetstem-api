from rstem.led_matrix import FrameBuffer, Text
from rstem.gpio import Output
import traceback
import sys
import time

led = Output(14)

while True:
    num_uuts = 0
    on = False
    start = time.time()
    while num_uuts <= 2 or num_uuts >= 12:
        try:
            num_uuts = FrameBuffer.detect()
        except:
            num_uuts = 0

        if on:
            led.on()
        else:
            led.off()

        elapsed = time.time() - start
        if on and elapsed > 0.3 or not on and elapsed > 2:
            on = not on
            start = time.time()

        time.sleep(0.05)

    fb_spec = [(8*x,0,0) for x in range(num_uuts)]
    fb = FrameBuffer(fb_spec)

    digits = [Text(str(i)) for i in range(10)]

    def endcaps():
        fb.erase()
        fb.line((0,0), (7,7))
        fb.line((0,7), (7,0))
        fb.line((fb.width-8,0), (fb.width-1,7))
        fb.line((fb.width-8,7), (fb.width-1,0))

    # Number UUTs
    endcaps()
    for uut in range(1,num_uuts-1):
        fb.draw(digits[uut], (8*uut+1, 0))
    fb.show()
    time.sleep(3)

    # Brightness sequence
    for color in range(16):
        endcaps()
        fb.rect((8,0), (fb.width-16,8), fill=True, color=color)
        fb.show()
        time.sleep(4/16)

    # Horizontal line moving down
    for y in reversed(range(8)):
        endcaps()
        fb.line((8,y),(fb.width-9,y))
        fb.show()
        time.sleep(4/8)

    def hash(color=0xF):
        for x in range(8, fb.width-8, 2):
            for y in range(0,8,2):
                fb.point(x, y, color=color)
                fb.point(x + 1, y + 1, color=color)
        fb.show()

    # Hash 1
    endcaps()
    hash()
    time.sleep(2)

    # Hash 2
    endcaps()
    fb.rect((8,0), (fb.width-16,8), fill=True, color=0xF)
    hash(color=0)
    time.sleep(2)

    led.on()
    fb.erase()
    fb.show()
    try:
        while True:
            FrameBuffer.detect()
            time.sleep(0.1)
    except:
        pass
    led.off()
            
            
