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

# The 1+1 code takes inspiration from ITK code: https://github.com/InsightSoftwareConsortium/ITK
# All rights reserved by the ITK consortium

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

m_Gaussfaze=1
m_Gausssave=np.zeros((1,8*128))
dat=np.zeros((1,6))
m_GScale=1.0/30000000.0


def OnePlusOne(Ref_uint8, Flt_uint8, wonderful_list):
    commonfunctions=FaberOneplusoneCommonFunctions()
    
    m_CatchGetValueException = False
    m_MetricWorstPossibleValue = 0

    m_Maximize = FaberHyperParams.oneplusone_Maximize
    m_Epsilon = FaberHyperParams.oneplusone_Epsilon

    m_Initialized = False
    m_GrowthFactor = FaberHyperParams.oneplusone_GrowthFactor
    m_ShrinkFactor = FaberHyperParams.oneplusone_ShrinkFactor
    m_InitialRadius = FaberHyperParams.oneplusone_InitialRadius
    m_MaximumIteration = FaberHyperParams.oneplusone_MaximumIteration
    m_Stop = False
    m_CurrentCost = 0
    m_CurrentIteration = 0
    m_FrobeniusNorm = 0.0

    spaceDimension = 3 

    A = np.identity(spaceDimension)*(m_InitialRadius) 
    parent = np.zeros((2,3))
    estimate_initial(Ref_uint8, Flt_uint8, parent) 
    f_norm = np.zeros(spaceDimension)
    child = np.array(spaceDimension)
    delta = np.array(spaceDimension)
    
    parentPosition = np.array(spaceDimension)
    childPosition = np.array(spaceDimension)

    parentPosition=[parent[0][2],parent[1][2],parent[0][0]]
    pvalue = wonderful_list[0](wonderful_list[1],Ref_uint8,Flt_uint8,parent,wonderful_list[2],wonderful_list[3],\
        wonderful_list[4],wonderful_list[5],wonderful_list[6],wonderful_list[7],\
            wonderful_list[8],wonderful_list[9])

    m_CurrentIteration = 0
    
    for i in range (0,m_MaximumIteration):
        m_CurrentIteration=m_CurrentIteration+1
    
        for j in range (0, spaceDimension):
            f_norm[j]= commonfunctions.NormalVariateGenerator() 
    
        delta = A.dot(f_norm)#A * f_norm
        child = parentPosition + delta
        childPosition = to_matrix_blocked(child)
        cvalue = wonderful_list[0](wonderful_list[1],Ref_uint8,Flt_uint8,childPosition,wonderful_list[2],wonderful_list[3],\
            wonderful_list[4],wonderful_list[5],wonderful_list[6],wonderful_list[7],\
            wonderful_list[8],wonderful_list[9])

        adjust = m_ShrinkFactor
    
        if(m_Maximize):
            if(cvalue>pvalue):
                pvalue = cvalue
                child, parentPosition = parentPosition, child 
                adjust = m_GrowthFactor
            else:
                pass
        else:
            if(cvalue < pvalue):
                pvalue = cvalue
                child, parentPosition = parentPosition, child 
                adjust = m_GrowthFactor
            else:
                pass
                
            
        m_CurrentCost = pvalue
        m_FrobeniusNorm = np.linalg.norm(A,'fro')
    
        if(m_FrobeniusNorm <= m_Epsilon):
            break
    
        alpha = ((adjust - 1.0) / np.dot(f_norm, f_norm))
    
        for c in range(0, spaceDimension):
            for r in range(0,spaceDimension):
                A[r][c] += alpha * delta[r] * f_norm[c]

    return (parentPosition)  


def register_images(Ref_uint8, Flt_uint8, wonderful_list):

    Ref_uint8_ravel = Ref_uint8.ravel()

    optimal_params = OnePlusOne(Ref_uint8, Flt_uint8, wonderful_list)
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
        # Flt_uint8=cv2.normalize(Flt_img, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        start_time = time.time()
        final_img.append(register_images(Ref_uint8, Flt_uint8, wonderful_list))
        end_time= time.time()
        it_time = (end_time - start_time)
        times.append(it_time)
        t=t+it_time
        print("%d) --- %s seconds ---" % (c, it_time))

        #    
    df = pd.DataFrame([t, np.mean(times), np.std(times)],columns=['Test'+str(patient_id)])
    times_df = pd.DataFrame(times,columns=['Test'+str(patient_id)])
    
    df_path = os.path.join(curr_res,'Time_1+1_%02d.csv' % (t_id))
    times_df_path = os.path.join(curr_res,'Img_1+1_%02d.csv' % (t_id))

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

    
    hist_dim = 256
    t=0
    args = parser.parse_args()
    accel_number=args.thread_number

    patient_number=args.patient
    dim = args.image_dimension


    faber = Overlay(args.overlay)

    num_threads = accel_number

    if args.platform=='Zynq' :
        from pynq.ps import Clocks
        print("Previous Frequency "+str(Clocks.fclk0_mhz))
        Clocks.fclk0_mhz = args.clock
        print("New frequency "+str(Clocks.fclk0_mhz))
   
    print(args.config)
    print(args)

    #try:
    compute_wrapper(args, faber, num_threads, dim)
    #except Exception as e:
    #    print("An exception occurred: "+str(e))

        

    if args.platform =='Alveo':
        faber.free()

    print("Faber (1+1) python is at the end :)")



if __name__== "__main__":
    main()
