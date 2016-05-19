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
TOTAL_TICKS = 200
tap_ticks = []
for i in range(TOTAL_TICKS):
    x, y, z = accel.forces()
    tap = abs(z_rest-z) > 0.1
    tap_ticks.append(tap)
        
    time.sleep(0.01)

# Beep to tell user we've stopped recording
beep.play(0.2).wait()

print(tap_ticks)
