# -*- coding: utf-8 -*-
"""
Created on Tue Aug 12 20:02:08 2014

@author: Federico Barabas
"""

import logging
import numpy as np
import tifffile as tiff
import os

from lantz import Driver
from lantz import Q_

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s',
                    datefmt='%Y-%d-%m %H:%M:%S')


class constants:

    def __init__(self):
        self.GND = 0


class MockMotor(object):

    def __init__(self):
        super().__init__()

    def getHardwareInformation(self):
        return 'Simulated Motor'

    def getPos(self):
        return 5.55

    def mAbs(self, x):
        pass

    def cleanUpAPT(self):
        pass


class MockWebcam(object):

    def __init__(self):
        super().__init__()
        print('Simulated Webcam')

    def start(self):
        pass

    def get_image(self):
        arr = (100 * np.random.rand(480, 640)).astype(np.float)
        return arr
#        return pygame.surfarray.make_surface(arr)

    def stop(self):
        pass


class MockDAQ(Driver):

    def __init__(self):
        super().__init__()
        self.constants = constants()
        self.digital_IO = np.zeros(23, dtype='bool')
        self.flipperState = True

    @property
    def idn(self):
        return 'Simulated Labjack T7'

    def streamStop(self):
        pass

    def streamStart(self, *args, **kwargs):
        pass

    def streamRead(self):
        return (np.random.normal(1, 0.1, 100), 0)

    def writeNames(self, *args, **kwargs):
        pass

    def address(self, port):
        return (0, 0)

    @property
    def flipper(self):
        return self.flipperState

    @flipper.setter
    def flipper(self, value):
        self.flipperState = value

    def toggleFlipper(self):
        pass


class MockProscan(Driver):

    def __init__(self):
        super().__init__()
        self.zobject = MockScanZ()


class MockScanZ(Driver):

    def __init__(self):
        super().__init__()
        self.um = Q_(1, 'um')

        self._position = 1000 * self.um
        self._hostPosition = 'left'

    @property
    def idn(self):
        return '''Simulated Prior's NanoScanZ'''

    @property
    def position(self):
        '''Gets and sets current position.
        If the value is set to z = 0, the display changes to REL 0 (relative
        display mode). To return to ABS mode use inst.move_absolute(0) and then
        inst.position = 0. Thus, the stage will return to 0 micrometers and the
        display screen will switch to ABS mode.
        '''
        return self._position

    @position.setter
    def position(self, value):
        '''Gets and sets current position.
        If the value is set to z = 0, the display changes to REL 0 (relative
        display mode). To return to ABS mode use inst.move_absolute(0) and then
        inst.position = 0. Thus, the stage will return to 0 micrometers and the
        display screen will switch to ABS mode.
        '''
        try:
            value.magnitude
            self._position = value.to('um')
        except:
            self._position = value

    @property
    def zPosition(self):
        '''Gets and sets current position.
        If the value is set to z = 0, the display changes to REL 0 (relative
        display mode). To return to ABS mode use inst.move_absolute(0) and then
        inst.position = 0. Thus, the stage will return to 0 micrometers and the
        display screen will switch to ABS mode.
        '''
        return self._position

    @zPosition.setter
    def zPosition(self, value):
        '''Gets and sets current position.
        If the value is set to z = 0, the display changes to REL 0 (relative
        display mode). To return to ABS mode use inst.move_absolute(0) and then
        inst.position = 0. Thus, the stage will return to 0 micrometers and the
        display screen will switch to ABS mode.
        '''
        try:
            value.magnitude
            self._position = value.to('um')
        except:
            self._position = value

    def moveRel(self, value):
        self.position = self.position + value

    def zMoveRelative(self, value):
        self.position = self.position + value

    @property
    def zUmPerRevolution(self):
        return 100 * self.um

    @zUmPerRevolution.setter
    def zUmPerRevolution(self, value):
        pass

    @property
    def zHostPosition(self):
        return self._hostPosition

    @zHostPosition.setter
    def zHostPosition(self, value):
        self._hostPosition = value

    @property
    def HostBacklashEnable(self):
        return True

    @HostBacklashEnable.setter
    def HostBacklashEnable(self, value):
        pass

    def finalize(self):
        pass


