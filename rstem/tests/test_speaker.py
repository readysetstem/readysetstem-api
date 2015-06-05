'''
Tests of sound module

Manual tests require a speaker attached to the the audio jack (with or without
speaker amplifier).
'''
import testing_log
import importlib
import testing
import time
from threading import Timer
from functools import wraps

from rstem.sound import Sound, Note, Speech, master_volume

TEST_SOUND='/home/pi/python_games/match1.wav'
TEST_SOUND_LENGTH=0.565125
TEST_SOUND_LONG='/opt/sonic-pi/etc/samples/loop_garzul.wav'
TEST_SOUND_LONG='/usr/share/scratch/Media/Sounds/Music Loops/Techno2.mp3'
TEST_SOUND_LONG_LENGTH=14.837551

"""

@testing.automatic
def abc():
    from rstem.button import Button
    from rstem.sound import Note

    buttons = [Button(17), Button(27)]
    notes = [Note('A'), Note('B')]

    while True:
        for button, note in zip(buttons, notes):
            if button.is_pressed():
                if not note.is_playing():
                    note.play(duration=None)
            else:
                note.stop()
            time.sleep(0.01)
    return True

@testing.automatic
def abc2():
    from rstem.sound import Note
    notes = [Note(n) for n in 'CDEFGABC']
    while True:
        for note in notes:
            note.play(duration=2)
            time.sleep(0.5)
    return True

@testing.automatic
def abc1():
    s = [Sound('/home/pi/python_games/match0.wav'),
        Sound('/home/pi/python_games/match1.wav'),
        Sound('/home/pi/python_games/match2.wav'),
        Sound('/home/pi/python_games/match3.wav')]
    s[0].play()
    s[1].play()
    s[2].play()
    s[3].play()
    time.sleep(2)
    return True

"""
@testing.automatic
def sound_init_with_known_good_sound():
    s = Sound(TEST_SOUND)
    return isinstance(s, Sound)

@testing.automatic
def sound_short_latency():
    s = Sound(TEST_SOUND)
    s.stop()
    start = time.time()
    s.play()
    s.wait()
    duration = time.time() - start
    latency = duration - TEST_SOUND_LENGTH
    print("Latency: ", latency)
    return latency > 0 and latency < 0.050

@testing.automatic
def sound_stop_time():
    #s = Sound(TEST_SOUND_LONG)
    s = Sound('/opt/sonic-pi/etc/samples/loop_garzul.wav')
    s.play()
    time.sleep(1)
    start = time.time()
    s.stop()
    end = time.time()
    duration = end - start
    print(start, end)
    print("stop() duration: ", duration)
    return duration > 0 and duration < 0.150

@testing.automatic
def sound_length():
    expected = Sound(TEST_SOUND).length() 
    actual = TEST_SOUND_LENGTH
    print("Expected: ", expected)
    print("Actual: ", actual)
    return expected == actual

@testing.automatic
def sound_init_bad_filename():
    try:
        s = Sound("qwemceqwncklenqwc")
    except IOError:
        return True
    return False

@testing.automatic
def sound_init_bad_filename_2():
    try:
        s = Sound([1,2,3])
    except TypeError:
        return True
    return False

@testing.automatic
def sound_not_is_playing_before_play():
    s = Sound(TEST_SOUND)
    return not s.is_playing()

@testing.automatic
def sound_not_is_playing_after_play():
    s = Sound(TEST_SOUND)
    print("before play")
    s.play()
    print("after play")
    time.sleep(TEST_SOUND_LENGTH + 0.5)
    print("after wait: ", s.is_playing())
    return not s.is_playing()

@testing.automatic
def sound_is_playing_at_play_start():
    s = Sound(TEST_SOUND)
    s.play()
    return s.is_playing()

@testing.automatic
def sound_is_playing_at_play_middle():
    s = Sound(TEST_SOUND)
    s.play()
    time.sleep(TEST_SOUND_LENGTH/2)
    return s.is_playing()

@testing.automatic
def sound_wait():
    s = Sound(TEST_SOUND)
    s.play()
    s.wait()
    return not s.is_playing()

@testing.automatic
def sound_stop():
    s = Sound(TEST_SOUND)
    s.play()
    s.stop()
    return not s.is_playing()

