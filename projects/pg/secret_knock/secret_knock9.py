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

# Print actual taps
chars_per_tick = TOTAL_TICKS/80
print("Actual Knock:", relative_tap_ticks)
if len(relative_tap_ticks) == 0:
    print("No taps!")
elif len(relative_tap_ticks) == 1:
    print("Just one tap!")
else:
    for tap_tick in relative_tap_ticks:
        spaces = int(80*tap_tick/TOTAL_TICKS)
        print(" " *  spaces + "*", end="")
    print()

# Print the expected taps of the "secret knock"
secret_knock = [0, 200, 100, 100, 200, 400, 200]
print("Secret Knock:", secret_knock)

# Compare actual taps to secret knock taps
knock_passed = False
if len(relative_tap_ticks) == len(secret_knock):
    knock_passed = True
    for i in range(len(relative_tap_ticks)):
        if abs(relative_tap_ticks[i] - secret_knock[i]) > secret_knock[i] * 0.5:
            knock_passed = False

if knock_passed:
    print("Access granted!")
else:
    print("Access DENIED!")
