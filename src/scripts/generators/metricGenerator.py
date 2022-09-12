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
import os
class MetricConfigurationGenerator:

    def __init__(self):
        pass

    def writeParzenStuffs(self, header, inp_img_dim):
        my_dim=1.0/(inp_img_dim*inp_img_dim)
        print(my_dim)
        header.write("\
#include \"string.h\"\n\
#include \"hls_stream.h\"\n\
#define ACC_PACK (ACC_SIZE * ACC_BITWIDTH)\n\
#define ACC_PACK_TYPE ap_uint<ACC_PACK>\n\
\n\
#define PADDING 0\n\
\n\
const unsigned int dim_row = J_HISTO_ROWS;\n\
// #define J_HISTO_PADDED_ROWS (J_HISTO_ROWS + (2*PADDING))\n\
// #define J_HISTO_PADDED_COLS J_HISTO_PADDED_ROWS\n\
#define KERNEL_SIZE 3\n\
\n\
const data_t dim_inverse = {0:0.15f}; // 1/(512*512)\n\
\n\
// equally spaced b-spline of degree 4 (5 knots, of which 3 non zero)\n\
//const data_t b_spline_kernel[KERNEL_SIZE] = {{ 0.167, 0.667, 0.167 }};\n\
#define COMPUTATION_TYPE ap_uint<32>\n\
\n\
\n\
// equally spaced b-spline of degree 4 (5 knots, of which 3 non zero)\n\
const COMPUTATION_TYPE b_spline_kernel[KERNEL_SIZE] = {{1, 4, 1}};\n\
const data_t kernel_factor = 36.;\n\
const data_t total_factor = 1/(kernel_factor*{1}.* {1}.);\n\
const data_t log_bits = 23.1699250014423123629074778878956330175;//log2(36*512*512)\n\
".format(my_dim, inp_img_dim) )
#TODO: parametrization of kernel, kernel size, and log bits

    def writeCachingUram(self,caching, uram, header):
        if caching:
            header.write(" \n \
#define CACHING\n\
//14\n")
        if uram:
            header.write(" \n \
#define URAM\n \
//15\n")

    def writeImgDimAndBitwidth(self,inp_img_bits, inp_img_dim, header):
        header.write(" \n\
/*********** SIM used values **********/\n\
#define DIMENSION {1}\n\
//1\n \
/*********** End **********/\n\
\n\
#define MYROWS DIMENSION\n\
#define MYCOLS DIMENSION\n\
\n\
#define UNPACK_DATA_BITWIDTH {0}\n\
//0\n \
typedef ap_uint<UNPACK_DATA_BITWIDTH> UNPACK_DATA_TYPE;\n".format(inp_img_bits,inp_img_dim))


    def print_ccmse_config(self,cc_or_mse, num_pe, inp_img_bits,inp_img_dim,\
        comp_type, caching, uram, vitis, derived,out_path,clean,top_name):
        if vitis:
            vitis_externC="\"C\""
        else:
            vitis_externC=""

        if cc_or_mse: #assuming true for cc and false for mse
            guard="CROSS_CORRELATION"
            top_name="cross_correlation"
        else:
            guard="MEAN_SQUARE_ERROR"
            top_name="mean_square_error"

        if clean:
            os.remove(out_path+top_name+".hpp")
        cc_header = open(out_path+top_name+".hpp","w+")
        cc_header.write("\
#ifndef {0}_HPP\n\
#define {0}_HPP\n\
#include \"string.h\"\n\
#include \"ap_int.h\"\n\
\n".format(guard))

        self.writeImgDimAndBitwidth(inp_img_bits, inp_img_dim, cc_header)
        cc_header.write("\n\
#define PE {0} \n\
//2\n\
\n\
#define INPUT_DATA_BITWIDTH (PE * UNPACK_DATA_BITWIDTH)\n\
typedef ap_uint<INPUT_DATA_BITWIDTH> INPUT_DATA_TYPE;\n\
\n\
#define NUM_DATA (DIMENSION*DIMENSION)\n\
#define NUM_INPUT_DATA (NUM_DATA/(PE))\n\
\n\
#define SUM_BITWIDTH {1} //UNPACK_DATA_BITWIDTH*2+log2(DIMENSION)*2\n\
#define TMP_SUM_BITWIDTH {2} //SUM_BITWIDTH - log2(PE)\n\
\n\
typedef {3} data_t;\n\
\n\
const unsigned int fifo_in_depth = NUM_INPUT_DATA;\n\
const unsigned int fifo_out_depth = 1;\n\
#ifndef CACHING\n\
extern {4} void {5}_master(INPUT_DATA_TYPE* If, INPUT_DATA_TYPE* Im, data_t *result);\n\
#else\n\
extern {4} void {5}_master(INPUT_DATA_TYPE * input_img,  data_t * result, unsigned int functionality, int *status);\n\
#endif//CACHING\n\
    ".format(num_pe, derived.sumbitwidth, derived.tmp_sumbitwidth, comp_type, vitis_externC,top_name))
        self.writeCachingUram(caching,uram, cc_header)
        cc_header.write("#endif //{0}_HPP\n".format(guard))
        cc_header.close()


    def print_mi_config(self,num_pe, inp_img_bits, inp_img_dim,  derived , pe_entropy, \
        fixed, caching, uram, vitis, out_path, clean, top_name, parzen_or_mi):
        derived_hist_dim=0
        if parzen_or_mi: #assuming true for cc and false for mse
            guard="PARZEN"
            top_name="parzen"
            derived_hist_dim=derived.hist_dim #+2 #TODO (+2 for Padding?)
        else:
            guard="MUTUAL_INF"
            top_name="mutual_information"
            derived_hist_dim=derived.hist_dim
        if clean:
            os.remove(out_path+top_name+".hpp")
        if fixed:
            fixerd_or_not=""
        else:
            fixerd_or_not="//"
        if vitis:
            vitis_externC="\"C\""
        else:
            vitis_externC=""

        mi_header = open(out_path+top_name+".hpp","w+")
        mi_header.write("\
#ifndef {0}_HPP\n \
#define {0}_HPP\n \
#include \"ap_int.h\"\n \
\n \
#define TWO_FLOAT 2.0f\n \
#define OUT_BUFF_SIZE 1\n \
\n \
#define ENTROPY_THRESH 0.000000000000001\n \
#define ENTROPY_FLT_THRESH 0.000000000001\n \
#define ENTROPY_REF_THRESH 0.000000000001\n \
\n \
/************/\n \
    \n ".format(guard))

        self.writeImgDimAndBitwidth(inp_img_bits, inp_img_dim, mi_header)
        mi_header.write("typedef float data_t;\n \
#define DATA_T_BITWIDTH 32\n \
typedef ap_uint<{0}> MY_PIXEL; \n \
//0\n \
/*********** SIM used values **********/\n \
#define MAX_RANGE (int)(MAX_FREQUENCY - 1)\n \
/*********** End **********/\n \
\n \
/*\n \
 Joint Histogram computations\n \
*/\n \
\n \
#define HIST_PE {2}\n \
//2\n \
\n \
#define INPUT_DATA_BITWIDTH (HIST_PE*UNPACK_DATA_BITWIDTH)\n \
#define INPUT_DATA_TYPE ap_uint<INPUT_DATA_BITWIDTH>\n \
\n \
#define NUM_INPUT_DATA (DIMENSION*DIMENSION/(HIST_PE))\n \
\n \
#define WRAPPER_HIST2(num) wrapper_joint_histogram_##num\n \
#define WRAPPER_HIST(num) WRAPPER_HIST2(num)\n \
\n \
#define WRAPPER_ENTROPY2(num) wrapper_entropy_##num\n \
#define WRAPPER_ENTROPY(num) WRAPPER_ENTROPY2(num)\n \
\n \
#define J_HISTO_ROWS {3}\n \
//3\n \
#define J_HISTO_COLS J_HISTO_ROWS\n \
#define MIN_HIST_BITS {4}\n \
//4\n \
#define MIN_HIST_BITS_NO_OVERFLOW MIN_HIST_BITS - 1\n\
//#define MIN_J_HISTO_BITS (int)(std::ceil(std::log2(MYROWS*MYCOLS)))\n \
// TODO overflow non contemplato :D, sarebbe + 1\n \
#define MIN_HIST_PE_BITS (MIN_HIST_BITS - {5})\n \
//5\n \
//#define MIN_HISTO_PE_BITS (int)(std::ceil(std::log2(ROW_PE_KRNL*COLS_PE_KRNL)))\n \
//MIN_HIST_BITS - log2(HIST_PE)\n \
\n \
\n \
typedef ap_uint<MIN_HIST_BITS> MinHistBits_t;\n \
typedef ap_uint<MIN_HIST_PE_BITS> MinHistPEBits_t;\n \
\n \
\n \
#define ENTROPY_PE {6}\n \
//6\n \
const unsigned int ENTROPY_PE_CONST = ENTROPY_PE;\n \
\n \
#define PACKED_HIST_PE_DATA_BITWIDTH (MIN_HIST_PE_BITS*ENTROPY_PE)\n \
#define PACKED_HIST_PE_DATA_TYPE ap_uint<PACKED_HIST_PE_DATA_BITWIDTH>\n \
\n \
#define PACKED_HIST_DATA_BITWIDTH (MIN_HIST_BITS*ENTROPY_PE)\n \
#define PACKED_HIST_DATA_TYPE ap_uint<PACKED_HIST_DATA_BITWIDTH>\n \
\n \
//#define PACKED_DATA_T_DATA_BITWIDTH (INNER_ENTROPY_TYPE_BITWIDTH*ENTROPY_PE)\n \
//#define PACKED_DATA_T_DATA_TYPE ap_uint<PACKED_DATA_T_DATA_BITWIDTH>\n \
\n \
#define UINT_OUT_ENTROPY_TYPE_BITWIDTH {7}\n \
//7\n \
// MAX std::ceil(std::log2( log2(MYROWS*MYCOLS) * (MYROWS*MYCOLS) )) + 1\n \
#define UINT_OUT_ENTROPY_TYPE ap_uint<UINT_OUT_ENTROPY_TYPE_BITWIDTH>\n \
\n \
#define FIXED_BITWIDTH 42\n \
#define FIXED_INT_BITWIDTH UINT_OUT_ENTROPY_TYPE_BITWIDTH\n \
{8}#define FIXED ap_ufixed<42, {7}>\n \
//8\n \
#ifndef FIXED\n \
    #define ENTROPY_TYPE data_t\n \
    #define OUT_ENTROPY_TYPE data_t\n \
#else\n \
    #define ENTROPY_TYPE FIXED\n \
    #define OUT_ENTROPY_TYPE UINT_OUT_ENTROPY_TYPE\n \
#endif\n \
\n \
\n \
#define ANOTHER_DIMENSION J_HISTO_ROWS // should be equal to j_histo_rows\n \
\n \
\n \
//UNIFORM QUANTIZATION\n \
#define INTERVAL_NUMBER {9} // L, amount of levels we want for the binning process, thus at the output\n \
//9\n \
#define MAX_FREQUENCY {10} // or 255? the maximum number of levels at the input stage\n \
//10\n\
#define MINIMUM_FREQUENCY 0\n \
#define INTERVAL_LENGTH ( (MAX_FREQUENCY - MINIMUM_FREQUENCY) / INTERVAL_NUMBER ) // Q = (fmax - fmin )/L\n \
#define INDEX_QUANTIZED(i) (i/INTERVAL_LENGTH) // Qy(i) =  f - fmin / Q\n \
\n \
/*****************/\n \
\n\
const unsigned int fifo_in_depth =  (MYROWS*MYCOLS)/(HIST_PE);\n\
const unsigned int fifo_out_depth = 1;\n\
const unsigned int pe_j_h_partition = HIST_PE;\n\
\n\
typedef MinHistBits_t HIST_TYPE;\n\
typedef MinHistPEBits_t HIST_PE_TYPE;\n\
\n\
const ENTROPY_TYPE scale_factor = {11}f;\n\
//11 \n \
//constexpr float scale_factor = 1.0f /(DIMENSION*DIMENSION);\n\
\n \
#ifndef CACHING\n \
    extern {12} void {14}_master(INPUT_DATA_TYPE * input_img, INPUT_DATA_TYPE * input_ref, data_t * mutual_info);\n \
#else\n \
    extern {12} void {14}_master(INPUT_DATA_TYPE * input_img,  data_t * mutual_info, unsigned int functionality, int* status);\n \
#endif\n \
\n \
//12 \n \
#define ACC_SIZE {13}\n \
#define ACC_BITWIDTH 32 \n\
// 13\n \
    \n".format(inp_img_bits, \
        inp_img_dim, \
        num_pe, \
        derived_hist_dim, \
        derived.histos_bits, \
        derived.pe_bits, \
        pe_entropy, \
        derived.uint_fixed_bitwidth , \
        fixerd_or_not,\
        derived.quant_levels, derived.maximum_freq,\
        derived.scale_factor,\
        vitis_externC,\
        derived.entr_acc_size,\
        top_name) )
        self.writeCachingUram(caching,uram,mi_header)
        if parzen_or_mi:
            self.writeParzenStuffs(mi_header, inp_img_dim)
        mi_header.write("\n#endif //{0}_HPP".format(guard))
        mi_header.close()
        
