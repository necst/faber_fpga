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

import cv2
import numpy as np
import math
import pydicom

class FaberHyperParams:
    
    oneplusone_Maximize = False
    oneplusone_Epsilon = 1.5e-4
    oneplusone_GrowthFactor = 1.05
    oneplusone_ShrinkFactor = np.power(oneplusone_GrowthFactor, -0.25)
    oneplusone_InitialRadius = 1.01
    oneplusone_MaximumIteration = 100

    gss_optimaze_ths=0.005
    powell_optimize_eps=0.000005
    powell_rng_1=80.0
    powell_rng_2=80.0
    powell_rng_3=1.0
		
def estimate_initial(Ref_uint8,Flt_uint8, params):
    ref_mom =cv2.moments(Ref_uint8)
    flt_mom = cv2.moments(Flt_uint8)

    flt_avg_10 = flt_mom['m10']/flt_mom['m00']
    flt_avg_01 = flt_mom['m01']/flt_mom['m00']
    flt_mu_20 = (flt_mom['m20']/flt_mom['m00']*1.0)-(flt_avg_10*flt_avg_10)
    flt_mu_02 = (flt_mom['m02']/flt_mom['m00']*1.0)-(flt_avg_01*flt_avg_01)
    flt_mu_11 = (flt_mom['m11']/flt_mom['m00']*1.0)-(flt_avg_01*flt_avg_10)

    ref_avg_10 = ref_mom['m10']/ref_mom['m00']
    ref_avg_01 = ref_mom['m01']/ref_mom['m00']
    ref_mu_20 = (ref_mom['m20']/ref_mom['m00']*1.0)-(ref_avg_10*ref_avg_10)
    ref_mu_02 = (ref_mom['m02']/ref_mom['m00']*1.0)-(ref_avg_01*ref_avg_01)
    ref_mu_11 = (ref_mom['m11']/ref_mom['m00']*1.0)-(ref_avg_01*ref_avg_10)

    params[0][2] = ref_mom['m10']/ref_mom['m00']-flt_mom['m10']/flt_mom['m00']
    params[1][2] = ref_mom['m01']/ref_mom['m00'] - flt_mom['m01']/flt_mom['m00']


    rho_flt=0.5*math.atan((2.0*flt_mu_11)/(flt_mu_20-flt_mu_02))
    rho_ref=0.5*math.atan((2.0*ref_mu_11)/(ref_mu_20-ref_mu_02))
    delta_rho=rho_ref-rho_flt

    roundness=(flt_mom['m20']/flt_mom['m00']) / (flt_mom['m02']/flt_mom['m00'])
    if math.fabs(roundness-1.0)>=0.3:
        params[0][0]= math.cos(delta_rho)
        params[0][1] = -math.sin(delta_rho)
        params[1][0] = math.sin(delta_rho)
        params[1][1] = math.cos(delta_rho)
    else:
        params[0][0]= 1.0
        params[0][1] = 0.0
        params[1][0] = 0.0
        params[1][1] = 1.0

    #print(params)
    return params

def transform(image, par):
    out = cv2.warpAffine(image,par,np.shape(image))
    return(out)

