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
import pynq
import numpy as np
from faberNewFunctions import *
import faberNewFunctions

def faber_accel_map(programmable_logic=None, number_of_cores=1, metric=None, transform=None,image_dimension=512, caching=False, platform='Alveo', exponential=False):
        l=[]
        if (metric=="mi" or metric=="cc" or metric=="mse" or metric=="prz" ) and transform=="wax" :
            print("composite")
            return composite_accel_map(programmable_logic, number_of_cores, metric, transform, image_dimension, platform, exponential)
        elif metric=="mi" or metric=="cc" or metric=="mse" or metric=="prz":
            print("single")            
            return single_accel_map(programmable_logic, number_of_cores, metric, image_dimension, platform, exponential)
        elif transform=="wax" :
            print("wax only")
            return wax_accel_map(programmable_logic, number_of_cores, image_dimension, platform, exponential)
        else:
            print("Nope")
            return -1

def composite_accel_map(programmable_logic=None, number_of_cores=1, metric=None, transform=None,image_dimension=512, platform='Alveo', exponential=False):
    ########valid for a single wax :)
    # if more than one transformer we should redesign this
    if metric=="mi":
        return mi_composite_map(programmable_logic, number_of_cores,image_dimension, platform, exponential)
    elif metric=="prz":
        return prz_composite_map(programmable_logic, number_of_cores,image_dimension, platform, exponential)
    elif metric =="cc":
        return cc_composite_map(programmable_logic, number_of_cores,image_dimension, platform, exponential)
    else :
        return mse_composite_map(programmable_logic, number_of_cores,image_dimension, platform, exponential)

def single_accel_map(programmable_logic=None, number_of_cores=1, metric=None, image_dimension=512, platform='Alveo', exponential=False):
    if metric=="mi":
        return mi_map(programmable_logic, number_of_cores,image_dimension, platform, exponential)
    elif metric =="cc":
        return cc_map(programmable_logic, number_of_cores,image_dimension, platform, exponential)
    elif metric =="prz":
        return prz_map(programmable_logic, number_of_cores,image_dimension, platform, exponential)
    else :
        return mse_map(programmable_logic, number_of_cores,image_dimension, platform, exponential)

def append_useless(wonderful_list,number_of_useless_items):
    for i in range(number_of_useless_items):
        wonderful_list.append(str(i))
    return wonderful_list

##########################################

