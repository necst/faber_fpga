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
import cv2
import numpy as np
import math
import glob
import time
import pandas as pd
import multiprocessing
from pynq import Overlay
import pynq
from pynq import allocate
import struct
import statistics
import argparse
import faberNewFunctions
import faberWonderfulListMapper as faber
from faberImageRegistration import *
from faberRegistrators import *

def decimal_str(x: float, decimals: int = 10) -> str:
    return format(x, f".{decimals}f").lstrip().rstrip('0')



def main():

    parser = argparse.ArgumentParser(description='Faber tester for wax+metric class of accelerators')
    parser.add_argument("-ol", "--overlay", nargs='?', help='Path and filename of the target overlay', default='./faber_wrapper.bit')
    parser.add_argument("-clk", "--clock", nargs='?', help='Target clock frequency of the PL', default=100, type=int)
    parser.add_argument("-t", "--thread_number", nargs='?', help='Number of // threads', default=1, type=int)
    parser.add_argument("-p", "--platform", nargs='?', help='platform to target.\
     \'Alveo\' is used for PCIe/XRT based,\n while \'Ultra96\' will setup for a Zynq-based environment', default='Alveo')
    parser.add_argument("-mem", "--caching", action='store_true', help='if it use or not the caching')
    parser.add_argument("-im", "--image_dimension", nargs='?', help='Target images dimensions', default=512, type=int)
    parser.add_argument("-rp", "--res_path", nargs='?', help='Path of the Results', default='./')
    parser.add_argument("-c", "--config", nargs='?', help='hw config to print only', default='ok')
    parser.add_argument("-mtr", "--metric", nargs='?', help='Metric accelrator to be tested', default='mi')
    parser.add_argument("-tx", "--transform", nargs='?', help='Metric accelrator to be tested', default='wax')
    parser.add_argument("-exp", "--exponential",  action='store_true', help='if the metric is exponential, useful for MI and PRZ')


    hist_dim = 256
    dim = 512
    t=0
    args = parser.parse_args()
    accel_number=args.thread_number



    faber_pl = Overlay(args.overlay)
    num_threads = accel_number
    if args.platform=='Zynq':
        from pynq.ps import Clocks;
        print("Previous Frequency "+str(Clocks.fclk0_mhz))
        Clocks.fclk0_mhz = args.clock; 
        print("New frequency "+str(Clocks.fclk0_mhz))

    print(args)
    exponential=args.exponential
    #try:
    the_list_of_wonderful_lists=faber.faber_accel_map(programmable_logic=faber_pl, \
        number_of_cores=num_threads, metric=args.metric, transform=args.transform,\
        image_dimension=args.image_dimension, caching=args.caching, platform=args.platform,exponential=exponential)
    hw_tester=the_list_of_wonderful_lists[0]
    sw_tester = FaberGenericComponent(ref_size=args.image_dimension, metric=args.metric, transform="wax", exponential=exponential, interpolation=cv2.INTER_NEAREST)
    #time test single MI
    iterations=10
    t_tot = 0
    t_sw=0
    times=[]
    dim=args.image_dimension
    diffs=[]
    times_sw=[]
    random_tx=False
    random_input=True 

    np.random.seed(12345)
    j="../Test/ST0/SE0/IM10.dcm"
    l="../Test/ST0/SE4/IM10.dcm"
    start_tot = time.time()
    for i in range(iterations):
        print("[Test"+str(i)+"] Let's start")
        # ref = np.random.randint(low=0, high=255, size=(dim,dim), dtype='uint8')
        # flt = np.random.randint(low=0, high=255, size=(dim,dim), dtype='uint8')
        # params = np.zeros((2,3))
        # estimate_initial(ref,flt, params)

        if random_input==True:
            ref = np.random.randint(low=0, high=255, size=(dim,dim), dtype='uint8')
            flt = np.random.randint(low=0, high=255, size=(dim,dim), dtype='uint8')
        else:
            ref, flt = read_and_prepare_dicom_ref_flt_pair(j,l,dim)

        if random_tx == False:
            params = np.zeros((2,3))
            params=estimate_initial(ref,flt, params)
        else:
            params = np.array([[1.0,0.0,0.0],[0.0,1.0,0.0]])

       

        start_sw =time.time()
        sw_mi= sw_tester.compute_metric(ref, flt, params)   
        end_sw =time.time()   
        t_sw=end_sw - start_sw
        times_sw.append(t_sw)
        start_single = time.time()
        out =  hw_tester[0](hw_tester[1],ref,flt,params,hw_tester[2],hw_tester[3],\
            hw_tester[4],hw_tester[5],hw_tester[6],hw_tester[7],hw_tester[8],hw_tester[9])
        end_single = time.time()
        print("Hw res: "+str(out))
        print("Sw res: "+str(sw_mi))
        t = end_single - start_single
        times.append(t)
        print("Sw time:" + str(t_sw) + " hw time: "+ str(t ))
        print("\n")
        diff=np.abs(sw_mi) - np.abs(out)
        diffs.append(diff)
        t_tot = t_tot +  t
    end_tot = time.time()

    print(np.mean(diffs))
    df = pd.DataFrame([\
        ["total_time_hw ",t_tot],\
        ["mean_time_hw",np.mean(times)],\
        ["std_time_hw",np.std(times)],\
        ["mean_time_sw",np.mean(times_sw)],\
        ["std_time_sw",np.std(times_sw)],\
        ["mean_diff",np.mean(diffs)],\
        ["std_diffs",np.std(diffs)]],\
                    columns=['Label','Test'+str(args.overlay)])

    df_path = os.path.join(args.res_path,'Time_mtrtx'+args.transform+args.metric+'_%02d.csv' % (args.clock))
    df.to_csv(df_path, index=False)
    data = {'time'+str(args.overlay):times,\
            'error'+str(args.overlay):diffs}

    df_breakdown = pd.DataFrame(data,\
            columns=['time'+str(args.overlay),'error'+str(args.overlay)])
    df_path_breakdown = os.path.join(args.res_path,'Breakdown'+args.transform+args.metric+'_%02d.csv' % (args.clock))
    df_breakdown.to_csv(df_path_breakdown, index=False)
    
    #except Exception as e:
    #    print("An exception occurred: "+str(e))        
    if args.platform =='Alveo':
        faber_pl.free()

    print("Faber is at the end :)")



if __name__== "__main__":
    main()
