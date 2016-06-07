# ##################################
# Import Modules and Initialize Game
# ##################################

from rstem.button import Button
from rstem.gpio import Output
from rstem.sound import Note
from random import randrange
import time
from itertools import cycle

buttons = [Button(14), Button(15), Button(23), Button(17)]
lights = [Output(4), Output(18), Output(24), Output(27)]
notes = [Note('C5'), Note('D5'), Note('E5'), Note('F5')]

you_failed_note = Note('E4')

light_cycle = cycle(lights)
while True:
    for b in buttons:
        b.presses()
    pressed = False
    prev_light = next(light_cycle)
    cur_light = next(light_cycle)
    while not pressed:
        prev_light.off()
        cur_light.on()
        prev_light = cur_light
        cur_light = next(light_cycle)

        for b in buttons:
            pressed = pressed or b.presses()

        time.sleep(0.1)

    # ##################################
    # Main while: loop for game
    # ##################################

    for light in lights: 
            light.off()

    time.sleep(1)

    play_order = []
    failed = False
    while not failed:
            
            # Add another random LED to sequence
            play_order += [randrange(4)] 

            # Play LED sequence 
            for i in play_order: 
                    lights[i].on() 
                    notes[i].play(0.4).wait() 
                    lights[i].off()
                    time.sleep(0.2) 

            # #############################
            # for: loop to get player input
            # #############################

            for i in play_order:

                    # Get the user's button press
                    button_pressed = Button.wait_many(buttons, timeout=3) 

                    # If user enters incorrect button, end game
                    if button_pressed != i: 
                            failed = True 
                            break 

                    # If user enters correct button, flash LED and play tone
                    lights[button_pressed].on()     
                    notes[button_pressed].play(duration=None)
                    buttons[button_pressed].wait(press=False) 
                    time.sleep(0.2)
                    lights[button_pressed].off() 
                    notes[button_pressed].stop() 

            if not failed: 
                    time.sleep(1.0)

# Game Over -- Play error sequence
    if button_pressed == None: 
            for light in lights: 
                    light.on()
    else: 
            lights[button_pressed].on()

    you_failed_note.play(1.5).wait()

    for light in lights: 
            light.off()

    time.sleep(0.5)

# Play correct sequence fast
    for i in play_order: 
            lights[i].on() 
            notes[i].play(0.2).wait()
            lights[i].off() 
            time.sleep(0.2)