@testing.automatic
def sound_playing_before_end_of_duration_play():
    s = Sound(TEST_SOUND_LONG)
    s.play(duration=1.0)
    time.sleep(0.5)
    playing = s.is_playing()
    s.stop()
    return playing

@testing.automatic
def sound_not_playing_after_end_of_duration_play():
    s = Sound(TEST_SOUND_LONG)
    s.play(duration=1.0)
    time.sleep(1.5)
    return not s.is_playing()

@testing.automatic
def sound_negative_duration_play_failure():
    s = Sound(TEST_SOUND_LONG)
    try:
        s.play(duration=-1)
    except ValueError:
        return True
    return False

@testing.automatic
def sound_playing_before_end_of_2_loops():
    s = Sound(TEST_SOUND)
    s.play(loops=2)
    time.sleep(TEST_SOUND_LENGTH * 2 - 0.5)
    playing = s.is_playing()
    s.stop()
    return playing

@testing.automatic
def sound_not_playing_after_end_of_2_loops():
    s = Sound(TEST_SOUND)
    s.play(loops=2)
    time.sleep(TEST_SOUND_LENGTH * 2 + 0.5)
    playing = s.is_playing()
    s.stop()
    return not playing

@testing.automatic
def sound_playing_before_end_of_2_loops_of_fixed_duration():
    s = Sound(TEST_SOUND_LONG)
    s.play(duration=1.0, loops=2)
    playing = s.is_playing()
    s.stop()
    return playing

@testing.automatic
def sound_not_playing_after_end_of_2_loops_of_fixed_duration():
    s = Sound(TEST_SOUND_LONG)
    s.play(duration=1.0, loops=2)
    time.sleep(2.5)
    playing = s.is_playing()
    s.stop()
    return not playing

@testing.automatic
def sound_play_then_replay():
    s = Sound(TEST_SOUND_LONG)
    s.play()
    time.sleep(0.5)
    playing_firsttime = s.is_playing()
    s.play(duration=1.0)
    time.sleep(0.5)
    playing_secondtime_before_end = s.is_playing()
    time.sleep(1.0)
    playing_secondtime_after_end = s.is_playing()
    s.stop()
    print('playing_firsttime: ', playing_firsttime)
    print('playing_secondtime_before_end: ', playing_secondtime_before_end)
    print('playing_secondtime_after_end: ', playing_secondtime_after_end)
    return playing_firsttime and playing_secondtime_before_end and not playing_secondtime_after_end

@testing.automatic
def sound_get_set_volume():
    # Verify Sound volume attribute can be get/set.
    return False

@testing.automatic
def sound_chaining_test():
    # Sound should be chainable from init->play->wait add tests for each of
    # play/wait/stop for each object type (Sound, Note, Speech) to verify they
    # return themselves.
    return False

def _note_freq(note, expected_freq):
    # Frequencies from: http://www.phy.mtu.edu/~suits/notefreqs.html
    n = Note(note)
    actual_freq = n.frequency
    n = None
    print('Note: {}, expected frequency: {}'.format(note, expected_freq))
    print('Acutal frequency: {}'.format(actual_freq))
    return abs(expected_freq - actual_freq) < 0.1
    
@testing.automatic
def note_play():
    n = Note('A')
    n.play()
    n.wait()
    return True

@testing.automatic
def note_playing_before_end_of_duration_play():
    s = Note('A')
    s.play(duration=1.0)
    time.sleep(0.5)
    playing = s.is_playing()
    s.stop()
    return playing

@testing.automatic
def note_not_playing_after_end_of_duration_play():
    s = Note('A')
    s.play(duration=1.0)
    time.sleep(1.5)
    return not s.is_playing()

@testing.automatic
def note_bad_note():
    try:
        Note('cnasdj')
    except ValueError:
        return True
    return False

@testing.automatic
def note_freq_numeric():
    return _note_freq(123, 123)

@testing.automatic
def note_freq_a():
    return _note_freq('A', 440)

@testing.automatic
def note_freq_aflat():
    return _note_freq('Ab', 415.30)

@testing.automatic
def note_freq_asharp():
    return _note_freq('A#', 466.16)

@testing.automatic
def note_freq_1():
    return _note_freq('C0', 16.35)

@testing.automatic
def note_freq_2():
    return _note_freq('C#0', 17.32)

@testing.automatic
def note_freq_3():
    return _note_freq('Db0', 17.32)

