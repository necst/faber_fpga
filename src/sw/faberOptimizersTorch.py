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
from faberImageRegistration import *
import math
from faberRegistratorsTorch import *
from abc import ABCMeta, abstractmethod
import pandas as pd
import time
import os
import pydicom
import torch
import numpy as np
import kornia
import cv2

class FaberTorchSwOptimizers(object, metaclass=ABCMeta):
    """docstring for FaberTorchSwOptimizers"""
    @abstractmethod
    def compute(self, CT, PET, name, curr_res, t_id, patient_id, faber_component, image_dimension):
        pass
    @abstractmethod
    def register_images(self, Ref_uint8, Flt_uint8, faber_component):
        pass

    def readprep_torch_dicom_refflt_pair(self, i,j, device):
        ref = pydicom.dcmread(i)
        Ref_img = torch.tensor(ref.pixel_array.astype(np.int16), dtype=torch.int16, device=device)
        Ref_img[Ref_img==-2000]=1

        flt = pydicom.dcmread(j)
        Flt_img = torch.tensor(flt.pixel_array.astype(np.int16), dtype=torch.int16, device=device)
        
        Ref_img = (Ref_img - Ref_img.min())/(Ref_img.max() - Ref_img.min())*255
        Ref_uint8 = Ref_img.round().type(torch.uint8)
        
        Flt_img = (Flt_img - Flt_img.min())/(Flt_img.max() - Flt_img.min())*255
        Flt_uint8 = Flt_img.round().type(torch.uint8)
        return Ref_uint8, Flt_uint8
        
    def save_data(self, out_stack, name, res_path):
        for i in range(len(out_stack)):
            b=name[i].split('/')
            c=b.pop()
            d=c.split('.')
            cv2.imwrite(res_path+'/'+d[0][0:2]+str(int(d[0][2:5])+1)+'.png', kornia.tensor_to_image(out_stack[i].cpu().byte())) 


class FaberTorchOnePlusOne(FaberTorchSwOptimizers):
    """docstring for FaberPowell"""
    def __init__(self):
        pass

    def compute(self, CT, PET, name, curr_res, t_id, patient_id, faber_component, image_dimension):
        final_img=[]
        times=[]
        t = 0.0
        it_time = 0.0
        for c,ij in enumerate(zip(CT, PET)):
            i = ij[0]
            j = ij[1]
            Ref_uint8, Flt_uint8 = self.readprep_torch_dicom_refflt_pair(i,j, faber_component.device)

            start_time = time.time()
            final_img.append(self.register_images(Ref_uint8, Flt_uint8, faber_component))
            end_time= time.time()
            it_time = (end_time - start_time)
            times.append(it_time)
            t=t+it_time
            print(i)
            print(j)
            print("%d) --- %s seconds ---" % (c, it_time))
            

        df = pd.DataFrame([t, np.mean(times), np.std(times)],columns=['Test'+str(patient_id)])
        times_df = pd.DataFrame(times,columns=['Test'+str(patient_id)])
        df_path = os.path.join(curr_res,'Time_1+1_%02d.csv' % (t_id))
        times_df_path = os.path.join(curr_res,'Img_1+1_%02d.csv' % (t_id))
        df.to_csv(df_path, index=False)
        times_df.to_csv(times_df_path, index=False)
        self.save_data(final_img,PET,curr_res)

    def register_images(self, Ref_uint8, Flt_uint8, faber_component):
        parent = torch.empty((2,3), device=faber_component.device)
        faber_component.estimate_initial(Ref_uint8, Flt_uint8, parent) 
            
        Ref_uint8_ravel = Ref_uint8.ravel().double()
        
        eref = faber_component.precompute_metric(Ref_uint8_ravel)
        
        optimal_params = self.OnePlusOne(Ref_uint8_ravel, Flt_uint8, faber_component,eref,parent)
        params_trans=faber_component.to_matrix_blocked(optimal_params)
        flt_transform = faber_component.transform(Flt_uint8, params_trans)
        return (flt_transform)
      

    def OnePlusOne(self, Ref_uint8_ravel, Flt_uint8, faber_component,eref,parent):
        parent_cpu = parent.cpu() 
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
        A = torch.eye(spaceDimension)*m_InitialRadius
        f_norm = torch.zeros(spaceDimension)
        child = torch.empty(spaceDimension)
        delta = torch.empty(spaceDimension)
        
        pvalue = faber_component.compute_metric(Ref_uint8_ravel, Flt_uint8, parent, eref)
        
        parentPosition = torch.tensor([parent_cpu[0][2],parent_cpu[1][2],parent_cpu[0][0]])
        childPosition = torch.empty(spaceDimension)

        m_CurrentIteration = 0
        
        for i in range (0,m_MaximumIteration):
            m_CurrentIteration=m_CurrentIteration+1
        
            for j in range (0, spaceDimension):
                f_norm[j]= commonfunctions.NormalVariateGenerator() 
        
            delta = A.matmul(f_norm)#A * f_norm
            child = parentPosition + delta
            childPosition = faber_component.to_matrix_blocked(child)
            cvalue = faber_component.compute_metric(Ref_uint8_ravel,Flt_uint8, childPosition, eref)

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

