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
if tap_ticks:
    tap_ticks[0] = 0

# Beep to tell user we've stopped recording
beep.play(0.2).wait()

# Print actual taps
chars_per_tick = TOTAL_TICKS/80
print("Actual Knock:", tap_ticks)
if len(tap_ticks) == 0:
    print("No taps!")
elif len(tap_ticks) == 1:
    print("Just one taps!")
else:
    for tap_tick in tap_ticks:
        spaces = int(80*tap_tick/TOTAL_TICKS)
        print(" " *  spaces + "*", end="")
    print()

# Print the expected taps of the "secret knock"
secret_knock = [0, 200, 100, 100, 200, 400, 200]
print("Secret Knock:", secret_knock)

# Compare actual taps to secret knock taps
if len(tap_ticks) == len(secret_knock):
    knock_passed = True
    for i in range(len(tap_ticks)):
        if abs(tap_ticks[i] - secret_knock[i]) > secret_knock[i] * 0.5:
            knock_passed = False
else:
    knock_passed = False

if knock_passed:
    print("Access granted!")
else:
    print("Access DENIED!")

        

