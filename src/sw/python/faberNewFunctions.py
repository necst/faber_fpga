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
import numpy as np
import cv2
import pynq
from pynq import allocate
import numpy as np
import cv2
import struct

AP_CTRL = 0x00
done_rdy = 0x6
ap_start = 0x1
AP_REF_ADDR = 0x10
AP_FLT_ADDR_OR_MI = 0x18
AP_MI_ADDR_OR_FUNCT = 0x20

def fix_wax_reference_system(params):
    params[0][2]=-params[0][2]
    params[1][2]=-params[1][2]

    params[0][1]=-params[0][1]
    params[1][0]=-params[1][0]
    return params

def execute_zynq(target_accel):
    target_accel.write(AP_CTRL, ap_start)
    while(target_accel.mmio.read(0) & 0x4 != 0x4):
        pass

def fill_buff(my_buffer,data):
    my_buffer[:] = data.ravel()
    my_buffer.flush()

def fill_two_buff(my_buffer1,my_buffer2,data1,data2):
    my_buffer1[:] = data1.ravel()
    my_buffer2[:] = data2.ravel()
    my_buffer1.flush()
    my_buffer2.flush()

def fill_three_buff(my_buffer1,my_buffer2,my_buffer3,data1,data2,data3):
    my_buffer1[:] = data1.ravel()
    my_buffer2[:] = data2.ravel()
    my_buffer3[:] = data3.ravel()
    my_buffer1.flush()
    my_buffer2.flush()
    my_buffer3.flush()

def read_buff(my_buffer, my_list):
    my_buffer.invalidate()
    my_list.append(my_buffer)

def write_axilite(target_accel,trgt_addres,trgt_data):
    target_accel.write(trgt_addres, trgt_data)

def execute_signature_zynq_std_alone(target_accel,in1_vadd,in2_vadd,out0):
    write_axilite(target_accel,AP_REF_ADDR,in1_vadd.device_address)
    write_axilite(target_accel,AP_FLT_ADDR_OR_MI,in2_vadd.device_address)
    write_axilite(target_accel,AP_MI_ADDR_OR_FUNCT,out0.device_address)
    execute_zynq(target_accel)


def compute_hw_sm_exp(target_accel,ref,flt,params,in1_vadd,in2_vadd,out0,useless,platform,useless2,useless3,useless4):
    transformed=cv2.warpAffine(flt,params,np.shape(flt),flags=cv2.INTER_NEAREST)
    fill_two_buff(in1_vadd,in2_vadd,ref,transformed)
    if platform != "Zynq":
        target_accel.call(in1_vadd,in2_vadd,out0)
    else:
        execute_signature_zynq_std_alone(target_accel,in1_vadd,in2_vadd,out0)

    out0.invalidate()
    data = struct.pack('d',out0)
    val=struct.unpack('d',data)
    mi = val[0]
    mi_exp = np.exp(-mi)
    return mi_exp


def compute_hw_sm_exp_positive(target_accel,ref,flt,params,in1_vadd,in2_vadd,out0,useless,platform,useless2,useless3,useless4):
    transformed=cv2.warpAffine(flt,params,np.shape(flt),flags=cv2.INTER_NEAREST)
    fill_two_buff(in1_vadd,in2_vadd,ref,transformed)
    if platform != "Zynq":
        target_accel.call(in1_vadd,in2_vadd,out0)
    else:
        execute_signature_zynq_std_alone(target_accel,in1_vadd,in2_vadd,out0)

    out0.invalidate()
    data = struct.pack('d',out0)
    val=struct.unpack('d',data)
    mi = val[0]
    mi_exp = np.exp(mi)
    return mi_exp


def compute_hw_sm(target_accel,ref,flt,params,in1_vadd,in2_vadd,out0,useless,platform,useless2,useless3,useless4):
    transformed=cv2.warpAffine(flt,params,np.shape(flt),flags=cv2.INTER_NEAREST)
    fill_two_buff(in1_vadd,in2_vadd,ref,transformed)
    if platform != "Zynq":
        target_accel.call(in1_vadd,in2_vadd,out0)
    else:
        execute_signature_zynq_std_alone(target_accel,in1_vadd,in2_vadd,out0)
    out0.invalidate()
    data = struct.pack('d',out0)
    val=struct.unpack('d',data)
    mi = val[0]
    return mi


