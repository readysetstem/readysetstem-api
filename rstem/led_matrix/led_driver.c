/*
 * led_driver.c
 *
 * Copyright (c) 2016, Ready Set STEM
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/spi/spidev.h>

//
// The SPI speed/delay are critical parameters, determined by the maximum that
// the LED Matrix can handle.  The LED Matrix runs at 8MHz, and has to retrieve
// each byte via code before the next one comes in, so it requires some time
// between bytes.
//
// The timing is affected by both the SPI clock speed, and the delay between
// bytes.  Testing shows that we can run up to 2MHz with a 2 usec delay.  The
// parameters below include a safety margin.
//
// See rw_bytes() for more info.
//
#define MATRIX_SPI_SHIFT_REGISTER_LENGTH 32
#define SPI_SPEED 500000
#define SPI_DELAY 5 

int spi;
unsigned char spi_mode;
unsigned char bits_per_trans;
unsigned int spi_speed;


// SPI  =============================================

int start_spi(void) {
    int err;
    char * device;

    if (spi) {
        close(spi);
    }

    //
    // CE0 is handled manually via GPIO (outside of this function).  Therefore,
    // we use a hack: we run on the CE1 device, but we don't use CE1.  That
    // does mean CE1 will be wigglin' away, but it is unused.
    //
    // See also rw_bytes()
    //
    device = "/dev/spidev0.1";

    spi_mode = SPI_MODE_0;
    bits_per_trans = 8;
    spi_speed = SPI_SPEED;
    spi = open(device, O_RDWR);

    err = ioctl(spi, SPI_IOC_WR_MODE, &spi_mode);
    if (err < 0) goto out;

    err = ioctl(spi, SPI_IOC_RD_MODE, &spi_mode);
    if (err < 0) goto out;

    err = ioctl(spi, SPI_IOC_WR_BITS_PER_WORD, &bits_per_trans);
    if (err < 0) goto out;

    err = ioctl(spi, SPI_IOC_WR_MAX_SPEED_HZ, &spi_speed);
    if (err < 0) goto out;

out:
    if (err < 0 && spi > 0)
        close(spi);
    return spi;
}

int rw_bytes(int dev, char * val, char * buff, int len){
    struct spi_ioc_transfer tr[MATRIX_SPI_SHIFT_REGISTER_LENGTH];
    int i, j;
    int ret = 0;

    //
    // SPI transfers are done in blocks of MATRIX_SPI_SHIFT_REGISTER_LENGTH at
    // a time.  We do transfers of one byte each, as this is the only way to
    // include an inter-byte delay (see SPI_DELAY).  We do just
    // MATRIX_SPI_SHIFT_REGISTER_LENGTH at a time, because the largest
    // transfers would exceed the ioctl() capability (so we break it into
    // MATRIX_SPI_SHIFT_REGISTER_LENGTH chunks).
    //
    // Final note: because CE0 is at the mercy of the driver, and the LED
    // Matrices require CE0 active for the full transaction (the end of CE0
    // indicates when to show the framebuffer on the display), CE0 is handled
    // manually outside of this driver.
    //
    for (i = 0; i < len; i += MATRIX_SPI_SHIFT_REGISTER_LENGTH) {
        memset(tr, 0, sizeof(tr));
        for (j = 0; j < MATRIX_SPI_SHIFT_REGISTER_LENGTH; j++) {
            tr[j].tx_buf = (unsigned long) &val[i+j];
            tr[j].rx_buf = (unsigned long) &buff[i+j];
            tr[j].len = 1;
            tr[j].delay_usecs = SPI_DELAY;
        }
        ret = ioctl(dev, SPI_IOC_MESSAGE(MATRIX_SPI_SHIFT_REGISTER_LENGTH), tr);
    }
    return ret;
}

// Python Wrappers =================================================


static PyObject *py_init_spi(PyObject *self, PyObject *args){
    int ret;
    ret = start_spi();
    if (ret < 0) {
        PyErr_SetString(PyExc_IOError, "Failed to init SPI port.");
        return NULL;
    }
    return Py_BuildValue("");
}   

static PyObject *py_send(PyObject *self, PyObject *args){
    char *s;
    int len;
    if(!PyArg_ParseTuple(args, "y#", &s, &len)){
        PyErr_SetString(PyExc_TypeError, "Not an unsigned int!");
        return NULL;
    }
    if (len % MATRIX_SPI_SHIFT_REGISTER_LENGTH) {
        PyErr_SetString(PyExc_IOError, "Failed to read/write LED Matrices via SPI (bad len).");
        return NULL;
    }
    if (rw_bytes(spi, s, s, len) < 0) {
        PyErr_SetString(PyExc_IOError, "Failed to read/write LED Matrices via SPI (bad IO).");
        return NULL;
    }
    return Py_BuildValue("y#", s, len);
}

static PyMethodDef led_driver_methods[] = {
    {"init_spi", py_init_spi, METH_VARARGS, "Initialize the SPI port."},
    {"send", py_send, METH_VARARGS, "Sends bytes via SPI port."},
    {NULL, NULL, 0, NULL}  /* Sentinal */
};


// Python Setup Magic, don't touch! =====================

struct module_state {
    PyObject *error;
};

#if PY_MAJOR_VERSION >= 3
#define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))
#else
#define GETSTATE(m) (&_state)
static struct module_state _state;
#endif

#if PY_MAJOR_VERSION >= 3

static int led_driver_traverse(PyObject *m, visitproc visit, void *arg) {
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}

static int led_driver_clear(PyObject *m) {
    Py_CLEAR(GETSTATE(m)->error);
    return 0;
}


static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "led_driver",
        NULL,
        sizeof(struct module_state),
        led_driver_methods,
        NULL,
        led_driver_traverse,
        led_driver_clear,
        NULL
};

#define INITERROR return NULL

PyObject *
PyInit_led_driver(void)

#else
#define INITERROR return

void initled_driver(void)
#endif
{
    struct module_state *st;

#if PY_MAJOR_VERSION >= 3
    PyObject *module = PyModule_Create(&moduledef);
#else
    PyObject *module = Py_InitModule("led_driver", led_driver_methods);
#endif

    if (module == NULL)
        INITERROR;

    st = GETSTATE(module);

    st->error = PyErr_NewException("led_driver.Error", NULL, NULL);
    if (st->error == NULL) {
        Py_DECREF(module);
        INITERROR;
    }

#if PY_MAJOR_VERSION >= 3
    return module;
#endif
}