class FaberTorchPowell(FaberTorchSwOptimizers):
    """docstring for FaberPowell"""
    def __init__(self):
        pass        
    def register_images(self, Ref_uint8, Flt_uint8, faber_component):
        params = torch.empty((2,3), device=faber_component.device)
        faber_component.estimate_initial(Ref_uint8, Flt_uint8, params)
        params_cpu = params.cpu()

        rng=torch.tensor([FaberHyperParams.powell_rng_1, FaberHyperParams.powell_rng_2, FaberHyperParams.powell_rng_3])
        pa=torch.tensor([params_cpu[0][2],params_cpu[1][2],params_cpu[0][0]])
        
        Ref_uint8_ravel = Ref_uint8.ravel().double()
        eref = faber_component.precompute_metric(Ref_uint8_ravel)
        optimal_params = self.optimize_powell(rng, pa, Ref_uint8_ravel, Flt_uint8, faber_component, eref) 
        params_trans=faber_component.to_matrix_blocked(optimal_params)
        flt_transform = faber_component.transform(Flt_uint8, params_trans)
        return (flt_transform)


    def compute(self, CT, PET, name, curr_res, t_id, patient_id, faber_component, image_dimension):
        final_img=[]
        times=[]
        t = 0.0
        it_time = 0.0
        for c,ij in enumerate(zip(CT, PET)):
            i = ij[0]
            j = ij[1]
            Ref_uint8, Flt_uint8 = self.readprep_torch_dicom_refflt_pair(i,j, faber_component.device)
            
            start_time = time.time()
            final_img.append(self.register_images(Ref_uint8, Flt_uint8, faber_component))
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
        self.save_data(final_img,PET,curr_res)


    def optimize_goldsearch(self, par, rng, ref_sup_ravel, flt_sup, linear_par,i,faber_component,eref):
        start=par-0.382*rng
        end=par+0.618*rng
        c=(end-(end-start)/1.618)
        d=(start+(end-start)/1.618)
        best_mi = 0.0
        while(math.fabs(c-d)>FaberHyperParams.gss_optimaze_ths):
            linear_par[i]=c
            a=faber_component.to_matrix_blocked(linear_par)
            linear_par[i]=d
            b=faber_component.to_matrix_blocked(linear_par)
            mi_a = faber_component.compute_metric(ref_sup_ravel,flt_sup,a,eref)
            mi_b = faber_component.compute_metric(ref_sup_ravel,flt_sup,b,eref)
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


    def optimize_powell(self, rng, par_lin, ref_sup_ravel, flt_sup, faber_component, eref):
        converged = False
        eps = FaberHyperParams.powell_optimize_eps
        last_mut=100000.0
        it=0
        while(not converged):
            converged=True
            it=it+1
            for i in range(par_lin.numel()):
                cur_par = par_lin[i]
                cur_rng = rng[i]
                param_opt, cur_mi = self.optimize_goldsearch(cur_par, cur_rng, ref_sup_ravel, flt_sup, par_lin,i,faber_component,eref)
                par_lin[i]=cur_par
                if last_mut-cur_mi>eps:
                    par_lin[i]=param_opt
                    last_mut=cur_mi
                    converged=False
                else:
                    par_lin[i]=cur_par
        #print("Iterations "+str(it))
        return (par_lin)