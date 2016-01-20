from rstem.accel import Accel
from rstem.button import Button
from rstem.mcpi import control
import time

control.show()

keymap = {
    Button(18) : control.left,
    Button(14) : control.right,
    Button(15) : control.forward,
    Button(23) : control.backward,
    Button(7)  : control.smash,
    Button(24) : control.jump,
    }

accel = Accel()

while True:
    for button, action in keymap.items():
        action(release=(not button.is_pressed()))

    x, y, z = accel.forces()
    y -= 0.3
    control.look(up=150*y*abs(y), left=150*x*abs(x))
    
    time.sleep(0.01)