def compute_hw_sm_negative(target_accel,ref,flt,params,in1_vadd,in2_vadd,out0,useless,platform,useless2,useless3,useless4):
    transformed=cv2.warpAffine(flt,params,np.shape(flt),flags=cv2.INTER_NEAREST)
    fill_two_buff(in1_vadd,in2_vadd,ref,transformed)
    if platform != "Zynq":
        target_accel.call(in1_vadd,in2_vadd,out0)
    else:
        execute_signature_zynq_std_alone(target_accel,in1_vadd,in2_vadd,out0)
    out0.invalidate()
    data = struct.pack('d',out0)
    val=struct.unpack('d',data)
    mi = val[0]
    return -mi


def fill_wonderful_list_std_alone(size_single=512, faber_pl=None, mem_bank=None,wonderful_list=None):

    in1_vadd = pynq.allocate((size_single * size_single), np.uint8,mem_bank)
    in2_vadd = pynq.allocate((size_single * size_single), np.uint8,mem_bank)
    out0 = pynq.allocate((1), np.float32,mem_bank)
    wonderful_list.append(in1_vadd)
    wonderful_list.append(in2_vadd)
    wonderful_list.append(out0)


######################################


AP_TRANSFORM_ADDR=0x28
AP_ROWS_ADDR=0x30
AP_COLS_ADDR=0x38
def execute_signature_zynq_composite(target_accel,in1_vadd,in2_vadd,out0,in3_vadd,rows,cols):
    write_axilite(target_accel,AP_REF_ADDR,in1_vadd.device_address)
    write_axilite(target_accel,AP_FLT_ADDR_OR_MI,in2_vadd.device_address)
    write_axilite(target_accel,AP_MI_ADDR_OR_FUNCT,out0.device_address)
    write_axilite(target_accel,AP_TRANSFORM_ADDR,in3_vadd.device_address)
    write_axilite(target_accel,AP_ROWS_ADDR,rows)
    write_axilite(target_accel,AP_COLS_ADDR,cols)
    execute_zynq(target_accel)

def compute_hw_sm_exp_composite(target_accel,ref,flt,params,in1_vadd,in2_vadd,in3_vadd,\
    out0, rows, cols, platform,useless):
    fill_two_buff(in1_vadd,in2_vadd,ref,flt)
    params=fix_wax_reference_system(params)
    in3_vadd[:6] = params.ravel()
    in3_vadd[6:9]=np.zeros((3))
    in3_vadd.flush()
    if platform != "Zynq":
        target_accel.call(in2_vadd,in1_vadd,out0, in3_vadd, rows, cols)
    else:
        execute_signature_zynq_composite(target_accel,in2_vadd,in1_vadd,out0,in3_vadd,rows,cols)
    out0.invalidate()
    data = struct.pack('d',out0)
    val=struct.unpack('d',data)
    mi = val[0]
    mi_exp = np.exp(-mi)
    return mi_exp


def compute_hw_sm_exp_positive_composite(target_accel,ref,flt,params,in1_vadd,in2_vadd,in3_vadd,\
    out0, rows, cols, platform,useless):
    fill_two_buff(in1_vadd,in2_vadd,ref,flt)
    params=fix_wax_reference_system(params)
    in3_vadd[:6] = params.ravel()
    in3_vadd[6:9]=np.zeros((3))
    in3_vadd.flush()
    if platform != "Zynq":
        target_accel.call(in2_vadd,in1_vadd,out0, in3_vadd, rows, cols)
    else:
        execute_signature_zynq_composite(target_accel,in2_vadd,in1_vadd,out0,in3_vadd,rows,cols)
    out0.invalidate()
    data = struct.pack('d',out0)
    val=struct.unpack('d',data)
    mi = val[0]
    mi_exp = np.exp(mi)
    return mi_exp




def compute_hw_sm_composite(target_accel,ref,flt,params,in1_vadd,in2_vadd,in3_vadd,\
    out0, rows, cols,platform,useless):

    fill_two_buff(in1_vadd,in2_vadd,ref,flt)
    params=fix_wax_reference_system(params)

    in3_vadd[:6] = params.ravel()
    in3_vadd[6:9]=np.zeros((3))
    in3_vadd.flush()
    if platform != "Zynq":
        target_accel.call(in2_vadd,in1_vadd,out0, in3_vadd, rows, cols)
    else:
        execute_signature_zynq_composite(target_accel,in2_vadd,in1_vadd,out0,in3_vadd,rows,cols)
    out0.invalidate()
    data = struct.pack('d',out0)
    val=struct.unpack('d',data)
    mi = val[0]
    return mi