class MockLaser(Driver):

    def __init__(self):
        super().__init__()

        self.mW = Q_(1, 'mW')

        self.enabled = False
        self.power_sp = 0 * self.mW

    @property
    def idn(self):
        return 'Simulated laser'

    @property
    def status(self):
        """Current device status
        """
        return 'Simulated laser status'

    @property
    def ld_temp(self):
        """To get the laser diode temperature (ºC)
        """
        return Q_(99.9, 'degC')

    @property
    def psuTemp(self):
        """To get the laser diode temperature (ºC)
        """
        return Q_(99.9, 'degC')

    @property
    def laserTemp(self):
        """To get the laser diode temperature (ºC)
        """
        return Q_(99.9, 'degC')

    @property
    def shg_temp(self):
        """To get the SHG temperature
        """
        return Q_(99.9, 'degC')

    # ENABLE LASER
    @property
    def enabled(self):
        """Method for turning on the laser
        """
        return self.enabled_state

    @enabled.setter
    def enabled(self, value):
        self.enabled_state = value

    # LASER'S CONTROL MODE AND SET POINT

    @property
    def power_sp(self):
        """To handle output power set point (mW) in APC Mode
        """
        return self.power_setpoint

    @power_sp.setter
    def power_sp(self, value):
        self.power_setpoint = value

    # LASER'S CURRENT STATUS

    @property
    def power(self):
        """To get the laser emission power (mW)
        """
        return 55555 * self.mW


