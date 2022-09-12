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

import os
import pydicom
import cv2
import numpy as np
import math
import glob
import time
from torch.multiprocessing import Pool, Process, set_start_method
#import multiprocessing

import torch
import pandas as pd
import struct
import statistics
import argparse
from faberRegistratorsTorch import *
from faberOptimizersTorch import *


def compute_wrapper(args, faber_pl, num_threads=1, image_dimension=512):
    config=args.config
    faber_list=[]
    optimizer=None
    if args.optimizer =='powell':
        optimizer=FaberTorchPowell()
    else:
        optimizer=FaberTorchOnePlusOne()
    for k in range(args.offset, args.patient):
        pool = []
        curr_prefix = args.prefix+str(k)
        curr_ct = os.path.join(curr_prefix,args.ct_path)
        curr_pet = os.path.join(curr_prefix,args.pet_path)
        curr_res = os.path.join("",args.res_path)
        os.makedirs(curr_res,exist_ok=True)
        CT=glob.glob(curr_ct+'/*dcm')
        PET=glob.glob(curr_pet+'/*dcm')
        PET.sort()
        CT.sort()
        assert len(CT) == len(PET)
        images_per_thread = len(CT) // num_threads
        for i in range(num_threads):
            start = images_per_thread * i
            end = images_per_thread * (i + 1) if i < num_threads - 1 else len(CT)
            faber_component = FaberTorchMetric(ref_size=image_dimension, metric=args.metric, transform=args.transform, \
                exponential=args.exponential, interpolation="nearest")
            name = "t%02d" % (i)
            #pool.append(multiprocessing.Process(target=optimizer.compute, args=(CT[start:end], PET[start:end], name, curr_res, i, k, faber_component, image_dimension)))
            #pool.append(Process(target=optimizer, args=(CT[start:end], PET[start:end], name, curr_res, i, k, faber_component, image_dimension)))
            optimizer.compute(CT[start:end], PET[start:end], name, curr_res, i, k, faber_component, image_dimension)
            faber_list.append(faber_component)
        for t in pool:
            t.start()
        for t in pool:
            t.join()




def main():

    parser = argparse.ArgumentParser(description='Faber software for IR onto a python env')
    parser.add_argument("-pt", "--patient", nargs='?', help='Number of the patient to analyze', default=1, type=int)
    parser.add_argument("-o", "--offset", nargs='?', help='Starting patient to analyze', default=0, type=int)
    parser.add_argument("-cp", "--ct_path", nargs='?', help='Path of the CT Images', default='./')
    parser.add_argument("-pp", "--pet_path", nargs='?', help='Path of the PET Images', default='./')
    parser.add_argument("-rp", "--res_path", nargs='?', help='Path of the Results', default='./')
    parser.add_argument("-t", "--thread_number", nargs='?', help='Number of // threads', default=1, type=int)
    parser.add_argument("-px", "--prefix", nargs='?', help='prefix Path of patients folder', default='./')
    parser.add_argument("-im", "--image_dimension", nargs='?', help='Target images dimensions', default=512, type=int)
    parser.add_argument("-c", "--config", nargs='?', help='prefix Path of patients folder', default='./')
    parser.add_argument("-mtr", "--metric", nargs='?', help='Metric to be tested', default='')
    parser.add_argument("-tx", "--transform", nargs='?', help='Transform to be tested', default='')
    parser.add_argument("-exp", "--exponential",  action='store_true', help='if the metric is exponential, useful for MI and PRZ')
    parser.add_argument("-opt", "--optimizer", nargs='?', help='Optimizer to be tested, powell and oneplusone', default='')
    
    args = parser.parse_args()

    print(args.config)
    print(args)

    #try:
    compute_wrapper(args, None, args.thread_number, args.image_dimension
)
    #except Exception as e:
    #    print("An exception occurred: "+str(e))


    print("Faber SW-" + str(args.optimizer)+" python is at the end :)")



if __name__== "__main__":
    main()
