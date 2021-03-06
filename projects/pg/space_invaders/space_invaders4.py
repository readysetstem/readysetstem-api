from rstem.accel import Accel
from rstem.led_matrix import FrameBuffer
import time

fb = FrameBuffer()
accel = Accel()

spaceship_position = fb.width / 2

alien_columns = [0, 1, 2, 3]
alien_row = fb.height - 1

TILT_FORCE = 0.1
SPACESHIP_STEP = 0.1

while True:
    # ########################################
    # Get inputs
    # ########################################
    x_force, y_force, z_force = accel.forces()

    # ########################################
    # Change the World
    # ########################################

    # Move spaceship
    if x_force > TILT_FORCE:
        spaceship_position -= SPACESHIP_STEP
    elif x_force < -TILT_FORCE:
        spaceship_position += SPACESHIP_STEP
    spaceship_position = max(0, min(fb.width - 1, spaceship_position))

    # ########################################
    # Show world
    # ########################################

    fb.erase()

    # Draw spaceship
    fb.point(round(spaceship_position), 0)

    # Draw aliens
    for column in alien_columns:
        fb.point(column, alien_row)

    # Show FrameBuffer on LED Matrix
    fb.show()
    time.sleep(0.001)
