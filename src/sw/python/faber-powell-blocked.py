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

def optimize_goldsearch(par, rng, ref_sup_ravel, flt_sup, linear_par,i,wonderful_list):
    start=par-0.382*rng
    end=par+0.618*rng
    c=(end-(end-start)/1.618)
    d=(start+(end-start)/1.618)
    best_mi = 0.0
    while(math.fabs(c-d)>FaberHyperParams.gss_optimaze_ths):
        linear_par[i]=c
        a=to_matrix_blocked(linear_par)
        linear_par[i]=d
        b=to_matrix_blocked(linear_par)
        mi_a = wonderful_list[0](wonderful_list[1],ref_sup_ravel,flt_sup,a,\
            wonderful_list[2],wonderful_list[3],\
            wonderful_list[4],wonderful_list[5],wonderful_list[6],wonderful_list[7],\
            wonderful_list[8],wonderful_list[9])
        mi_b = wonderful_list[0](wonderful_list[1],ref_sup_ravel,flt_sup,b,\
            wonderful_list[2],wonderful_list[3],\
            wonderful_list[4],wonderful_list[5],wonderful_list[6],wonderful_list[7],\
            wonderful_list[8],wonderful_list[9])
        if(mi_a < mi_b):
            end=d
            best_mi = mi_a
            linear_par[i]=c
        else:
            start=c
            best_mi = mi_b
            linear_par[i]=d
        c=(end-(end-start)/1.618)
        d=(start+(end-start)/1.618)
        #it=it+1
    #print("Iterations gss " +str(it))
    return (end+start)/2, best_mi

def optimize_powell(rng, par_lin, ref_sup_ravel, flt_sup, wonderful_list):
    converged = False
    eps = FaberHyperParams.powell_optimize_eps
    last_mut=100000.0
    it=0
    while(not converged):
        converged=True
        it=it+1
        for i in range(len(par_lin)):
            cur_par = par_lin[i]
            cur_rng = rng[i]
            param_opt, cur_mi = optimize_goldsearch(cur_par, cur_rng, ref_sup_ravel, flt_sup, par_lin,i,wonderful_list)
            par_lin[i]=cur_par
            if last_mut-cur_mi>eps:
                par_lin[i]=param_opt
                last_mut=cur_mi
                converged=False
            else:
                par_lin[i]=cur_par
    #print("Iterations "+str(it))
    return (par_lin)



def register_images(Ref_uint8, Flt_uint8, wonderful_list):
    params = np.zeros((2,3))
    estimate_initial(Ref_uint8, Flt_uint8, params)
    rng=np.array([FaberHyperParams.powell_rng_1, FaberHyperParams.powell_rng_2, FaberHyperParams.powell_rng_3])
    pa=[params[0][2],params[1][2],params[0][0]]
    
    Ref_uint8_ravel = Ref_uint8.ravel()

    optimal_params = optimize_powell(rng, pa, Ref_uint8_ravel, Flt_uint8, wonderful_list) 
    params_trans=to_matrix_blocked(optimal_params)
    flt_transform = transform(Flt_uint8, params_trans)
    return (flt_transform)


def compute(CT, PET, name, curr_res, t_id, patient_id, wonderful_list, image_dimension):
    final_img=[]
    times=[]
    t = 0.0
    it_time = 0.0
    dim = image_dimension
    for c,ij in enumerate(zip(CT, PET)):
        i = ij[0]
        j = ij[1]
        Ref_uint8, Flt_uint8 = read_and_prepare_dicom_ref_flt_pair(i,j,dim)

        # ref = pydicom.dcmread(i)
        # Ref_img = ref.pixel_array
        # Ref_img[Ref_img==-2000]=1

        # flt = pydicom.dcmread(j)
        # img = flt.pixel_array

        # Flt_img = cv2.resize(img, dsize=(dim, dim))


        # Ref_uint8=cv2.normalize(Ref_img, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        # Flt_uint8=cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

        start_time = time.time()
        final_img.append(register_images(Ref_uint8, Flt_uint8,wonderful_list))
        end_time= time.time()
        it_time = (end_time - start_time)
        times.append(it_time)
        t=t+it_time
        print(i)
        print(j)
        print("%d) --- %s seconds ---" % (c, it_time))
        

    df = pd.DataFrame([t, np.mean(times), np.std(times)],columns=['Test'+str(patient_id)])
    times_df = pd.DataFrame(times,columns=['Test'+str(patient_id)])
    df_path = os.path.join(curr_res,'Time_powll_%02d.csv' % (t_id))
    times_df_path = os.path.join(curr_res,'Img_powll_%02d.csv' % (t_id))
    df.to_csv(df_path, index=False)
    times_df.to_csv(times_df_path, index=False)
    save_data(final_img,PET,curr_res)



def compute_wrapper(args, faber_pl, num_threads=1, image_dimension=512):
    config=args.config
    the_list_of_wonderful_lists=faber.faber_accel_map(programmable_logic=faber_pl, \
        number_of_cores=num_threads, metric=args.metric, transform=args.transform,\
        image_dimension=image_dimension, caching=args.caching, platform=args.platform, exponential=args.exponential)

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
            wonderful_list = the_list_of_wonderful_lists[i%num_threads]
            name = "t%02d" % (i)
            pool.append(multiprocessing.Process(target=compute, args=(CT[start:end], PET[start:end], name, curr_res, i, k, wonderful_list, image_dimension)))
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
    parser.add_argument("-ol", "--overlay", nargs='?', help='Path and filename of the target overlay', default='./faber_wrapper.bit')
    parser.add_argument("-clk", "--clock", nargs='?', help='Target clock frequency of the PL', default=100, type=int)
    parser.add_argument("-t", "--thread_number", nargs='?', help='Number of // threads', default=1, type=int)
    parser.add_argument("-px", "--prefix", nargs='?', help='prefix Path of patients folder', default='./')
    parser.add_argument("-p", "--platform", nargs='?', help='platform to target.\
     \'Alveo\' is used for PCIe/XRT based,\n while \'Ultra96\' will setup for a Zynq-based environment', default='Alveo')
    parser.add_argument("-mem", "--caching", action='store_true', help='if it use or not the caching')    
    parser.add_argument("-im", "--image_dimension", nargs='?', help='Target images dimensions', default=512, type=int)
    parser.add_argument("-c", "--config", nargs='?', help='prefix Path of patients folder', default='./')
    parser.add_argument("-mtr", "--metric", nargs='?', help='Metric accelrator to be tested', default='')
    parser.add_argument("-tx", "--transform", nargs='?', help='Metric accelrator to be tested', default='')
    parser.add_argument("-exp", "--exponential",  action='store_true', help='if the metric is exponential, useful for MI and PRZ')
    
    args = parser.parse_args()
    accel_number=args.thread_number

    dim = args.image_dimension
    patient_number=args.patient


    faber = Overlay(args.overlay)

    num_threads = accel_number

    if args.platform=='Zynq' :
        from pynq.ps import Clocks;
        print("Previous Frequency "+str(Clocks.fclk0_mhz))
        Clocks.fclk0_mhz = args.clock; 
        print("New frequency "+str(Clocks.fclk0_mhz))
   
    print(args.config)
    print(args)

    #try:
    compute_wrapper(args, faber, num_threads, dim)
    #except Exception as e:
    #    print("An exception occurred: "+str(e))

        

    if args.platform =='Alveo':
        faber.free()

    print("Faber Powell python is at the end :)")



if __name__== "__main__":
    main()
