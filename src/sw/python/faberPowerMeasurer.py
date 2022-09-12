#!/usr/bin/env python
#CARE IF PYTHON OR PYTHON 3
# coding: utf-8

# /******************************************
# *MIT License
# *
# *Copyright (c) [2022] [Eleonora D'Arnese, Davide Conficconi, Emanuele Del Sozzo, Luigi Fusco, Donatella Sciuto, Marco Domenico Santambrogio]
# *
# *Permission is hereby granted, free of charge, to any person obtaining a copy
# *of this software and associated documentation files (the "Software"), to deal
# *in the Software without restriction, including without limitation the rights
# *to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# *copies of the Software, and to permit persons to whom the Software is
# *furnished to do so, subject to the following conditions:
# *
# *The above copyright notice and this permission notice shall be included in all
# *copies or substantial portions of the Software.
# *
# *THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# *IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# *FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# *AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# *LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# *OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# *SOFTWARE.
# ******************************************/
from pynq import Device
from pynq.pmbus import DataRecorder       
import pandas as pd
import numpy as np

class FaberPowerMeasurer(object):

    def __init__(self):
        object.__init__(self)
        self.sensors = Device.active_device.sensors
        self.recorder = DataRecorder(self.sensors["12v_aux"].power,
        self.sensors["12v_pex"].power,
        self.sensors["vccint"].power)


    def measure_power(self):
        self.recorder.mark()

    def rec_power(self, recording_interval=0.1):
        self.recorder.record(recording_interval)

    def stop_rec(self):
        self.recorder.stop()

    def get_board_power(self):
        f = self.recorder.frame
        self.powers = pd.DataFrame(index=f.index)
        self.powers['board_power'] = f['12v_aux_power'] + f['12v_pex_power']
        self.powers['fpga_power'] = f['vccint_power']
        self.mean_power=np.mean(self.powers['board_power'])
        return self.mean_power