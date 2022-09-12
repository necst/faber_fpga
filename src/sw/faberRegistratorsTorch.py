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
import torch
import kornia



class FaberTorchMetric(object):
    """docstring for FaberTorchMetric"""
    def __init__(self, ref_size=512, metric="mi", transform="wax", exponential=True, interpolation="nearest"):
        object.__init__(self)
        self.ref_entropy = 0
        self.ref_size=ref_size
        self.metric=metric
        self.similarity_function=None
        self.transform_component=transform
        self.exponential=exponential
        self.interpolation=interpolation

        self.compute_metric = None
        self.precompute_metric = None
        self.device = "cpu"
        self.ref_vals = torch.ones(ref_size*ref_size, dtype=torch.int, device=self.device)
        self.move_data = None
        self.hist_dim=256
        self.map_similarity_function()
        self.move_data = self.no_transfer

    def map_similarity_function(self):
        if self.metric == "mi":
            if self.exponential == True:
                self.compute_metric=self.compute_mi_exponential
            else:
                self.compute_metric = self.compute_mi
            self.precompute_metric = self.precompute_mutual_information
        elif self.metric == "prz":
            if self.exponential == True:
                self.compute_metric=self.compute_parzen_mi_exponential
            else:
                self.compute_metric=self.parzen_mi     
            self.precompute_metric = self.precompute_parzen
        elif self.metric == "cc":
            self.compute_metric = self.compute_cc
            self.precompute_metric = self.precompute_cross_correlation
        elif self.metric == "mse":
            self.compute_metric = self.compute_mse
            self.precompute_metric = self.precompute_mean_squared_error
        else:
            self.compute_metric=self.compute_mi
            self.precompute_metric = self.precompute_mutual_information

    def batch_transform(self, images, pars):
        img_warped = kornia.geometry.warp_affine(images, pars, mode=self.interpolation, dsize=(images.shape[2], images.shape[3]))
        return img_warped

    def no_transfer(self, input_data):
        return input_data

    def transform(self, image, par):
        tmp_img = image.reshape((1, 1, *image.shape)).float()
        t_par = torch.unsqueeze(par, dim=0)
        img_warped = kornia.geometry.warp_affine(tmp_img, t_par, mode=self.interpolation, dsize=(tmp_img.shape[2], tmp_img.shape[3]))
        return img_warped

    def my_squared_hist2d_t(self, sample, bins, smin, smax):
        D, N = sample.shape
        edges = torch.linspace(smin, smax, bins + 1, device=self.device)
        nbin = edges.shape[0] + 1
        
        # Compute the bin number each sample falls into.
        Ncount = D*[None]
        for i in range(D):
            Ncount[i] = torch.searchsorted(edges, sample[i, :], right=True)
        
        # Using digitize, values that fall on an edge are put in the right bin.
        # For the rightmost bin, we want values equal to the right edge to be
        # counted in the last bin, and not as an outlier.
        for i in range(D):
            # Find which points are on the rightmost edge.
            on_edge = (sample[i, :] == edges[-1])
            # Shift these points one bin to the left.
            Ncount[i][on_edge] -= 1
        
        # Compute the sample indices in the flattened histogram matrix.
        xy = Ncount[0]*nbin+Ncount[1]
            

        # Compute the number of repetitions in xy and assign it to the
        hist = torch.bincount(xy, None, minlength=nbin*nbin)
        
        # Shape into a proper matrix
        hist = hist.reshape((nbin, nbin))

        hist = hist.float()
        
        # Remove outliers (indices 0 and -1 for each dimension).
        hist = hist[1:-1,1:-1]
        
        return hist

    def precompute_mutual_information(self, Ref_uint8_ravel):
        
        href = torch.histc(Ref_uint8_ravel, bins=256)
        href /= Ref_uint8_ravel.numel()
        href=href[href>0.000000000000001]
        eref=(torch.sum(href*(torch.log2(href))))*-1
        
        return eref

    def mutual_information(self, Ref_uint8_ravel, Flt_uint8_ravel, eref):
        
        idx_joint = torch.stack((Ref_uint8_ravel, Flt_uint8_ravel))
        j_h_init = self.my_squared_hist2d_t(idx_joint, self.hist_dim, 0, 255)/Ref_uint8_ravel.numel()
        
        j_h = j_h_init[j_h_init>0.000000000000001]
        entropy=(torch.sum(j_h*(torch.log2(j_h))))*-1
        
        hflt=torch.sum(j_h_init,axis=0) 
        hflt=hflt[hflt>0.000000000000001]
        eflt=(torch.sum(hflt*(torch.log2(hflt))))*-1
        
        mutualinfo=eref+eflt-entropy
        
        return(mutualinfo)

    def precompute_cross_correlation(self, Ref_uint8_ravel):

        return torch.sum(Ref_uint8_ravel * Ref_uint8_ravel)
        
    def cross_correlation(self, Ref_uint8_ravel, Flt_uint8_ravel, cc_ref):
        
        cc_ref_flt = torch.sum(Ref_uint8_ravel * Flt_uint8_ravel)
        cc_flt = torch.sum(Flt_uint8_ravel * Flt_uint8_ravel)
        return - cc_ref_flt/torch.sqrt(cc_ref*cc_flt)

    def precompute_mean_squared_error(self, Ref_uint8_ravel):
        pass

    def mean_squared_error(self, Ref_uint8_ravel, Flt_uint8_ravel, mse_ref):
        return torch.sum((Ref_uint8_ravel - Flt_uint8_ravel)**2)

    def compute_mi(self, ref_img, flt_img, t_mat, eref):
        flt_warped = self.transform(flt_img, t_mat)
        mi = self.mutual_information(ref_img, flt_warped.ravel(), eref)
        return -(mi.cpu())

    def compute_mi_exponential(self, ref_img, flt_img, t_mat, eref):
        mi = self.compute_mi(ref_img, flt_img, t_mat, eref)
        return torch.exp(mi).cpu()

    def compute_cc(self, ref_img, flt_img, t_mat, cc_ref):
        flt_warped = self.transform(flt_img, t_mat)
        cc = self.cross_correlation(ref_img, flt_warped.ravel(), cc_ref)
        return cc.cpu()

    def compute_cc_exponential(self, ref_img, flt_img, t_mat, cc_ref):
        cc = self.compute_cc(ref_img, flt_img, t_mat, cc_ref)
        return torch.exp(-cc).cpu()

    def compute_mse(self, ref_img, flt_img, t_mat, mse_ref):
        flt_warped = self.transform(flt_img, t_mat)
        mse = self.mean_squared_error(ref_img, flt_warped.ravel(), mse_ref)
        return mse.cpu()

    def compute_mi_couple(self, ref_img, flt_imgs, t_mats, eref):
        flt_warped = self.batch_transform(flt_imgs, t_mats)
        #flt_img = transform(flt_img, t_mat)
        mi_a = self.mutual_information(ref_img, flt_warped[0].ravel(), eref)
        mi_b = self.mutual_information(ref_img, flt_warped[1].ravel(), eref)
        return torch.exp(-mi_a).cpu(), torch.exp(-mi_b).cpu()

    def compute_cc_couple(self, ref_img, flt_imgs, t_mats, cc_ref):
        flt_warped = self.batch_transform(flt_imgs, t_mats)
        cc_a = self.cross_correlation(ref_img, flt_warped[0].ravel(), cc_ref)
        cc_b = self.cross_correlation(ref_img, flt_warped[1].ravel(), cc_ref)
        return cc_a.cpu(), cc_b.cpu()

    def compute_mse_couple(self, ref_img, flt_imgs, t_mats, mse_ref):
        flt_warped = self.batch_transform(flt_imgs, t_mats)
        mse_a = self.mean_squared_error(ref_img, flt_warped[0].ravel(), mse_ref)
        mse_b = self.mean_squared_error(ref_img, flt_warped[1].ravel(), mse_ref)
        return mse_a.cpu(), mse_b.cpu()


    def compute_moments(self, img):
        moments = torch.empty(6, device=self.device)
        l = torch.arange(img.shape[0], device=self.device)
        moments[0] = torch.sum(img) # m00
        moments[1] = torch.sum(img * l) # m10
        moments[2] = torch.sum(img * (l**2)) # m20
        moments[3] = torch.sum(img * l.reshape((img.shape[0], 1)) ) # m01
        moments[4] = torch.sum(img * (l.reshape((img.shape[0], 1)))**2 ) # m02
        moments[5] = torch.sum(img * l * l.reshape((img.shape[0], 1))) # m11
        return moments

    def to_matrix_blocked(self, vector_params):
        mat_params=torch.empty((2,3))
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
            mat_params[0][1]=torch.sqrt(1-(vector_params[2]**2))
            mat_params[1][0]=-mat_params[0][1]
        return (mat_params)

    def estimate_initial(self, Ref_uint8, Flt_uint8, params):
        
        ref_mom = self.compute_moments(Ref_uint8)
        flt_mom = self.compute_moments(Flt_uint8)
            
        flt_avg_10 = flt_mom[1]/flt_mom[0]
        flt_avg_01 = flt_mom[3]/flt_mom[0]
        flt_mu_20 = (flt_mom[2]/flt_mom[0]*1.0)-(flt_avg_10*flt_avg_10)
        flt_mu_02 = (flt_mom[4]/flt_mom[0]*1.0)-(flt_avg_01*flt_avg_01)
        flt_mu_11 = (flt_mom[5]/flt_mom[0]*1.0)-(flt_avg_01*flt_avg_10)

        ref_avg_10 = ref_mom[1]/ref_mom[0]
        ref_avg_01 = ref_mom[3]/ref_mom[0]
        ref_mu_20 = (ref_mom[2]/ref_mom[0]*1.0)-(ref_avg_10*ref_avg_10)
        ref_mu_02 = (ref_mom[4]/ref_mom[0]*1.0)-(ref_avg_01*ref_avg_01)
        ref_mu_11 = (ref_mom[5]/ref_mom[0]*1.0)-(ref_avg_01*ref_avg_10)
        
        params[0][2] = ref_mom[1]/ref_mom[0]-flt_mom[1]/flt_mom[0]
        params[1][2] = ref_mom[3]/ref_mom[0] - flt_mom[3]/flt_mom[0]
        
        rho_flt=0.5*torch.atan((2.0*flt_mu_11)/(flt_mu_20-flt_mu_02))
        rho_ref=0.5*torch.atan((2.0*ref_mu_11)/(ref_mu_20-ref_mu_02))
        delta_rho=rho_ref-rho_flt
        
        roundness=(flt_mom[2]/flt_mom[0]) / (flt_mom[4]/flt_mom[0])
        if torch.abs(roundness-1.0)>=0.3:
            params[0][0]= torch.cos(delta_rho)
            params[0][1] = -torch.sin(delta_rho)
            params[1][0] = torch.sin(delta_rho)
            params[1][1] = torch.cos(delta_rho)
        else:
            params[0][0]= 1.0
            params[0][1] = 0.0
            params[1][0] = 0.0
            params[1][1] = 1.0
        return (params)
    
    def precompute_parzen(self, Ref_uint8_ravel):
        pass

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

    def compute_parzen_mi_exponential(self,ref,flt):
        mi=self.parzen_mi(ref,flt)
        return np.exp(-mi)

##################################################
##################################################
##################################################
##################################################
##################################################