class MockCamera(Driver):

    def __init__(self):
        super().__init__()

        self.s = Q_(1, 's')
        self.us = Q_(1, 'us')

        self.mock = True
        self.temperature_setpoint = -10
        self.cooler_on_state = False
        self.acq_mode = 'Run till abort'
        self.status_state = 'Camera is idle, waiting for instructions.'
        self.image_size = self.detector_shape
        self.preamp_st = 1
        self.EM_gain_st = 1
        self.ftm_state = False
        self.horiz_shift_speed_state = 1
        self.n_preamps = 1

        self.PreAmps = np.around([self.true_preamp(n)
                                  for n in np.arange(self.n_preamps)],
                                 decimals=1)[::-1]
        self.HRRates = [self.true_horiz_shift_speed(n)
                        for n in np.arange(self.n_horiz_shift_speeds())]
        self.vertSpeeds = [np.round(self.true_vert_shift_speed(n), 1)
                           for n in np.arange(self.n_vert_shift_speeds)]
        self.vertAmps = ['+' + str(self.true_vert_amp(n))
                         for n in np.arange(self.n_vert_clock_amps)]
        self.vertAmps[0] = 'Normal'

        with tiff.TiffFile(os.path.join(os.getcwd(), 'tormenta', 'control',
                           'beads.tif')) as ff:
            self.image = ff.asarray()

        self.expTime = 0.1 * self.s

    @property
    def idn(self):
        """Identification of the device
        """
        return 'Simulated Andor camera'

    @property
    def detector_shape(self):
        return (512, 512)

    @property
    def px_size(self):
        """ This function returns the dimension of the pixels in the detector
        in microns.
        """
        return (8, 8)

    @property
    def temperature(self):
        """ This function returns the temperature of the detector to the
        nearest degree. It also gives the status of cooling process.
        """
        return 55555

    @property
    def temperature_setpoint(self):
        return self.temperature_sp

    @temperature_setpoint.setter
    def temperature_setpoint(self, value):
        self.temperature_sp = value

    @property
    def cooler_on(self):
        return self.cooler_on_state

    @cooler_on.setter
    def cooler_on(self, value):
        self.cooler_on_state = value

    @property
    def temperature_status(self):
        if self.cooler_on_state:
            return 'Temperature stabilized'
        else:
            return 'Temperature not stabilized'

    @property
    def acquisition_mode(self):
        """ This function will set the acquisition mode to be used on the next
        StartAcquisition.
        NOTE: In Mode 5 the system uses a “Run Till Abort” acquisition mode. In
        Mode 5 only, the camera continually acquires data until the
        AbortAcquisition function is called. By using the SetDriverEvent
        function you will be notified as each acquisition is completed.
        """
        return self.acq_mode

    @acquisition_mode.setter
    def acquisition_mode(self, mode):
        self.acq_mode = mode

    def start_acquisition(self):
        """ This function starts an acquisition. The status of the acquisition
        can be monitored via GetStatus().
        """
        self.status_state = 'Acquisition in progress.'
        self.j = 0

    def abort_acquisition(self):
        """This function aborts the current acquisition if one is active
        """
        self.status_state = 'Camera is idle, waiting for instructions.'

    @property
    def status(self):
        """ This function will return the current status of the Andor SDK
        system. This function should be called before an acquisition is started
        to ensure that it is IDLE and during an acquisition to monitor the
        process.
        """
        return self.status_state

    def set_image(self, shape, p_0):
        """ This function will set the horizontal and vertical binning to be
        used when taking a full resolution image.
        Parameters
            int hbin: number of pixels to bin horizontally.
            int vbin: number of pixels to bin vertically.
            int hstart: Start column (inclusive).
            int hend: End column (inclusive).
            int vstart: Start row (inclusive).
            int vend: End row (inclusive).
        """
        self.p_0 = p_0
        self.image_size = (shape)

    def free_int_mem(self):
        """The FreeInternalMemory function will deallocate any memory used
        internally to store the previously acquired data. Note that once this
        function has been called, data from last acquisition cannot be
        retrived.
        """
        pass

    def most_recent_image16(self, shape):
        """ This function will update the data array with the most recently
        acquired image in any acquisition mode. The data are returned as long
        integers (32-bit signed integers). The "array" must be exactly the same
        size as the complete image.
        """
        im = self.image[self.p_0[0]:self.p_0[0]+self.image_size[0],
                        self.p_0[1]:self.p_0[1]+self.image_size[1]]
        im = np.random.poisson(im)
        noise = np.random.normal(400, 50, im.shape)
        return np.transpose(im + noise).astype(np.uint16)

    def images16(self, first, last, shape, validfirst, validlast):
        halfw = shape[0]//2
        halfh = shape[1]//2
        im = self.image[256 - halfw:256 + halfw, 256 - halfh:256 + halfh]
        arr = np.repeat(im[np.newaxis, :, :], last - first + 1, axis=0)
        return arr.astype(np.uint16)

    def set_n_kinetics(self, n):
        self.n = n

    def set_n_accum(self, i):
        pass

    def set_accum_time(self, dt):
        pass

    def set_kinetic_cycle_time(self, dt):
        pass

    @property
    def n_images_acquired(self):
        self.j += 1
        if self.j == self.n:
            self.status_state = 'Camera is idle, waiting for instructions.'
        return self.j

    @property
    def new_images_index(self):
        return (self.j, self.j)

    def shutter(self, *args):
        pass

    @property
    def preamp(self):
        return self.preamp_st

    @preamp.setter
    def preamp(self, value):
        self.preamp_st = value

    def true_preamp(self, n):
        return 10

    def n_horiz_shift_speeds(self):
        return 1

    def true_horiz_shift_speed(self, n):
        return 100 * self.us

    @property
    def horiz_shift_speed(self):
        return self.horiz_shift_speed_state

    @horiz_shift_speed.setter
    def horiz_shift_speed(self, value):
        self.horiz_shift_speed_state = value

    @property
    def max_exposure(self):
        return 12 * self.s

    @property
    def acquisition_timings(self):
        return 1.1*self.expTime, 1.1*self.expTime, 1.1*self.expTime

    @property
    def EM_gain_range(self):
        return (0, 1000)

    @property
    def EM_gain(self):
        return self.EM_gain_st

    @EM_gain.setter
    def EM_gain(self, value):
        self.EM_gain_st = value

    @property
    def n_vert_shift_speeds(self):
        return 4

    def true_vert_shift_speed(self, n):
        return 3.3 * self.us

    @property
    def n_vert_clock_amps(self):
        return 4

    def true_vert_amp(self, n):
        return 1

    def set_vert_clock(self, n):
        pass

    def set_exposure_time(self, t):
        values = [t.to('s').magnitude, self.max_exposure.to('s').magnitude]
        self.expTime = Q_(np.min(values), 's')

    @property
    def frame_transfer_mode(self):
        return self.ftm_state

    @frame_transfer_mode.setter
    def frame_transfer_mode(self, state):
        self.ftm_state = state
