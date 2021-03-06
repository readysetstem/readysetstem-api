from rstem.led_matrix import FrameBuffer, Text
import time

fb = FrameBuffer()
start_text = Text("PUSH TO PLAY! ")
lose_text = Text("YOU LOSE! ")
win_text = Text("YOU WIN! ")

def scroll(text, cancel=None, speed=0.07):
    for i in range(text.width + fb.width):
        fb.erase()
        fb.draw(text, origin=(fb.width-i,0))
        fb.show()
        time.sleep(speed)
        if cancel and cancel():
            return True
    return False

# ###############################################################
#
# SPACE INVADERS GAME
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
fb = FrameBuffer()

# Initialize accelerometer
accel = Accel()

# Initialize spaceship
spaceship = Sprite('''
    -F-
    FAF
    ''')
TILT_FORCE = 0.1
SPACESHIP_STEP = 0.1

# Initialize aliens
ALIENS_STEP_TIME = .8

# Initialize missiles
fire_button = Button(7)
MISSILE_COLOR = 10
MISSILE_STEP_TIME = 0.1     
        
# Initialize sounds     
fire_sound = Sound("fire.wav")
hit_sound = Sound("hit.wav")
notes = [Note('B5'), Note('G5'), Note('E5'), Note('C5')]
notes_cycle = cycle(notes)
while True:
    fire_button.presses()
    while True:
        if scroll(start_text, cancel=fire_button.presses):
            break
    
    spaceship_middle = 1
    spaceship_position = fb.width / 2
    alien_columns = [0, 1, 2, 3]
    alien_row = fb.height - 1
    alien_start_time = time.time()
    alien_direction = 1
    alien_speed = 2
    missile_x, missile_y = -1, -1

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
    
        if missile_x >= 0 and now - missile_start_time > MISSILE_STEP_TIME:
            # Missile already launched - move it up
            missile_y += 1
            if missile_y >= fb.height:
                missile_x, missile_y = -1, -1
            missile_start_time = now
        elif presses:
            # Button was pressed - launch missile
            missile_x, missile_y = (round(spaceship_position), 1)
            missile_start_time = now
            fire_sound.play()
    
        # Move spaceship
        if x_force > TILT_FORCE:
            spaceship_position -= SPACESHIP_STEP
        elif x_force < -TILT_FORCE:
            spaceship_position += SPACESHIP_STEP
        spaceship_position = max(0, min(fb.width - 1, spaceship_position))
    
        # Move alien
        if now - alien_start_time > ALIENS_STEP_TIME / alien_speed:
            for note in notes:
                note.stop()
            next(notes_cycle).play(duration=0.20)
            alien_at_right_side = alien_direction > 0 and max(alien_columns) == fb.width - 1
            alien_at_left_side = alien_direction < 0 and min(alien_columns) == 0
            if alien_at_left_side or alien_at_right_side:
                alien_row -= 1
                alien_speed *= 1.3
                alien_direction = - alien_direction
                if alien_row == 0:
                    break
            else:
                alien_columns = [column + alien_direction for column in alien_columns]
            alien_start_time = now
    
        # Check for collision
        if missile_y == alien_row and missile_x in alien_columns:
            alien_columns.remove(missile_x)
            missile_x, missile_y = -1, -1
            hit_sound.play()
            if not alien_columns:
                break
    
        # ########################################
        # Show world
        # ########################################
    
        fb.erase()
    
        # Draw missile
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
        scroll(lose_text, speed=0.12)
    else:
        print("You win!")
        scroll(win_text, speed=0.12)
