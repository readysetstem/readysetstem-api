import testing_log
import importlib
import testing
import pytest
import rstem.gpio as g
import time
from threading import Timer
from functools import wraps

'''
Automatic tests of gpio module via loopback output to input

Short GPIO 23 to 24.
'''

OUTPUT_PIN = 23
INPUT_PIN = 24

def io_setup(button=False, input_active_low=False, output_active_low=False, pull=None):
    def decorator(func):
        @wraps(func)
        def wrapper():
            # Setup
            if button:
                i = g.Button(INPUT_PIN)
            else:
                i = g.Input(INPUT_PIN, active_low=input_active_low, pull=pull)
            o = g.Output(OUTPUT_PIN, active_low=output_active_low)

            passed = func(i, o)

            # Teardown
            g.DisabledPin(OUTPUT_PIN)
            g.DisabledPin(INPUT_PIN)

            return passed
        return wrapper
    return decorator

"""
@testing.automatic
@io_setup()
def output_starts_off(i, o):
    return i.is_off()

@testing.automatic
@io_setup()
def output_turned_on(i, o):
    o.off()
    o.on()
    return i.is_on()

@testing.automatic
@io_setup()
def output_turned_off(i, o):
    o.on()
    o.off()
    return i.is_off()

@testing.automatic
@io_setup()
def output_turned_on_via_set(i, o):
    o.off()
    o.level = 1
    return i.is_on()

@testing.automatic
@io_setup()
def output_turned_off_via_set(i, o):
    o.on()
    o.level = 0
    return i.is_off()

@testing.automatic
@io_setup()
def io_on_off_sequence(i, o):
    on_times = 0
    off_times = 0
    TRIES = 100
    for n in range(TRIES):
        o.on()
        if i.is_on:
            on_times += 1
        o.off()
        if i.is_off:
            off_times += 1
    passed = on_times == TRIES and off_times == TRIES
    if not passed:
        print("Failed: on_times {}, off_times {}, TRIES {}".format(on_times, off_times, TRIES))
    return passed

@testing.automatic
@io_setup()
def output_init_start_off_false(i, o):
    return False

@testing.automatic
@io_setup(output_active_low=True)
def output_init_active_low_on(i, o):
    o.on()
    return i.level == 0

@testing.automatic
@io_setup(output_active_low=True)
def output_init_active_low_off(i, o):
    o.off()
    return i.level == 1

@testing.automatic
@io_setup()
def input_is_off(i, o):
    o.off()
    return i.is_off()

@testing.automatic
@io_setup()
def input_is_on(i, o):
    o.off()
    return i.is_off()

@testing.automatic
@io_setup()
def input_is_off_via_get(i, o):
    o.on()
    return i.level

@testing.automatic
@io_setup()
def input_is_on_via_get(i, o):
    o.off()
    return not i.level

@testing.automatic
@io_setup()
def input_wait_for_change(i, o):
    return False

@testing.automatic
@io_setup()
def input_wait_for_change_with_timeout(i, o):
    return False

@testing.automatic
@io_setup()
def input_call_if_changed_rising(i, o):
    input_call_if_changed_rising.count = 0
    def callme(change):
        input_call_if_changed_rising.count += 1
    o.level = 0
    i.call_if_changed(callme, g.RISING)
    o.level = 1
    print("Rising edge detected {} times".format(input_call_if_changed_rising.count))
    return input_call_if_changed_rising.count == 1

@testing.automatic
@io_setup()
def input_wait_for_change_rising(i, o):
    def callme(o):
        o.level = 1
    o.level = 0
    Timer(0.1, callme, args=[o]).start()
    i.wait_for_change(g.RISING)
    return True

@testing.automatic
@io_setup()
def input_wait_for_change_rising_timeout(i, o):
    def callme(o):
        o.level = 1
    o.level = 0
    Timer(0.1, callme, args=[o]).start()
    i.wait_for_change(g.RISING, timeout=10)
    return True

@testing.automatic
@io_setup()
def input_wait_for_change_norising_timeout(i, o):
    def callme(o):
        o.level = 0
    o.level = 1
    Timer(0.1, callme, args=[o]).start()
    i.wait_for_change(g.RISING, timeout=10)
    return True

@testing.automatic
@io_setup()
def input_wait_for_change_falling(i, o):
    def callme(o):
        o.level = 0
    o.level = 1
    Timer(0.1, callme, args=[o]).start()
    i.wait_for_change(g.FALLING)
    return True

@testing.automatic
@io_setup()
def input_wait_for_change_both(i, o):
    def callme(o, level):
        o.level = level
    o.level = 1
    Timer(0.1, callme, args=[o, 0]).start()
    i.wait_for_change(g.FALLING)
    Timer(0.1, callme, args=[o, 1]).start()
    i.wait_for_change(g.RISING)
    return True

@testing.automatic
@io_setup()
def input_changes_starts_zero(i, o):
    return i.changes() == (0, 0, 0)

@testing.automatic
@io_setup()
def input_changes_starts_zero_2(i, o):
    time.sleep(0.01)
    return i.changes() == (0, 0, 0)

@testing.automatic
@io_setup()
def input_changes_rising(i, o):
    o.level = 0
    o.level = 1
    time.sleep(0.1)
    changes = i.changes()
    #print(changes)
    return changes == (1, 0, 1)

@testing.automatic
@io_setup()
def input_changes_rising_2(i, o):
    o.level = 0
    o.level = 1
    time.sleep(0.00001)
    o.level = 0
    time.sleep(0.00001)
    changes = i.changes()
    print(changes)
    return changes == (1, 1, 0)
"""
def delay_ms(ms):   
    """ Somewhat accurate millisecond busy-loop delay for testing """
    start_time = time.time() * 1000
    while (time.time() * 1000 < start_time + ms):
        pass