@testing.automatic
def note_freq_4():
    return _note_freq('D0', 18.35)

@testing.automatic
def note_freq_5():
    return _note_freq('D#0', 19.45)

@testing.automatic
def note_freq_23():
    return _note_freq('Eb1', 38.89)

@testing.automatic
def note_freq_24():
    return _note_freq('E1', 41.20)

@testing.automatic
def note_freq_65():
    return _note_freq('A3', 220.00)

@testing.automatic
def note_freq_66():
    return _note_freq('A#3', 233.08)

@testing.automatic
def note_freq_67():
    return _note_freq('Bb3', 233.08)

@testing.automatic
def note_freq_68():
    return _note_freq('B3', 246.94)

@testing.automatic
def note_freq_69():
    return _note_freq('C4', 261.63)

@testing.automatic
def note_freq_70():
    return _note_freq('C#4', 277.18)

@testing.automatic
def note_freq_71():
    return _note_freq('Db4', 277.18)

@testing.automatic
def note_freq_72():
    return _note_freq('D4', 293.66)

@testing.automatic
def note_freq_73():
    return _note_freq('D#4', 311.13)

@testing.automatic
def note_freq_74():
    return _note_freq('Eb4', 311.13)

@testing.automatic
def note_freq_75():
    return _note_freq('E4', 329.63)

@testing.automatic
def note_freq_76():
    return _note_freq('F4', 349.23)

@testing.automatic
def note_freq_77():
    return _note_freq('F#4', 369.99)

@testing.automatic
def note_freq_78():
    return _note_freq('Gb4', 369.99)

@testing.automatic
def note_freq_79():
    return _note_freq('G4', 392.00)

@testing.automatic
def note_freq_80():
    return _note_freq('G#4', 415.30)

@testing.automatic
def note_freq_81():
    return _note_freq('Ab4', 415.30)

@testing.automatic
def note_freq_82():
    return _note_freq('A4', 440.00)

@testing.automatic
def note_freq_83():
    return _note_freq('A#4', 466.16)

@testing.automatic
def note_freq_84():
    return _note_freq('Bb4', 466.16)

@testing.automatic
def note_freq_85():
    return _note_freq('B4', 493.88)

@testing.automatic
def note_freq_86():
    return _note_freq('C5', 523.25)

@testing.automatic
def note_freq_162():
    return _note_freq('Bb8', 7458.62)

@testing.automatic
def note_freq_163():
    return _note_freq('B8', 7902.13)

@testing.automatic
def speech_play():
    s = Speech("Test")
    s.play()
    s.wait()
    return True

@testing.manual_output
def speech_manual_play():
    '''The text "These aren't the droids you're looking for." will play on the speaker.'''
    s = Speech("These aren't the droids you're looking for.")
    s.play()
    s.wait()

@testing.manual_output
def sound_play_test_sound():
    '''The sound match1.wav will play on the speaker (about 0.5 seconds).'''
    s = Sound(TEST_SOUND).play()
    s.play()
    s.wait()

@testing.manual_output
def sound_play_test_sound_loop_2():
    '''The sound match1.wav will play TWO TIMES on the speaker (about 0.5 seconds each).'''
    s = Sound(TEST_SOUND)
    s.play(loops=2)
    s.wait()

@testing.manual_output
def sound_master_volume():
    '''The sound match1.wav will play on the speaker 5 times (about 0.5 seconds
    each), at 60, 70, 80, 90 and 100% master volume.  Lower volumes are too low
    to hear with an unamplified speaker.
    '''
    master_volume( 60); Sound(TEST_SOUND).play().wait()
    master_volume( 70); Sound(TEST_SOUND).play().wait()
    master_volume( 80); Sound(TEST_SOUND).play().wait()
    master_volume( 90); Sound(TEST_SOUND).play().wait()
    master_volume(100); Sound(TEST_SOUND).play().wait()

@testing.manual
def sound_sound_volume():
    '''The long test sound will play for 10 second with increasing volume.
    '''
    master_volume(100)
    s = Sound(TEST_SOUND_LONG)
    s.volume = 0
    s.play(duration=10)
    for i in range(20):
        s.volume += 15
        time.sleep(0.5)
    s.wait()
    return True

'''
#New tests
- 2 notes at same time return repeating data
- replay note
'''
