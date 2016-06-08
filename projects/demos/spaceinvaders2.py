# ###############################################################
#
# ALIEN INTRUDERS GAME
#
# ###############################################################

# ################################
# Initialize the game environment
# ################################

# Import required functions/modules
from rstem.accel import Accel
from rstem.button import Button
from rstem.led_matrix import FrameBuffer, Sprite
from rstem.sound import Sound, Note
from itertools import cycle
import time

# Initialize framebuffer
fb = FrameBuffer(matrix_layout=[
        (0,0,0),(8,0,0),(16,0,0),(24,0,0),(32,0,0),
        (32,8,180),(24,8,180),(16,8,180),(8,8,180),(0,8,180),
        (0,16,0),(8,16,0),(16,16,0),(24,16,0),(32,16,0),
        (32,24,180),(24,24,180),(16,24,180),(8,24,180),(0,24,180),
        (0,32,0),(8,32,0),(16,32,0),(24,32,0),(32,32,0),
        ])

# Initialize accelerometer
accel = Accel()

# Initialize spaceship
spaceship = Sprite('''
    --F--
    FFAFF
    FAAAF
    ''')
spaceship_middle = 2
spaceship_position = fb.width / 2
TILT_FORCE = 0.1
SPACESHIP_STEP = 1

# Initialize aliens
alien_columns = [i for i in range(24) if i % 3]
alien_row = fb.height - 1
alien_start_time = time.time()
alien_direction = 1
alien_speed = 1
ALIENS_STEP_TIME = .8

# Initialize missiles
fire_button = Button(7)
missiles = []
MISSILE_COLOR = 10
MISSILE_STEP_TIME = 0.05         
missile_start_time = 0

# Initialize sounds          
fire_sound = Sound("fire.wav")
hit_sound = Sound("hit.wav")
notes = cycle([Note('B3'), Note('G3'), Note('E3'), Note('C3')])

times = []
while True:
    # ########################################
    # Get inputs
    # ########################################
    presses = fire_button.presses()
    x_force, y_force, z_force = accel.forces()
    now = time.time()
    """
    times.append(now)
    if len(times) > 100:
        print(sum(a-b for a,b in zip(times[1:],times[:-1]))/(len(times)-1))
        times = []
    """

    # ########################################
    # Change the World
    # ########################################

    if now - missile_start_time > MISSILE_STEP_TIME:
        new_missiles = []
        for missile_x, missile_y in missiles:
            missile_y += 1
            if missile_y < fb.height:
                new_missiles.append((missile_x, missile_y))
        missiles = new_missiles
        missile_start_time = now
    # Button was pressed - launch missile
    if presses and len(missiles) < 5:
        missiles.append((round(spaceship_position), 3))
        fire_sound.play()

    # Move spaceship
    if x_force > TILT_FORCE:
        spaceship_position -= SPACESHIP_STEP * x_force
    elif x_force < -TILT_FORCE:
        spaceship_position -= SPACESHIP_STEP * x_force
    spaceship_position = max(0, min(fb.width - 1, spaceship_position))

    # Move alien
    if now - alien_start_time > ALIENS_STEP_TIME / alien_speed:
        next(notes).play(duration=0.20)
        alien_at_right_side = alien_direction > 0 and max(alien_columns) == fb.width - 1
        alien_at_left_side = alien_direction < 0 and min(alien_columns) == 0
        if alien_at_left_side or alien_at_right_side:
            alien_row -= 1
            alien_speed *= 1.2
            alien_direction = - alien_direction
            if alien_row == 0:
                break
        else:
            alien_columns = [column + alien_direction for column in alien_columns]
        alien_start_time = now

    # Check for collision
    new_missiles = []
    for missile_x, missile_y in missiles:
        if missile_y == alien_row and missile_x in alien_columns:
            alien_columns.remove(missile_x)
            hit_sound.play()
        else:
            new_missiles.append((missile_x, missile_y))
    missiles = new_missiles

    if not alien_columns:
        break

    # ########################################
    # Show world
    # ########################################

    fb.erase()

    # Draw missile
    for missile_x, missile_y in missiles:
        if missile_x >= 0:
            fb.point(missile_x, missile_y, MISSILE_COLOR)

    # Draw spaceship
    spaceship_x = round(spaceship_position) - spaceship_middle
    fb.draw(spaceship, origin=(spaceship_x, 0))

    # Draw aliens
    for column in alien_columns:
        fb.point(column, alien_row)

    # Show FrameBuffer on LED Matrix
    fb.show()
    time.sleep(0.001)

if alien_columns:
    print("Ouch!")
else:
    print("You win!")
