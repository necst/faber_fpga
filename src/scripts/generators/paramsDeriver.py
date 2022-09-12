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
import numpy
import math
######################################################

class MetricsParametersDerived:

    def __init__(self):
        self.histos_bits = 0
        self.quant_levels = 0
        self.reduced_lvls = 0 
        self.hist_dim = 0
        self.j_idx_bits = 0
        self.idx_bits = 0
        self.reduced_histos_bits = 0
        self.maximum_freq = 0
        self.in_dim = 0
        self.in_bits = 0
        self.bin_val = 0
        self.pe_number = 0
        self.entr_acc_size = 0
        self.bit_entropy = 0
        self.scale_factor = 0
        self.pe_bits = 0
        self.uint_fixed_bitwidth=0
        #cc and mse
        self.sumbitwidth=0
        self.tmp_sumbitwidth=0
        self.dim_inverse=0

    def derive_bitwidth(self,data_container):
        return 32


    def derive(self, in_dim, in_bits, bin_val, pe_number, entr_acc_size, histotype):
        self.in_dim = in_dim
        self.in_bits = in_bits
        self.bin_val = bin_val
        self.pe_number = pe_number
        self.entr_acc_size = entr_acc_size
        self.histos_bits = math.ceil(numpy.log2(in_dim*in_dim+1))
        self.reduced_lvls = math.ceil(in_bits - bin_val)
        self.quant_levels = math.ceil(2**self.reduced_lvls)
        self.hist_dim = math.ceil(2**self.reduced_lvls)
        self.j_idx_bits = math.ceil(numpy.log2(self.hist_dim*self.hist_dim))
        self.idx_bits = math.ceil(numpy.log2(self.hist_dim))
        self.reduced_histos_bits = math.ceil(numpy.log2(in_dim*in_dim / pe_number))+1
        self.maximum_freq = math.ceil(2**in_bits)
        self.bit_entropy = self.derive_bitwidth(histotype)
        self.scale_factor = 1.0 / (in_dim*in_dim)
        self.pe_bits = math.ceil(numpy.log2(pe_number))
        self.uint_fixed_bitwidth=math.ceil(math.log2(math.log2(in_dim*in_dim)*in_dim*in_dim))
        self.sumbitwidth=math.ceil(in_bits*2+numpy.log2(in_dim)*2)
        self.tmp_sumbitwidth=math.ceil(self.sumbitwidth-numpy.log2(pe_number))

    def getScaleFactor(self):
        return self.scale_factor
    
    def printDerived(self):
        print("Starting params:\n in_dim {0}\n in_bits {1}\n bin_val {2}\n pe_number {3}\n entr_acc_size {4}\n"\
            .format(self.in_dim,\
            self.in_bits, self.bin_val, self.pe_number, self.entr_acc_size))
        print("Derived Configuration: \nhisto bits "+ str(self.histos_bits))
        print("quant_levels "+ str(self.quant_levels))
        print("hist_dim "+ str(self.hist_dim))
        print("j_idx_bits "+ str(self.j_idx_bits))
        print("idx_bits "+ str(self.idx_bits))
        print("reduced_histos_bits "+ str(self.reduced_histos_bits))
        print("maximum_freq "+ str(self.maximum_freq))
        print("entropies bitwdith "+str(self.bit_entropy))


###################################################################################################################################
###################################################################################################################################
###################################################################################################################################
###################################################################################################################################
###################################################################################################################################
###################################################################################################################################