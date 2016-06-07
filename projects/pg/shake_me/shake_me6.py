from rstem.accel import Accel
import time

accel = Accel()

NOACTION = 0
LEFT = 1
RIGHT = 2
UP = 3
SHAKE = 4

# Ready to play?
SCORE_NEEDED = 10
period = 300
while True:
    request = LEFT
    action = NOACTION
    print(request)

    tilt_left_score = 0
    for i in range(period):
        x, y, z = accel.forces()
        if x > 0.75:
            tilt_left_score += 1

        if tilt_left_score > SCORE_NEEDED:
            action = LEFT
            break

        time.sleep(0.01)

    if request == action:
        print("CORRECT!")
    else:
        print("OOPS!")
        break

    time.sleep(0.5)
