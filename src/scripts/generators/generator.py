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


import argparse
import os
import numpy
import math
import sys
from paramsDeriver import MetricsParametersDerived
from metricGenerator import MetricConfigurationGenerator
from transformerGenerator  import TransformerConfigurationGenerator
##########################################################################################
def createMetric(args, metric, derived,fixed, both):
    print(" [INFO] Creating the metric configuration")
    if both:
        config_name="mutual_information.hpp"
    else:
        config_name=args.config_name
    #this config name will be overwritten in case of cc or mse
    # need to check if really needed here
    if args.metric == "mi" or args.metric == "prz":
        metric.print_mi_config(args.pe_number, args.in_bits ,\
        args.in_dim,  derived, args.pe_entropy, \
        fixed , args.cache_mem, args.use_uram, args.vitis, args.out_path, args.clean, config_name, args.metric == "prz")
    elif  args.metric == "cc" or args.metric == "mse":
        metric.print_ccmse_config(args.metric == "cc" , args.pe_number, args.in_bits, \
            args.in_dim, args.histotype, args.cache_mem, \
            args.use_uram, args.vitis, derived, args.out_path, args.clean, config_name)
    else:
        print("\n\n***********\
            \n   [ERROR] Metric not recognized\
            \n***********\
            \n\n")
        sys.exit("[ERROR] Metric not recognized")

def createTx(args, transformer, derived, both):
    print(" [INFO] Creating the transformer configuration")
    if both:
        config_name="xf_warp_transform_config.hpp"
    else:
        config_name=args.config_name
    input_bitwidth= (args.in_bits * args.pe_number)
    gray=1
    rgb=0
    wax_type=0
    tx_wax_type=0
    use_wax_uram="false"
    if args.rgb:
        gray=0
        rgb=1
    if args.interp_wax_type:
        wax_type=1
    if args.tx_wax_type:
        tx_wax_type=1
    if args.use_wax_uram:
        use_wax_uram="true"
    transformer.printwarpTransform_Xilconfig(args.in_dim,args.num_store_rows,args.num_start_proc_rows,\
    rgb,gray,wax_type,tx_wax_type,\
    use_wax_uram,input_bitwidth,args.vitis,args.out_path, \
    args.clean,args.config_name)

def createBoth(args):
    print(" [INFO] Creating both :D")
    pass


######################################################
######################################################


def main():
    parser = argparse.ArgumentParser(description='Configuration Generation for the MI and histogram accelerator,\n\
        Default configuration is to use \'float\' datatypes with a 512x512 8 bits input matrix and a histogram \n\
        of 256 levels with one PE')
    parser.add_argument("-op","--out_path", nargs='?', help='output path for the out files, default ./', default='./')
    parser.add_argument("-cfg","--config_name", nargs='?', help='configuration file name', default='ddrbenchmark.hpp')
    parser.add_argument("-c", "--clean", help='clean previously created files befor starting', action='store_true')
    parser.add_argument("-mtrc", "--metric", help='Chose among the possible metrics: mi,cc,mse,prz', default="mi")
    parser.add_argument("-ht", "--histotype", nargs='?', help='data type for the floating point computation, \
        default float', default='float')
    parser.add_argument("-pe", "--pe_number", nargs='?', help='number of PEs assigned to the joint histogram\
     computation, default 1', default='1', type=int)
    parser.add_argument("-ib", "--in_bits", nargs='?', help='number of bits for the target input image, \
        default 8', default='8', type=int)
    parser.add_argument("-id", "--in_dim", nargs='?', help='maximum dimension of the target input image,\
     default 512', default='512', type=int)
    parser.add_argument("-bv", "--bin_val", nargs='?', help='reduction factor of in the binning process of the histogram \n\
                        (i.e. a factor of 2 means 2** (in bits - bin_val) bin levels) , default 0', default='0', type=int)
    parser.add_argument("-es", "--entr_acc_size", nargs='?', help=' accumulator size for the entropies \
        computation', default='8', type=int)
    parser.add_argument("-pen", "--pe_entropy", nargs='?', help='number of PEs assigned to the entropy \
        computation, default 1', default='1', type=int)
    
    parser.add_argument("-vts", "--vitis", help='generate vitis version?', action='store_true')
    parser.add_argument("-mem", "--cache_mem", help='use the caching version or not', action='store_true')
    parser.add_argument("-uram", "--use_uram", help="using a caching version with urams, no sens to\
     use without caching", action='store_true')
    
    parser.add_argument("-wax", "--use_wax", help="using xilinx warp transfrom", action='store_true')
    parser.add_argument("-muse", "--use_metric", help="using metric", action='store_true')

    parser.add_argument("-rgb", "--rgb", help='use the warp transfrom version with 3 channels,\
     1 channel if not inserted', action='store_true')
    parser.add_argument("-wau", "--use_wax_uram", help="using a urams in the warp transfrom", action='store_true')
    parser.add_argument("-txt", "--tx_wax_type", help="define this flag for perspective transform, \
        affine otherwise", action='store_true')
    parser.add_argument("-int", "--interp_wax_type", help="define this flag for bilinear interpolation, \
        nearest neighbor otherwise", action='store_true')
    parser.add_argument("-nstrw", "--num_store_rows", nargs='?', help='number of rows to be stored', default='100', type=int)
    parser.add_argument("-nrwproc", "--num_start_proc_rows", nargs='?', help='number of rows after \
        which start computation, <= num_store_rows', default='50', type=int)

    args = parser.parse_args()
    derived = MetricsParametersDerived()
    derived.derive(args.in_dim, args.in_bits, args.bin_val, args.pe_number, args.entr_acc_size, args.histotype)
    derived.printDerived()
    print(args)
    print(args.clean)
    fixed=(args.histotype == "fixed")
    metric = MetricConfigurationGenerator()
    transformer = TransformerConfigurationGenerator()

    if args.use_metric and args.use_wax:
        createMetric(args, metric ,derived,fixed, True)
        createTx(args, transformer, derived, True)
        createBoth(args)
    elif args.use_metric:
        createMetric(args, metric ,derived, fixed, False)
    elif args.use_wax:
        createTx(args, transformer, derived,False)
    else:
        sys.exit(" [WARNING] either a mteric or a transfromer must be used")




if __name__== "__main__":
    main()