def compute_hw_sm_negative_composite(target_accel,ref,flt,params,in1_vadd,in2_vadd,in3_vadd,\
    out0, rows, cols,platform,useless):
    fill_two_buff(in1_vadd,in2_vadd,ref,flt)
    params=fix_wax_reference_system(params)

    in3_vadd[:6] = params.ravel()
    in3_vadd[6:9]=np.zeros((3))
    in3_vadd.flush()
    if platform != "Zynq":
        target_accel.call(in2_vadd,in1_vadd,out0, in3_vadd, rows, cols)
    else:
        execute_signature_zynq_composite(target_accel,in2_vadd,in1_vadd,out0,in3_vadd,rows,cols)
    out0.invalidate()
    data = struct.pack('d',out0)
    val=struct.unpack('d',data)
    mi = val[0]
    return -mi





def fill_wonderful_list_composite(size_single=512, faber_pl=None, mem_bank=None, wonderful_list=None):
    if mem_bank==None:
        target_allocate=None
    else:
        target_allocate=mem_bank

    in1_vadd = pynq.allocate((size_single * size_single), np.uint8,target_allocate)
    in2_vadd = pynq.allocate((size_single * size_single), np.uint8,target_allocate)
    in3_vadd = pynq.allocate(9, np.float32,mem_bank)
    out0 = pynq.allocate((1), np.float32,mem_bank)

    wonderful_list.append(in1_vadd)
    wonderful_list.append(in2_vadd)
    wonderful_list.append(in3_vadd)
    wonderful_list.append(out0)
    wonderful_list.append(size_single)
    wonderful_list.append(size_single)

######################################
AP_WAX_IN_IMG_ADDR=AP_REF_ADDR #0x10
AP_WAX_TRANSFORM_MATRIX_ADDR=0x18
AP_WAX_OUT_IMG_ADDR=0x20
AP_WAX_ROWS_ADDR = 0x28
AP_WAX_COLS_ADDR = 0x30

def execute_signature_zynq_wax(target_accel,in1_vadd,in2_vadd,out0,rows,cols):
    write_axilite(target_accel,AP_WAX_IN_IMG_ADDR,in1_vadd.device_address)
    write_axilite(target_accel,AP_WAX_TRANSFORM_MATRIX_ADDR,in2_vadd.device_address)
    write_axilite(target_accel,AP_WAX_OUT_IMG_ADDR,out0.device_address)
    write_axilite(target_accel,AP_WAX_ROWS_ADDR,rows)
    write_axilite(target_accel,AP_WAX_COLS_ADDR,cols)
    execute_zynq(target_accel)

def compute_hw_wax(target_accel,flt,params,in1_vadd,in2_vadd,\
    out0, rows, cols, platform, useless, useless2):
    fill_buff(in1_vadd, flt)
    params=fix_wax_reference_system(params)
    in2_vadd[:6] = params.ravel()
    in2_vadd[6:9]= np.zeros((3))
    in2_vadd.flush()
    if platform != "Zynq":
        target_accel.call(in1_vadd,in2_vadd,out0, rows, cols)
    else:
        execute_signature_zynq_wax(target_accel,in1_vadd,in2_vadd,out0,rows,cols)
    out0.invalidate()
    hw_res = out0.reshape(rows,cols)
    return hw_res


def fill_wonderful_list_wax_only(size_single=512, faber_pl=None, mem_bank=None, wonderful_list=None):
    if mem_bank==None:
        target_allocate=None
    else:
        target_allocate=mem_bank

    in1_vadd = pynq.allocate((size_single * size_single), np.uint8,target_allocate)
    in2_vadd = pynq.allocate(9, np.float32,mem_bank)
    out0 = pynq.allocate((size_single * size_single), np.uint8,target_allocate)

    wonderful_list.append(in1_vadd)
    wonderful_list.append(in2_vadd)
    wonderful_list.append(out0)
    wonderful_list.append(size_single)
    wonderful_list.append(size_single)