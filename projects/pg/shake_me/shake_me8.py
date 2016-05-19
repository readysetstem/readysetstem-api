from rstem.accel import Accel
from rstem.sound import Speech
import random
import time

ready_tts = Speech("Ready to play?")

tilt_left_tts = Speech("Tilt left!")
tilt_right_tts = Speech("Tilt right!")
tilt_up_tts = Speech("Tilt up!")
shake_me_tts = Speech("Shake me!")
no_action_tts = Speech("No action!")

detect_tts = Speech("I detected:")
wrong_tts = Speech("Oops!")
correct_tts = Speech("Correct!")
try_again_tts = Speech("Try again another time!")

accel = Accel()

NOACTION = 0
LEFT = 1
RIGHT = 2
UP = 3
SHAKE = 4

actions_tts = [no_action_tts, tilt_left_tts, tilt_right_tts, tilt_up_tts, shake_me_tts]

# Ready to play?
SCORE_NEEDED = 10
period = 300
ready_tts.play().wait()
while True:
    request = random.randint(1,4)
    actions_tts[request].play().wait()
    tilt_left_score = 0
    tilt_right_score = 0
    tilt_up_score = 0
    shake_me_score = 0
    action = NOACTION
    for i in range(period):
        x, y, z = accel.forces()
        if x < -0.75:
            tilt_right_score += 1
        if x > 0.75:
            tilt_left_score += 1
        if y > 0.75:
            tilt_up_score += 1
        if (z < 0.7 or z > 1.3) and (-0.5 < x < 0.5) and (-0.5 < y < 0.5):
            shake_me_score += 1

        if tilt_left_score > SCORE_NEEDED:
            action = LEFT
            break
        elif tilt_right_score > SCORE_NEEDED:
            action = RIGHT
            break
        elif tilt_up_score > SCORE_NEEDED:
            action = UP
            break
        elif shake_me_score > SCORE_NEEDED:
            action = SHAKE
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

    period = int(period * 0.95)
    time.sleep(0.5)

try_again_tts.play().wait()