@testing.automatic
@io_setup()
def input_changes_rising_3(i, o):
    o.level = 0; delay_ms(10); i.changes()
    print(i.changes())

    o.level = 0; delay_ms(10); i.changes()
    o.level = 0; delay_ms(10)
    print(i.changes())

    o.level = 0; delay_ms(10); i.changes()
    o.level = 0; delay_ms(10)
    o.level = 1; delay_ms(10)
    print(i.changes())

    o.level = 0; delay_ms(10); i.changes()
    o.level = 0; delay_ms(10)
    o.level = 1; delay_ms(10)
    o.level = 0; delay_ms(10)
    print(i.changes())

    o.level = 0; delay_ms(10); i.changes()
    o.level = 0; delay_ms(10)
    o.level = 1; delay_ms(10)
    o.level = 0; delay_ms(10)
    o.level = 1; delay_ms(10)
    print(i.changes())

    return changes == (1, 1, 0)

"""
@testing.automatic
def input_recreation(i, o):
    # Recreate input pin serval times and verify
    pass

@testing.automatic
@io_setup()
def input_changes(i, o):
    o.level = 0
    print("CHANGES: ", i.changes())
    o.level = 1
    o.level = 0
    o.level = 1
    o.level = 0
    time.sleep(0.000001)
    print("CHANGES: ", i.changes())
    print("CHANGES: ", i.changes())
    return True

@testing.automatic
@io_setup()
def input_call_if_changed_disable(i, o):
    return False

@testing.automatic
@io_setup(input_active_low=True)
def input_init_active_low_on(i, o):
    o.level = 0
    return i.is_on()

@testing.automatic
@io_setup(input_active_low=True)
def input_init_active_low_off(i, o):
    o.level = 1
    return i.is_off()

@testing.automatic
@io_setup()
def input_init_poll_period_slow(i, o):
    return False

@testing.automatic
@io_setup()
def input_init_pullup(i, o):
    return False

@testing.automatic
@io_setup()
def input_init_pulldown(i, o):
    return False

@testing.automatic
@io_setup()
def input_init_pullnone(i, o):
    return False

@testing.automatic
def input_invalid_pin():
    passed = False
    try:
        g.Input(5)
    except ValueError:
        passed = True
    return passed

@testing.automatic
@io_setup(button=True)
def input_button_is_pressed(b, o):
    o.level = 0
    return b.is_pressed()

@testing.automatic
@io_setup(button=True)
def input_button_is_released(b, o):
    o.level = 1
    return b.is_released()

@testing.automatic
@io_setup()
def time_output(i, o):
    TRIES = 100
    start = time.time()
    for n in range(TRIES):
        o.on()
    end = time.time()
    rate = float(TRIES)/(end-start)
    # We expect this to run at least MINIMUM_RATE in Hz.  Arbitrary, just to
    # keep it reasonable (testing shows it runs at ~3kHz).
    MINIMUM_RATE = 1000
    print("Output test running at: {:.2f}Hz (MINIMUM_RATE: {}Hz)".format(rate, MINIMUM_RATE))
    return rate > MINIMUM_RATE

@testing.automatic
@io_setup()
def time_input(i, o):
    TRIES = 100
    start = time.time()
    for n in range(TRIES):
        i.is_on()
    end = time.time()
    rate = float(TRIES)/(end-start)
    # We expect this to run at least MINIMUM_RATE in Hz.  Arbitrary, just to
    # keep it reasonable (testing shows it runs at ~3kHz).
    MINIMUM_RATE = 1000
    print("Input test running at: {:.2f}Hz (MINIMUM_RATE: {}Hz)".format(rate, MINIMUM_RATE))
    return rate > MINIMUM_RATE

"""