def read_and_prepare_dicom_ref_flt_pair(ref_path,flt_path,dim):
        ref = pydicom.dcmread(ref_path)
        Ref_img = ref.pixel_array
        Ref_img[Ref_img==-2000]=1

        flt = pydicom.dcmread(flt_path)
        img = flt.pixel_array

        Flt_img = cv2.resize(img, dsize=(dim, dim))

        Ref_uint8=cv2.normalize(Ref_img, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        Flt_uint8=cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        return Ref_uint8, Flt_uint8

def turnaindre(vec):
    mat=np.zeros((2,3))
    mat[0][0]=vec[2]
    mat[0][1]=vec[3]
    mat[0][2]=vec[0]
    mat[1][0]=vec[4]
    mat[1][1]=vec[5]
    mat[1][2]=vec[1]
    return (mat)


def to_matrix(vector_params):
    mat_params=np.zeros((2,3))
    mat_params[0][0]=vector_params[0]
    mat_params[0][1]=vector_params[1]
    mat_params[0][2]=vector_params[2]
    mat_params[1][0]=vector_params[3]
    mat_params[1][1]=vector_params[4]
    mat_params[1][2]=vector_params[5]
    return (mat_params)

def to_matrix_blocked(vector_params):
    mat_params=np.zeros((2,3))
    mat_params[0][2]=vector_params[0]
    mat_params[1][2]=vector_params[1]
    if vector_params[2] > 1 or vector_params[2] < -1:
        mat_params[0][0]=1 #cos_teta
        mat_params[1][1]=1 #cos_teta
        mat_params[0][1]=0
        mat_params[1][0]=0
    else:
        mat_params[0][0]=vector_params[2] #cos_teta
        mat_params[1][1]=vector_params[2] #cos_teta
        mat_params[0][1]=np.sqrt(1-(vector_params[2]**2))
        mat_params[1][0]=-mat_params[0][1]
    return (mat_params)

def save_data(final_img,list_name,res_path):
    for i in range(len(final_img)):
        b=list_name[i].split('/')
        c=b.pop()
        d=c.split('.')
        cv2.imwrite(res_path+'/'+d[0][0:2]+str(int(d[0][2:5])+1)+'.png', final_img[i])

def analyzeDiff(imageA, imageB, threshold):
    res=np.abs(imageA - imageB)
    #--- convert the result to integer type ---
    res = res.astype(np.uint8)
    #--- find percentage difference based on number of pixels that are not zero ---
    percentage = (np.sum(res>threshold) * 100)/ res.size
    return percentage


class FaberOneplusoneCommonFunctions(object):
    """docstring for FaberOneplusoneCommonFunctions"""
    def __init__(self):
        object.__init__(self)
        self.m_Gaussfaze=1
        self.m_Gausssave=np.zeros((1,8*128))
        self.dat=np.zeros((1,6))
        self.m_GScale=1.0/30000000.0
    

    def NormalVariateGenerator(self):

        self.m_Gaussfaze = self.m_Gaussfaze-1
        if (self.m_Gaussfaze):
            return self.m_GScale * self.m_Gausssave[self.m_Gaussfaze]
        else:
            return self.FastNorm()



    def SignedShiftXOR(self,x):
        uirs = np.uint32(x)
        c=np.int32((uirs << 1) ^ 333556017) if np.int32(x <= 0) else np.int32(uirs << 1)
        return c



    def FastNorm(self):
        m_Scale = 30000000.0
        m_Rscale = 1.0 / m_Scale
        m_Rcons = 1.0 / (2.0 * 1024.0 * 1024.0 * 1024.0)
        m_ELEN = 7  #LEN must be 2 ** ELEN  
        m_LEN = 128
        m_LMASK = (4 * (m_LEN - 1))
        m_TLEN = (8 * m_LEN)
        m_Vec1 = np.zeros(m_TLEN)
        m_Lseed = 12345
        m_Irs = 12345
        self.m_GScale = m_Rscale
        fake = 1.0 + 0.125 / m_TLEN
        m_Chic2 = np.sqrt(2.0 * m_TLEN - fake * fake) / fake
        m_Chic1 = fake * np.sqrt(0.5 / m_TLEN)
        m_ActualRSD = 0.0
        inc = 0
        mask = 0
        m_Nslew = 0
        if (not(m_Nslew & 0xFF)):
            if (m_Nslew & 0xFFFF):
                print('Vado a recalcsumsq')
            else:
                ts = 0.0
                p = 0
                while(True):
                    while(True):
                        m_Lseed = np.int32(69069 * np.int64(m_Lseed) + 33331)
                        m_Irs = np.int64(self.SignedShiftXOR(m_Irs))
                        r = np.int32((m_Irs)+ np.int64(m_Lseed))
                        tx = m_Rcons * r
                        m_Lseed = np.int32(69069 * np.int64(m_Lseed) + 33331)
                        m_Irs = np.int64(self.SignedShiftXOR(m_Irs))
                        r = np.int32((m_Irs) + np.int64(m_Lseed))
                        ty = m_Rcons * r
                        tr = tx * tx + ty * ty
                        if ((tr <= 1.0) and (tr >= 0.1)):
                            break
                    m_Lseed = np.int32(69069 * np.int64(m_Lseed) + 33331)
                    m_Irs = np.int64(self.SignedShiftXOR(m_Irs))
                    r = np.int32((m_Irs) + np.int64(m_Lseed))
                    if (r < 0):
                        r = ~r
                    tz = -2.0 * np.log((r + 0.5) * m_Rcons)
                    ts += tz
                    tz = np.sqrt(tz / tr)
                    m_Vec1[p] = (int)(m_Scale * tx * tz)
                    p=p+1
                    m_Vec1[p] = (int)(m_Scale * ty * tz)
                    p=p+1
                    if (p >= m_TLEN):
                        break
                ts = m_TLEN / ts
                tr = np.sqrt(ts)
                for p in range(0, m_TLEN):
                    tx = m_Vec1[p] * tr
                    m_Vec1[p]= int(tx - 0.5) if int(tx < 0.0) else int(tx + 0.5)
                ts = 0.0
                for p in range(0,m_TLEN):
                    tx = m_Vec1[p]
                    ts += (tx * tx)
                ts = np.sqrt(ts / (m_Scale * m_Scale * m_TLEN))
                m_ActualRSD = 1.0 / ts
                m_Nslew=m_Nslew+1
                self.m_Gaussfaze = m_TLEN - 1
                m_Lseed = np.int32(69069 * np.int64(m_Lseed) + 33331)
                m_Irs = np.int64(self.SignedShiftXOR(m_Irs))
                t = np.int32((m_Irs) + np.int64(m_Lseed))
                if (t < 0):
                    t = ~t
                t = t >> (29 - 2 * m_ELEN)
                skew = (m_LEN - 1) & t
                t = t >> m_ELEN
                skew = 4 * skew
                stride = int((m_LEN / 2 - 1)) & t
                t = t >> (m_ELEN - 1)
                stride = 8 * stride + 4
                mtype = t & 3
                stype = m_Nslew & 3
                if(stype==1):
                    inc = 1
                    mask = m_LMASK
                    pa = m_Vec1[4 * m_LEN]
                    pa_idx = 4 * m_LEN
                    pb = m_Vec1[4 * m_LEN + m_LEN]
                    pb_idx = 4 * m_LEN + m_LEN
                    pc = m_Vec1[4 * m_LEN + 2 * m_LEN]
                    pc_idx = 4 * m_LEN + 2 * m_LEN
                    pd = m_Vec1[4 * m_LEN + 3 * m_LEN]
                    pd_idx = 4 * m_LEN + 3 * m_LEN
                    p0 = m_Vec1[0]
                    p0_idx = 0
                    self.m_Gausssave = m_Vec1
                    i = m_LEN
                    pb = m_Vec1[4 * m_LEN + m_LEN + (inc * (m_LEN - 1))]
                    pb_idx = 4 * m_LEN + m_LEN + (inc * (m_LEN - 1))
                    while(True):
                        skew = (skew + stride) & mask
                        pe = m_Vec1[skew]
                        pe_idx = skew
                        p = -m_Vec1[pa_idx]
                        q = m_Vec1[pb_idx]
                        r = m_Vec1[pc_idx]
                        s = -m_Vec1[pd_idx]
                        t = int(p + q + r + s) >> 1
                        p = t - p
                        q = t - q
                        r = t - r
                        s = t - s
    
                        t = m_Vec1[pe_idx]
                        m_Vec1[pe_idx] = p
                        pe = m_Vec1[skew+inc]
                        pe_idx = skew+inc
                        p = -m_Vec1[pe_idx]
                        m_Vec1[pe_idx] = q
                        pe = m_Vec1[skew + 2 * inc]
                        pe_idx = skew + 2 * inc
                        q = -m_Vec1[pe_idx]
                        m_Vec1[pe_idx] = r
                        pe = m_Vec1[skew + 3 * inc]
                        pe_idx = skew + 3 * inc
                        r = m_Vec1[pe_idx]
                        m_Vec1[pe_idx] = s
                        s = int(p + q + r + t) >> 1
                        m_Vec1[pa_idx] = s - p
                        pa = m_Vec1[pa_idx + inc]
                        pa_idx = pa_idx + inc
                        m_Vec1[pb_idx] = s - t
                        pb = m_Vec1[pb_idx - inc]
                        pb_idx = pb_idx - inc
                        m_Vec1[pc_idx] = s - q
                        pc = m_Vec1[pc_idx + inc]
                        pc_idx = pc_idx + inc
                        m_Vec1[pd_idx] = s - r
                        if(i==1):
                            break
                        else:
                            pd = m_Vec1[pd_idx + inc] 
                            pd_idx = pd_idx + inc
                        i=i-1
                        if (i==0):
                            break
                    ts = m_Chic1 * (m_Chic2 + self.m_GScale * m_Vec1[m_TLEN - 1])
                    self.m_GScale = m_Rscale * ts * m_ActualRSD
                    return (self.m_GScale * m_Vec1[0])
    
                else:
                    print('ERRORE')
        else:
            return 10