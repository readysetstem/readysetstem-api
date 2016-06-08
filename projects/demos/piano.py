from rstem.button import Button
from rstem.sound import Note
import time

buttons_and_notes = [
    [Button(10), Note('G3')],
    [Button(3),  Note('A3')],
    [Button(2),  Note('B3')],
    [Button(15), Note('C')],
    [Button(17), Note('D')],
    [Button(23), Note('E')],
    [Button(11), Note('F')],
    [Button(7),  Note('G')],
    [Button(19), Note('A')],
    [Button(20), Note('B')],
    [Button(26), Note('C5')],
    [Button(21), Note('D5')],
    ]

while True:
    for button, note in buttons_and_notes:
        if button.is_pressed():
            if not note.is_playing():
                note.play(duration=None)
        else:
            note.stop()
    time.sleep(0.01)

