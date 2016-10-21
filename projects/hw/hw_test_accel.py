from rstem.accel import Accel
from rstem.gpio import Input, Output
from rstem.button import Button
import sys
import time
import os

def near(actual, expected):
    return abs(actual - expected) < 0.1

NUM_SAMPLES = 5

pins = {
    "PASS0":10,
    "FAIL0":22,
    "PASS1":27,
    "FAIL1":17,
    "PASS2":14,
    "FAIL2":15,
    "PASS3":18,
    "FAIL3":23,
    "PASS4":24,
    "FAIL4":25,
    "PASS5":8,
    "FAIL5":7,
    "PASS6":12,
    "FAIL6":16,
    "PASS7":20,
    "FAIL7":21,
    "READY":19,
    "XTEST":13,
    "YTEST":6,
    "ZTEST":5,
    "STAT1":11,
    "STAT2":9,
    "START":26,
}


#
# Pins are turned on by 5V with GPIO to ground.  Unfortunately, the GPIOs can
# only go to 3.3V to turn them off, so instead we turn them off by disabling
# the pin (i.e. making an Input).  we keep track of the current pin state in
# pin_io.
#
pin_io = {}
def on(pin_name):
    if pin_name in pin_io:
        pin_io[pin_name].disable()
    pin_io[pin_name] = Output(pins[pin_name])
    pin_io[pin_name].on()

def off(pin_name):
    if pin_name in pin_io:
        pin_io[pin_name].disable()
    pin_io[pin_name] = Input(pins[pin_name])

#
# flasher generator
#
def flasher(pin_name, on_time, off_time):
    start = time.time()
    on(pin_name)

    while True:
        elapsed = time.time() - start
        if elapsed > off_time:
            on(pin_name)
            start = time.time()
        elif elapsed > on_time:
            off(pin_name)
        yield

def tester(xgood, ygood, zgood):
    start = time.time()
    for bus in range(2):
        for part in range(4):
            os.system("/usr/sbin/i2cset -y 1 {:s} {:s}".format(hex(0x70+bus),hex(1<<part)))
            try:
                a = Accel()
            except:
                yield False
                continue
            index = bus*4 + part
            forces = []
            for sample in range(NUM_SAMPLES):
                elapsed = 0
                while elapsed < 0.1:
                    yield
                    elapsed = time.time() - start
                start = time.time()

                try:
                    forces.append(a.forces())
                except:
                    break
            if len(forces) < NUM_SAMPLES:
                yield False
            else:
                def mean(items):
                    return sum(items)/len(items)
                xs, ys, zs = list(zip(*forces))
                yield near(xgood, mean(xs)) and near(ygood, mean(ys)) and near(zgood, mean(zs))

def flash_until_button(led):
    flash = flasher(led, 0.1, 1.0)
    while not start_button.presses():
        next(flash)
        time.sleep(0.01)
    on(led)
    
def test_all_in_one_direction(led, xgood, ygood, zgood):
    flash_until_button(led)
    for i in range(8):
        off("FAIL" + str(i))
    flash = flasher(led, 0.1, 0.2)
    test = tester(xgood, ygood, zgood)
    results = []
    for result in test:
        if result != None:
            results.append(result)
        next(flash)
        time.sleep(0.01)
    on(led)
    for i, passed in enumerate(results):
        if not passed:
            on("FAIL" + str(i))
    return results

start_button = Button(pins["START"])

#
# Hack!  Pin 8 is used by the LED Driver SPI bus, which we don't care about
# here.  So we forcibly disable it.
#
os.system("echo 8 > /sys/class/gpio/unexport")

for led in pins:
    if led != "START":
        off(led)

while True:
    for led in ["XTEST", "YTEST", "ZTEST"]:
        off(led)
    flash_until_button("READY")
    xresults = test_all_in_one_direction("XTEST", 1, 0, 0)
    yresults = test_all_in_one_direction("YTEST", 0, 1, 0)
    zresults = test_all_in_one_direction("ZTEST", 0, 0, 1)
    for i, results in enumerate(zip(xresults, yresults, zresults)):
        if False in results:
            on("FAIL" + str(i))
            off("PASS" + str(i))
        else:
            off("FAIL" + str(i))
            on("PASS" + str(i))
