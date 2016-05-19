from rstem.accel import Accel
from rstem.sound import Note
import time

accel = Accel()

# Calibrate
z_rest = 0
SAMPLES = 100
for i in range(SAMPLES):
    x, y, z = accel.forces()
    z_rest += z
    time.sleep(1/SAMPLES)
z_rest /= SAMPLES

# Beep to tell user we're starting recording
beep = Note('A6')
beep.play(0.2).wait()

# Record taps
TOTAL_TICKS = 2000
tap_period = 0
tick = 0
tap_ticks = []
for i in range(TOTAL_TICKS):
    x, y, z = accel.forces()
    tap = abs(z_rest-z) > 0.1
    if tap_period == 0 and tap:
        tap_period = 50
        taps_in_this_period = 0
        last_tick = tick
        tick = 0
    elif tap_period > 0:
        if tap:
            taps_in_this_period += 1
        tap_period -= 1
        if tap_period == 0 and taps_in_this_period > 5:
            tap_ticks.append(last_tick)
    tick += 1
        
    time.sleep(0.001)

# Beep to tell user we've stopped recording
beep.play(0.2).wait()

print(tap_ticks)