def mi_map(programmable_logic=None, number_of_cores=1, image_dimension=512, platform='Alveo', exponential=False):
    the_list_of_wonderful_lists=[]
    wonderful_list=[]
    mem_bank=None
    if number_of_cores >=1:
        if exponential:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_exp)
        else:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_negative)
        
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.mutual_information_master_1_1)
            mem_bank=programmable_logic.bank0
        else:
            wonderful_list.append(programmable_logic.mutual_information_master_0)
        faberNewFunctions.fill_wonderful_list_std_alone(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        append_useless(wonderful_list,1)
        wonderful_list.append(platform)
        append_useless(wonderful_list,4)

    if number_of_cores >=2:
        the_list_of_wonderful_lists.append(wonderful_list)
        wonderful_list=[]
        if exponential:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_exp)
        else:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_negative)
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.mutual_information_master_2_1)
            mem_bank=programmable_logic.bank1
        else:
            wonderful_list.append(programmable_logic.mutual_information_master_1)
        faberNewFunctions.fill_wonderful_list_std_alone(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        append_useless(wonderful_list,1)
        wonderful_list.append(platform)
        append_useless(wonderful_list,4)


    if number_of_cores >=3:
        the_list_of_wonderful_lists.append(wonderful_list)
        wonderful_list=[]
        if exponential:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_exp)
        else:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_negative)
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.mutual_information_master_3_1)
            mem_bank=programmable_logic.bank2
        else :
            wonderful_list.append(programmable_logic.mutual_information_master_2)
        faberNewFunctions.fill_wonderful_list_std_alone(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        append_useless(wonderful_list,1)
        wonderful_list.append(platform)
        append_useless(wonderful_list,4)

    if number_of_cores == 4:
        the_list_of_wonderful_lists.append(wonderful_list)
        wonderful_list=[]
        if exponential:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_exp)
        else:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_negative)
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.mutual_information_master_4_1)
            mem_bank=programmable_logic.bank3
        else:
            wonderful_list.append(programmable_logic.mutual_information_master_3)
        faberNewFunctions.fill_wonderful_list_std_alone(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        append_useless(wonderful_list,1)
        wonderful_list.append(platform)
        append_useless(wonderful_list,4)


    
    the_list_of_wonderful_lists.append(wonderful_list)
    return the_list_of_wonderful_lists

##########################################

def prz_map(programmable_logic=None, number_of_cores=1, image_dimension=512, platform='Alveo', exponential=False):
    the_list_of_wonderful_lists=[]
    wonderful_list=[]
    mem_bank=None
    if number_of_cores >=1:
        if exponential:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_exp)
        else:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_negative)
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.parzen_master_1_1)
            mem_bank=programmable_logic.bank0
        else:
            wonderful_list.append(programmable_logic.parzen_master_0)
        faberNewFunctions.fill_wonderful_list_std_alone(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        append_useless(wonderful_list,1)
        wonderful_list.append(platform)
        append_useless(wonderful_list,4)

    if number_of_cores >=2:
        the_list_of_wonderful_lists.append(wonderful_list)
        wonderful_list=[]
        if exponential:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_exp)
        else:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_negative)
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.parzen_master_2_1)
            mem_bank=programmable_logic.bank1
        else:
            wonderful_list.append(programmable_logic.parzen_master_1)
        faberNewFunctions.fill_wonderful_list_std_alone(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        append_useless(wonderful_list,1)
        wonderful_list.append(platform)
        append_useless(wonderful_list,4)


    if number_of_cores >=3:
        the_list_of_wonderful_lists.append(wonderful_list)
        wonderful_list=[]
        if exponential:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_exp)
        else:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_negative)
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.parzen_master_3_1)
            mem_bank=programmable_logic.bank2
        else :
            wonderful_list.append(programmable_logic.parzen_master_2)
        faberNewFunctions.fill_wonderful_list_std_alone(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        append_useless(wonderful_list,1)
        wonderful_list.append(platform)
        append_useless(wonderful_list,4)



    if number_of_cores == 4:
        the_list_of_wonderful_lists.append(wonderful_list)
        wonderful_list=[]
        if exponential:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_exp)
        else:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_negative)
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.parzen_master_4_1)
            mem_bank=programmable_logic.bank3
        else:
            wonderful_list.append(programmable_logic.parzen_master_3)
        faberNewFunctions.fill_wonderful_list_std_alone(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        append_useless(wonderful_list,1)
        wonderful_list.append(platform)
        append_useless(wonderful_list,4)


    
    the_list_of_wonderful_lists.append(wonderful_list)
    return the_list_of_wonderful_lists
##########################################

def cc_map(programmable_logic=None, number_of_cores=1, image_dimension=512, platform='Alveo', exponential=False):
    the_list_of_wonderful_lists=[]
    wonderful_list=[]
    mem_bank=None
    if number_of_cores >=1:    
        if exponential:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_exp)
        else:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_negative)
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.cross_correlation_master_1_1)
            mem_bank=programmable_logic.bank0
        else:
            wonderful_list.append(programmable_logic.cross_correlation_master_0)
        faberNewFunctions.fill_wonderful_list_std_alone(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        append_useless(wonderful_list,1)
        wonderful_list.append(platform)
        append_useless(wonderful_list,4)



    if number_of_cores >=2:
        the_list_of_wonderful_lists.append(wonderful_list)
        wonderful_list=[]
        if exponential:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_exp)
        else:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_negative)
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.cross_correlation_master_2_1)
            mem_bank=programmable_logic.bank1
        else:
            wonderful_list.append(programmable_logic.cross_correlation_master_1)
        faberNewFunctions.fill_wonderful_list_std_alone(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        append_useless(wonderful_list,1)
        wonderful_list.append(platform)
        append_useless(wonderful_list,4)


    if number_of_cores >=3:
        the_list_of_wonderful_lists.append(wonderful_list)
        wonderful_list=[]
        if exponential:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_exp)
        else:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_negative)
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.cross_correlation_master_3_1)
            mem_bank=programmable_logic.bank2
        else:
            wonderful_list.append(programmable_logic.cross_correlation_master_2)
        faberNewFunctions.fill_wonderful_list_std_alone(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        append_useless(wonderful_list,1)
        wonderful_list.append(platform)
        append_useless(wonderful_list,4)



    if number_of_cores == 4:
        the_list_of_wonderful_lists.append(wonderful_list)
        wonderful_list=[]
        if exponential:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_exp)
        else:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_negative)
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.cross_correlation_master_4_1)
            mem_bank=programmable_logic.bank3
        else:
            wonderful_list.append(programmable_logic.cross_correlation_master_3)
        faberNewFunctions.fill_wonderful_list_std_alone(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        append_useless(wonderful_list,1)
        wonderful_list.append(platform)
        append_useless(wonderful_list,4)



    the_list_of_wonderful_lists.append(wonderful_list)
    return the_list_of_wonderful_lists
##########################################

def mse_map(programmable_logic=None, number_of_cores=1, image_dimension=512, platform='Alveo', exponential=False):
    the_list_of_wonderful_lists=[]
    wonderful_list=[]
    mem_bank=None
    if number_of_cores >=1:
        if exponential:
            wonderful_list.append(faberNewFunctions.compute_hw_sm)
        else:
            wonderful_list.append(faberNewFunctions.compute_hw_sm)
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.mean_square_error_master_1_1)
            mem_bank=programmable_logic.bank0
        else:
            wonderful_list.append(programmable_logic.mean_square_error_master_0)
        faberNewFunctions.fill_wonderful_list_std_alone(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        append_useless(wonderful_list,1)
        wonderful_list.append(platform)
        append_useless(wonderful_list,4)



    if number_of_cores >=2:
        the_list_of_wonderful_lists.append(wonderful_list)
        wonderful_list=[]
        if exponential:
            wonderful_list.append(faberNewFunctions.compute_hw_sm)
        else:
            wonderful_list.append(faberNewFunctions.compute_hw_sm)
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.mean_square_error_master_2_1)
            mem_bank=programmable_logic.bank1
        else:
            wonderful_list.append(programmable_logic.mean_square_error_master_1)
        faberNewFunctions.fill_wonderful_list_std_alone(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        append_useless(wonderful_list,1)
        wonderful_list.append(platform)
        append_useless(wonderful_list,4)


    if number_of_cores >=3:
        the_list_of_wonderful_lists.append(wonderful_list)
        wonderful_list=[]
        if exponential:
            wonderful_list.append(faberNewFunctions.compute_hw_sm)
        else:
            wonderful_list.append(faberNewFunctions.compute_hw_sm)
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.mean_square_error_master_3_1)
            mem_bank=programmable_logic.bank2
        else:
            wonderful_list.append(programmable_logic.mean_square_error_master_2)
        faberNewFunctions.fill_wonderful_list_std_alone(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        append_useless(wonderful_list,1)
        wonderful_list.append(platform)
        append_useless(wonderful_list,4)



    if number_of_cores == 4:
        the_list_of_wonderful_lists.append(wonderful_list)
        wonderful_list=[]
        if exponential:
            wonderful_list.append(faberNewFunctions.compute_hw_sm)
        else:
            wonderful_list.append(faberNewFunctions.compute_hw_sm)
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.mean_square_error_master_4_1)
            mem_bank=programmable_logic.bank3
        else:
            wonderful_list.append(programmable_logic.mean_square_error_master_3)
        faberNewFunctions.fill_wonderful_list_std_alone(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        append_useless(wonderful_list,1)
        wonderful_list.append(platform)
        append_useless(wonderful_list,4)



    the_list_of_wonderful_lists.append(wonderful_list)
    return the_list_of_wonderful_lists



##########################################
##########################################
##########################################

def mi_composite_map(programmable_logic=None, number_of_cores=1, image_dimension=512, platform='Alveo', exponential=False):
    the_list_of_wonderful_lists=[]
    wonderful_list=[]
    mem_bank=None
    if number_of_cores >=1:
        if exponential:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_exp_composite)
        else:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_negative_composite)
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.wax_mi_accel_1_1)
            mem_bank=programmable_logic.bank0
        else:
            wonderful_list.append(programmable_logic.wax_mi_accel_0)
        faberNewFunctions.fill_wonderful_list_composite(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        wonderful_list.append(platform)
        append_useless(wonderful_list,3)
    if number_of_cores >=2:
        the_list_of_wonderful_lists.append(wonderful_list)
        wonderful_list=[]
        if exponential:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_exp_composite)
        else:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_negative_composite)
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.wax_mi_accel_2_1)
            mem_bank=programmable_logic.bank1
        else:
            wonderful_list.append(programmable_logic.wax_mi_accel_1)
        faberNewFunctions.fill_wonderful_list_composite(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        wonderful_list.append(platform)
        append_useless(wonderful_list,3)
    if number_of_cores >=3:
        the_list_of_wonderful_lists.append(wonderful_list)
        wonderful_list=[]
        if exponential:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_exp_composite)
        else:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_negative_composite)
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.wax_mi_accel_3_1)
            mem_bank=programmable_logic.bank2
        else :
            wonderful_list.append(programmable_logic.wax_mi_accel_2_1)
        faberNewFunctions.fill_wonderful_list_composite(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        wonderful_list.append(platform)
        append_useless(wonderful_list,3)
    if number_of_cores == 4:
        the_list_of_wonderful_lists.append(wonderful_list)
        wonderful_list=[]
        if exponential:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_exp_composite)
        else:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_negative_composite)
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.wax_mi_accel_4_1)
            mem_bank=programmable_logic.bank3
        else:
            wonderful_list.append(programmable_logic.wax_mi_accel_3)
        faberNewFunctions.fill_wonderful_list_composite(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        wonderful_list.append(platform)
        append_useless(wonderful_list,3)

    
    the_list_of_wonderful_lists.append(wonderful_list)
    return the_list_of_wonderful_lists

##########################################

def prz_composite_map(programmable_logic=None, number_of_cores=1, image_dimension=512, platform='Alveo', exponential=False):
    the_list_of_wonderful_lists=[]
    wonderful_list=[]
    mem_bank=None
    if number_of_cores >=1:
        if exponential:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_exp_composite)
        else:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_negative_composite)
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.wax_prz_accel_1_1)
            mem_bank=programmable_logic.bank0
        else:
            wonderful_list.append(programmable_logic.wax_prz_accel_0)
        faberNewFunctions.fill_wonderful_list_composite(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        wonderful_list.append(platform)
        append_useless(wonderful_list,3)



    if number_of_cores >=2:
        the_list_of_wonderful_lists.append(wonderful_list)
        wonderful_list=[]
        if exponential:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_exp_composite)
        else:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_negative_composite)
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.wax_prz_accel_2_1)
            mem_bank=programmable_logic.bank1
        else:
            wonderful_list.append(programmable_logic.wax_prz_accel_1)
        faberNewFunctions.fill_wonderful_list_composite(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        wonderful_list.append(platform)
        append_useless(wonderful_list,3)

    if number_of_cores >=3:
        the_list_of_wonderful_lists.append(wonderful_list)
        wonderful_list=[]
        if exponential:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_exp_composite)
        else:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_negative_composite)
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.wax_prz_accel_3_1)
            mem_bank=programmable_logic.bank2
        else :
            wonderful_list.append(programmable_logic.wax_prz_accel_2_1)
        faberNewFunctions.fill_wonderful_list_composite(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        wonderful_list.append(platform)
        append_useless(wonderful_list,3)



    if number_of_cores == 4:
        the_list_of_wonderful_lists.append(wonderful_list)
        wonderful_list=[]
        if exponential:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_exp_composite)
        else:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_negative_composite)
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.wax_prz_accel_4_1)
            mem_bank=programmable_logic.bank3
        else:
            wonderful_list.append(programmable_logic.wax_prz_accel_3)
        faberNewFunctions.fill_wonderful_list_composite(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        wonderful_list.append(platform)
        append_useless(wonderful_list,3)

    
    the_list_of_wonderful_lists.append(wonderful_list)
    return the_list_of_wonderful_lists
##########################################

def cc_composite_map(programmable_logic=None, number_of_cores=1, image_dimension=512, platform='Alveo', exponential=False):
    the_list_of_wonderful_lists=[]
    wonderful_list=[]
    mem_bank=None

    if number_of_cores >=1:
        if exponential:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_exp_composite)
        else:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_negative_composite)
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.wax_cc_accel_1_1)
            mem_bank=programmable_logic.bank0
        else:
            wonderful_list.append(programmable_logic.wax_cc_accel_0)
        faberNewFunctions.fill_wonderful_list_composite(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        wonderful_list.append(platform)
        append_useless(wonderful_list,3)


    if number_of_cores >=2:
        the_list_of_wonderful_lists.append(wonderful_list)
        wonderful_list=[]
        if exponential:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_exp_composite)
        else:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_negative_composite)
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.wax_cc_accel_2_1)
            mem_bank=programmable_logic.bank1
        else:
            wonderful_list.append(programmable_logic.wax_cc_accel_1)
        faberNewFunctions.fill_wonderful_list_composite(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        wonderful_list.append(platform)
        append_useless(wonderful_list,3)

    if number_of_cores >=3:
        the_list_of_wonderful_lists.append(wonderful_list)
        wonderful_list=[]
        if exponential:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_exp_composite)
        else:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_negative_composite)
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.wax_cc_accel_3_1)
            mem_bank=programmable_logic.bank2
        else:
            wonderful_list.append(programmable_logic.wax_cc_accel_2)
        faberNewFunctions.fill_wonderful_list_composite(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        wonderful_list.append(platform)
        append_useless(wonderful_list,3)



    if number_of_cores == 4:
        the_list_of_wonderful_lists.append(wonderful_list)
        wonderful_list=[]
        if exponential:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_exp_composite)
        else:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_negative_composite)
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.wax_cc_accel_4_1)
            mem_bank=programmable_logic.bank3
        else:
            wonderful_list.append(programmable_logic.wax_cc_accel_3)
        faberNewFunctions.fill_wonderful_list_composite(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        wonderful_list.append(platform)
        append_useless(wonderful_list,3)


    the_list_of_wonderful_lists.append(wonderful_list)
    return the_list_of_wonderful_lists
##########################################

def mse_composite_map(programmable_logic=None, number_of_cores=1, image_dimension=512, platform='Alveo', exponential=False):
    the_list_of_wonderful_lists=[]
    wonderful_list=[]
    mem_bank=None
    if number_of_cores >=1:
        if exponential:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_composite)
        else:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_composite)
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.wax_mse_accel_1_1)
            mem_bank=programmable_logic.bank0
        else:
            wonderful_list.append(programmable_logic.wax_mse_accel_0)
        faberNewFunctions.fill_wonderful_list_composite(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        wonderful_list.append(platform)
        append_useless(wonderful_list,3)



    if number_of_cores >=2:
        the_list_of_wonderful_lists.append(wonderful_list)
        wonderful_list=[]
        if exponential:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_composite)
        else:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_composite)
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.wax_mse_accel_2_1)
            mem_bank=programmable_logic.bank1
        else:
            wonderful_list.append(programmable_logic.wax_mse_accel_1)
        faberNewFunctions.fill_wonderful_list_composite(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        wonderful_list.append(platform)
        append_useless(wonderful_list,3)


    if number_of_cores >=3:
        the_list_of_wonderful_lists.append(wonderful_list)
        wonderful_list=[]
        if exponential:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_composite)
        else:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_composite)
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.wax_mse_accel_3_1)
            mem_bank=programmable_logic.bank2
        else:
            wonderful_list.append(programmable_logic.wax_mse_accel_2)
        faberNewFunctions.fill_wonderful_list_composite(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        wonderful_list.append(platform)
        append_useless(wonderful_list,3)



    if number_of_cores == 4:
        the_list_of_wonderful_lists.append(wonderful_list)
        wonderful_list=[]
        if exponential:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_composite)
        else:
            wonderful_list.append(faberNewFunctions.compute_hw_sm_composite)
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.wax_mse_accel_4_1)
            mem_bank=programmable_logic.bank3
        else:
            wonderful_list.append(programmable_logic.wax_mse_accel_3)
        faberNewFunctions.fill_wonderful_list_composite(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        wonderful_list.append(platform)
        append_useless(wonderful_list,3)



    the_list_of_wonderful_lists.append(wonderful_list)
    return the_list_of_wonderful_lists

##########################################
##########################################
##########################################

def wax_accel_map(programmable_logic=None, number_of_cores=1, image_dimension=512, platform='Alveo', exponential=False):

    the_list_of_wonderful_lists=[]
    wonderful_list=[]
    mem_bank=None
    if number_of_cores >=1:
        wonderful_list.append(faberNewFunctions.compute_hw_wax)
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.xf_warp_transform_accel_1_1)
            mem_bank=programmable_logic.bank0
        else:
            wonderful_list.append(programmable_logic.xf_warp_transform_accel_0)
        faberNewFunctions.fill_wonderful_list_wax_only(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        wonderful_list.append(platform)
        append_useless(wonderful_list,4)
    
    if number_of_cores >=2:
        wonderful_list.append(faberNewFunctions.compute_hw_wax)
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.xf_warp_transform_accel_2_1)
            mem_bank=programmable_logic.bank0
        else:
            wonderful_list.append(programmable_logic.xf_warp_transform_accel_1)
        faberNewFunctions.fill_wonderful_list_wax_only(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        wonderful_list.append(platform)
        append_useless(wonderful_list,4)
    if number_of_cores >=3:
        wonderful_list.append(faberNewFunctions.compute_hw_wax)
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.xf_warp_transform_accel_3_1)
            mem_bank=programmable_logic.bank0
        else:
            wonderful_list.append(programmable_logic.xf_warp_transform_accel_2)
        faberNewFunctions.fill_wonderful_list_wax_only(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        wonderful_list.append(platform)
        append_useless(wonderful_list,4)
    if number_of_cores >=4:
        wonderful_list.append(faberNewFunctions.compute_hw_wax)
        if platform =='Alveo':
            wonderful_list.append(programmable_logic.xf_warp_transform_accel_4_1)
            mem_bank=programmable_logic.bank0
        else:
            wonderful_list.append(programmable_logic.xf_warp_transform_accel_3)
        faberNewFunctions.fill_wonderful_list_wax_only(size_single=image_dimension, \
            faber_pl=programmable_logic, mem_bank=mem_bank,\
            wonderful_list=wonderful_list)
        wonderful_list.append(platform)
        append_useless(wonderful_list,4)
    the_list_of_wonderful_lists.append(wonderful_list)
    return the_list_of_wonderful_lists