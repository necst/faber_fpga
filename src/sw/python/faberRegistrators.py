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
from scipy import signal
import math


class FaberGenericComponent(object):
    """docstring for FaberGeneric"""
    def __init__(self, ref_size=512, metric="mi", transform="wax", exponential=True, interpolation=cv2.INTER_NEAREST):
        object.__init__(self)
        self.ref_entropy = 0
        self.ref_size=ref_size
        self.metric=metric
        self.similarity_function=None
        self.transform=transform
        self.exponential=exponential
        self.interpolation=interpolation
        self.map_similarity_function()
        self.similarity_function_sw=self.similarity_function
        self.AP_CTRL = 0x00
        self.done_rdy = 0x6
        self.ap_start = 0x1
        self.LOAD_IMG = 0
        self.COMPUTE = 1   

    def map_similarity_function(self):
        if self.metric == "mi":
            if self.exponential == True:
                self.similarity_function=self.compute_mi_exponential_sw
            else:
                self.similarity_function=self.mutual_info_sw
        elif self.metric == "prz":
            if self.exponential == True:
                self.similarity_function=self.compute_parzen_mi_exponential
            else:
                self.similarity_function=self.parzen_mi     
        elif self.metric == "cc":
            self.similarity_function=self.cross_correlation_np
        elif self.metric == "mse":
            self.similarity_function=self.mean_squared_error_np
        else:
            self.similarity_function=self.mutual_info_sw

    def compute_entropy(self, histogram):
        histogram=histogram[np.where(histogram>0.000000000000001)]
        entropy=(np.sum(histogram*(np.log2(histogram))))*-1
        return entropy

    def reint_entropy(self):
        self.ref_entropy = 0

    def mutual_info_sw(self, Ref_uint8, Flt_uint8,dim=512):
        ref_ravel=Ref_uint8.ravel()
        dim=ref_ravel.shape
        j_h=np.histogram2d(ref_ravel,Flt_uint8.ravel(),bins=[256,256])[0]
        j_h=j_h/(dim)
          
        j_h1=j_h[np.where(j_h>0.000000000000001)]
        entropy=(np.sum(j_h1*np.log2(j_h1)))*-1

        href=np.sum(j_h,axis=0)
        hflt=np.sum(j_h,axis=1)     
        if self.ref_entropy==0:
            eref=self.compute_entropy(href)
        else:
            eref=self.ref_entropy

        eflt=self.compute_entropy(hflt)

        mutualinfo=eref+eflt-entropy

        return(mutualinfo)

    def warpAffine(self,image, params):
        return cv2.warpAffine(image,params,np.shape(image),flags=self.interpolation)

    def mean_squared_error_np(self, fixed, moving):
        fixed_ravel=fixed.ravel()
        moving_ravel=moving.ravel()
        gne=np.longdouble(fixed_ravel)
        gnki=np.longdouble(moving_ravel)
        diff=np.subtract(gne,gnki)
        prod=np.multiply(diff,diff)
        summer=np.sum(prod)
        return summer/(512*512)
    def cross_correlation_np(self, fixed, moving):
        fixed_ravel=fixed.ravel().astype(np.double)
        moving_ravel=moving.ravel().astype(np.double)
        m1=np.multiply(fixed_ravel,moving_ravel)
        m2=np.multiply(fixed_ravel,fixed_ravel)
        m3=np.multiply(moving_ravel,moving_ravel)
        prod=np.sum(m1)
        sq_mvng=np.sum(m2)
        sq_fx=np.sum(m3)
        return -(prod/np.sqrt(sq_mvng*sq_fx))
    def parzen_mi(self, fixed, moving, bin=256, padding=False):
        n_bins = bin
        omega = np.array([[1 / 6, 2 / 3, 1 / 6]])
        omega_prime = -np.array([[1 / 2, 0, -1 / 2]])
        filter = np.dot(omega.transpose(), omega)
        filter_prime = np.dot(omega_prime.transpose(), omega)
        filter_prime_sum = np.sum(filter_prime)
        filter_prime_j = omega_prime.transpose() * np.sum(omega)
        pad_size=0
        if padding:
            pad_size = omega.size//2

        epsilon= np.finfo(np.float64).tiny
        #end of init
        count_matrix = np.zeros((n_bins, n_bins))
        fixed_clipped = np.clip(fixed, 0, n_bins-1)
        moving_clipped = np.clip(moving, 0, n_bins-1)
        for f, m in zip(
            fixed_clipped.flatten().astype(int), moving_clipped.flatten().astype(int)
        ):
            count_matrix[m, f] += 1

        if pad_size > 0:
            count_matrix = np.pad(count_matrix, pad_size)

        prob_matrix = signal.correlate2d(count_matrix, filter, "same")

        prob_matrix /= fixed_clipped.size

        prob_k = np.sum(prob_matrix, axis=0)
        prob_j = np.sum(prob_matrix, axis=1)

        logs = np.zeros((n_bins + pad_size*2, n_bins + pad_size*2))
        for j in range(n_bins + pad_size*2):
            for k in range(n_bins + pad_size*2):
                denom = prob_j[j] * prob_k[k]
                if denom == 0:
                    denom = epsilon
                num = prob_matrix[j, k]
                if num == 0:
                    num = epsilon
                frac = num / denom
                logs[j, k] = math.log(frac)

        res = 0

        for j in range(n_bins + pad_size*2):
            for k in range(n_bins + pad_size*2):
                res += prob_matrix[j, k] * logs[j, k]

        result = -res

        return result


    def compute_mi_exponential_sw(self,ref,flt):
        return np.exp(-self.mutual_info_sw(ref,flt))

    def compute_parzen_mi_exponential(self,ref,flt):
        return np.exp(-self.parzen_mi(ref,flt))

    def compute_metric(self,ref,flt,params):
        flt_tx=self.warpAffine(flt, params)
        return self.similarity_function(ref,flt_tx)

    def fill_buff1_img(self,image):
        pass

##################################################
##################################################
##################################################
##################################################
##################################################
##################################################
##################################################
##################################################
##################################################
##################################################
