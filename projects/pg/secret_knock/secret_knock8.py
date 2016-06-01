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
    time.sleep(0.01)
z_rest /= SAMPLES

# Beep to tell user we're starting recording
beep = Note('A6')
beep.play(0.2).wait()

# Record taps
TOTAL_TICKS = 2000
raw_tap_ticks = []
for i in range(TOTAL_TICKS):
    x, y, z = accel.forces()
    if abs(z_rest-z) > 0.1:
        raw_tap_ticks.append(i)
    time.sleep(0.001)

# Beep to tell user we've stopped recording
beep.play(0.2).wait()

# Convert raw ticks to absolute ticks
absolute_tap_ticks = []
previous_tick = None
for tick in raw_tap_ticks:
    if previous_tick == None or tick - previous_tick > 20:
        absolute_tap_ticks.append(tick)
    previous_tick = tick

# Convert absolute ticks to relative ticks
relative_tap_ticks = []
previous_tick = absolute_tap_ticks[0]
for tick in absolute_tap_ticks:
    relative_tap_ticks.append(tick - previous_tick)
    previous_tick = tick

print(raw_tap_ticks)
print(absolute_tap_ticks)
print(relative_tap_ticks)
