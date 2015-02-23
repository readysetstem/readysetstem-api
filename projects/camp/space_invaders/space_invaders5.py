from rstem import Accel
from rstem.gpio import Button
from rstem.led_matrix import FrameBuffer
import time

fire_button = Button(1)

fb = FrameBuffer()
accel = Accel()

spaceship_position = fb.width / 2

alien_columns = [0, 1, 2, 3]
alien_row = fb.height

missile_x = None
MISSILE_COLOR = 8
MISSILE_STEP_TIME = 0.05

TILT_FORCE = 0.3

while True:
    # ########################################
    # Get inputs
    # ########################################
    presses = fire_button.presses()
    x_force, y_force, z_force = accel.forces()
    now = time.time()

    # ########################################
    # Change the World
    # ########################################

    if missile_x and now - missile_start_time > MISSILE_STEP_TIME
        # Missile already launched - move it up
        missile_y += 1
        missile_start_time = now
    elif presses:
        # Button was pressed - launch missile
        missile_x, missile_y = (spaceship_position, 1)
        missile_start_time = now

    # Move spaceship
    if x_force < -TILT_FORCE:
        spaceship_position -= SPACESHIP_STEP
    elif x_force > TILT_FORCE:
        spaceship_position += SPACESHIP_STEP
    spaceship_position = max(0, min(fb.width - 1, spaceship_position)

    # Move alien
    if now - alien_start_time > ALIENS_STEP_TIME
        alien_columns = [(column + 1) % fb.width for column in alien_columns]
        alien_start_time = now

    # ########################################
    # Show world
    # ########################################

    fb.erase()

    # Draw missile
    if missile_x:
        fb.point(missile_x, missile_y, MISSILE_COLOR)

    # Draw spaceship
    fb.point(round(spaceship_position), 0)

    # Draw aliens
    for column in alien_columns:
        fb.point(column, alien_row)

    # Show FrameBuffer on LED Matrix
    fb.show()
    time.sleep(0.001)
