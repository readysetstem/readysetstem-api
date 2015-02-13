import testing_log
import importlib
import testing
import time
from threading import Timer
from functools import wraps

from rstem import accel

'''
Automatic tests of accel module

Accelerometer must be connected via VCC, GND, SDA and SCL.  Accelerometer must
sit level (flat) in the X/Y directions.
'''

def io_setup(output_active_low=False, pull=None):
    def decorator(func):
        @wraps(func)
        def wrapper():
            a = accel.Accel()

            passed = func(a)

            return passed
        return wrapper
    return decorator

@testing.automatic
@io_setup()
def accel_forces(a):
    x, y, z = a.forces()
    x_good = abs(0.0 - x) < 0.05
    y_good = abs(0.0 - y) < 0.05
    z_good = abs(1.0 - z) < 0.05
    return x_good and y_good and z_good

@testing.automatic
@io_setup()
def accel_time_forces(a):
    TRIES = 100
    start = time.time()
    for n in range(TRIES):
        x, y, z = a.forces()
    end = time.time()
    rate = float(TRIES)/(end-start)
    # We expect this to run at least MINIMUM_RATE in Hz.  Arbitrary, just to
    # keep it reasonable (testing shows it runs at ~300Hz).
    MINIMUM_RATE = 100
    print("Output test running at: {:.2f}Hz (MINIMUM_RATE: {}Hz)".format(rate, MINIMUM_RATE))
    return rate > MINIMUM_RATE