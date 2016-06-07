# ##################################
# Import Modules and Initialize Game
# ##################################

from rstem.button import Button
from rstem.gpio import Output
from rstem.sound import Note
from random import randrange
import time

buttons = [Button(14), Button(15), Button(23), Button(17)]
lights = [Output(4, active_low=False), Output(18, active_low=False), Output(24, active_low=False), Output(27, active_low=False)]
notes = [Note('C'), Note('D'), Note('E'), Note('F')]

you_failed_note = Note('E3')

while True:
    button_pressed = 0
    count = 0
    while not button_pressed:
        for light in lights:
            if count % 15:
                light.off()
            else:
                light.on()
        for button in buttons:
            button_pressed += button.presses()
        count += 1
        time.sleep(0.2)

    for light in lights:
        light.on()
    time.sleep(1)
    for button in buttons:
        button.presses()
    for light in lights:
        light.off()
    time.sleep(0.6)

    play_order = []

    failed = False

    # ##################################
    # Main while: loop for game
    # ##################################

    while not failed:

        # Add another random LED to sequence
        play_order.append(randrange(4))

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

    # Game Over — Play error sequence
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


