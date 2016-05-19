from rstem.accel import Accel
from rstem.sound import Speech
import time

ready_tts = Speech("Ready to play?")

tilt_left_tts = Speech("Tilt left!")
no_action_tts = Speech("No action!")

detect_tts = Speech("I detected:")
wrong_tts = Speech("Oops!")
correct_tts = Speech("Correct!")
try_again_tts = Speech("Try again another time!")

accel = Accel()

NOACTION = 0
LEFT = 1

actions_tts = [no_action_tts, tilt_left_tts]

# Ready to play?
SCORE_NEEDED = 10
period = 300
ready_tts.play().wait()
while True:
    request = LEFT
    actions_tts[request].play().wait()
    tilt_left_score = 0
    action = NOACTION
    for i in range(period):
        x, y, z = accel.forces()
        if x > 0.75:
            tilt_left_score += 1

        if tilt_left_score > SCORE_NEEDED:
            action = LEFT
            break

        time.sleep(0.01)

    if request == action:
        # Yes!
        correct_tts.play().wait()
    else:
        # No - let user know what we detected
        wrong_tts.play().wait()
        detect_tts.play().wait()
        actions_tts[action].play().wait()
        break

    time.sleep(0.5)

try_again_tts.play().wait()
