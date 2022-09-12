/******************************************
*MIT License
*
*Copyright (c) [2022] [Eleonora D'Arnese, Davide Conficconi, Emanuele Del Sozzo, Luigi Fusco, Donatella Sciuto, Marco Domenico Santambrogio]
*
*Permission is hereby granted, free of charge, to any person obtaining a copy
*of this software and associated documentation files (the "Software"), to deal
*in the Software without restriction, including without limitation the rights
*to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
*copies of the Software, and to permit persons to whom the Software is
*furnished to do so, subject to the following conditions:
*
*The above copyright notice and this permission notice shall be included in all
*copies or substantial portions of the Software.
*
*THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
*IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
*FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
*AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
*LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
*OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
*SOFTWARE.
*/
#ifndef PARZEN_HPP
#define PARZEN_HPP
#include "string.h"
#include "ap_int.h"
#include "hls_stream.h"

typedef float data_t;
#define DATA_T_BITWIDTH 32
typedef ap_uint<8> MY_PIXEL;

#define TWO_FLOAT 2.0f
#define OUT_BUFF_SIZE 1

/*********** SIM used values **********/
#define DIMENSION 512
/*********** End **********/

#define MYROWS DIMENSION
#define MYCOLS DIMENSION

/*********** SIM used values **********/
//#define MAX_RANGE (int)(MAX_FREQUENCY - 1)
/*********** End **********/

// Joint Histogram computations

#define HIST_PE 8
#define UNPACK_DATA_BITWIDTH 8
#define UNPACK_DATA_TYPE ap_uint<UNPACK_DATA_BITWIDTH>

#define INPUT_DATA_BITWIDTH (HIST_PE*UNPACK_DATA_BITWIDTH)
#define INPUT_DATA_TYPE ap_uint<INPUT_DATA_BITWIDTH>

#define NUM_INPUT_DATA (DIMENSION*DIMENSION/(HIST_PE))

#define WRAPPER_HIST2(num) wrapper_joint_histogram_##num
#define WRAPPER_HIST(num) WRAPPER_HIST2(num)

#define WRAPPER_ENTROPY2(num) wrapper_entropy_##num
#define WRAPPER_ENTROPY(num) WRAPPER_ENTROPY2(num)

#define ACC_SIZE 12
#define ACC_BITWIDTH 32

#define ACC_PACK (ACC_SIZE * ACC_BITWIDTH)

#define ACC_PACK_TYPE ap_uint<ACC_PACK>

#define PADDING 0

#define J_HISTO_ROWS (256)
const unsigned int dim_row = J_HISTO_ROWS;
#define J_HISTO_COLS J_HISTO_ROWS
#define MIN_HIST_BITS 19
#define MIN_HIST_BITS_NO_OVERFLOW MIN_HIST_BITS - 1

#if HIST_PE == 1
	#define MIN_HIST_PE_BITS (MIN_HIST_BITS)
#endif

#if HIST_PE == 2
	#define MIN_HIST_PE_BITS (MIN_HIST_BITS - 1)
#endif

#if HIST_PE == 4
	#define MIN_HIST_PE_BITS (MIN_HIST_BITS - 2)
#endif

#if HIST_PE == 8
	#define MIN_HIST_PE_BITS (MIN_HIST_BITS - 3)
#endif

#if HIST_PE == 16
	#define MIN_HIST_PE_BITS (MIN_HIST_BITS - 4)
#endif

#if HIST_PE == 32
	#define MIN_HIST_PE_BITS (MIN_HIST_BITS - 5)
#endif

typedef ap_uint<MIN_HIST_BITS> MinHistBits_t;
typedef ap_uint<MIN_HIST_PE_BITS> MinHistPEBits_t;


#define ENTROPY_PE 1
const unsigned int ENTROPY_PE_CONST = ENTROPY_PE;

#define PACKED_HIST_PE_DATA_BITWIDTH (MIN_HIST_PE_BITS*ENTROPY_PE)
#define PACKED_HIST_PE_DATA_TYPE ap_uint<PACKED_HIST_PE_DATA_BITWIDTH>

#define PACKED_HIST_DATA_BITWIDTH (MIN_HIST_BITS*ENTROPY_PE)
#define PACKED_HIST_DATA_TYPE ap_uint<PACKED_HIST_DATA_BITWIDTH>

#define UINT_OUT_ENTROPY_TYPE_BITWIDTH 30
#define UINT_OUT_ENTROPY_TYPE ap_uint<UINT_OUT_ENTROPY_TYPE_BITWIDTH>

#define FIXED_BITWIDTH 64
#define FIXED_INT_BITWIDTH UINT_OUT_ENTROPY_TYPE_BITWIDTH
//#define FIXED ap_ufixed<64, 30>

#ifndef FIXED
        #define ENTROPY_TYPE data_t
        #define OUT_ENTROPY_TYPE data_t
#else
        #define ENTROPY_TYPE FIXED
        #define OUT_ENTROPY_TYPE UINT_OUT_ENTROPY_TYPE
#endif




typedef MinHistBits_t HIST_TYPE;
typedef MinHistPEBits_t HIST_PE_TYPE;

#define ANOTHER_DIMENSION J_HISTO_ROWS // should be equal to j_histo_rows

//UNIFORM QUANTIZATION
#define INTERVAL_NUMBER 256 // L, amount of levels we want for the binning process, thus at the output
#define MAX_FREQUENCY J_HISTO_ROWS // the maximum number of levels at the input stage
#define MINIMUM_FREQUENCY 0
#define INTERVAL_LENGTH ( (MAX_FREQUENCY - MINIMUM_FREQUENCY) / INTERVAL_NUMBER ) // Q = (fmax - fmin )/L
#define INDEX_QUANTIZED(i) (i/INTERVAL_LENGTH) // Qy(i) =  f - fmin / Q

/*****************/

#define KERNEL_SIZE 3

const data_t dim_inverse = 0.000003814697266; // 1/(512*512)

#define COMPUTATION_TYPE ap_uint<32>

// equally spaced b-spline of degree 4 (5 knots, of which 3 non zero)
const COMPUTATION_TYPE b_spline_kernel[KERNEL_SIZE] = {1, 4, 1};
const data_t kernel_factor = 36.;
const data_t total_factor = 1/(kernel_factor*512.*512.);
const data_t log_bits = 23.1699250014423123629074778878956330175;

const unsigned int fifo_in_depth =  (MYROWS*MYCOLS)/(HIST_PE);
const unsigned int fifo_out_depth = 1;



//#define CACHING
//#define URAM

#ifndef CACHING

#ifndef USING_XILINX_VITIS
	extern void parzen_master(INPUT_DATA_TYPE* If, INPUT_DATA_TYPE* Im, data_t *result);
#else //USING_XILINX_VITIS
	extern "C" void parzen_master(INPUT_DATA_TYPE* If, INPUT_DATA_TYPE* Im, data_t *result);
#endif //USING_XILINX_VITIS

#else // CACHING
	#ifndef USING_XILINX_VITIS
	extern void parzen_master(INPUT_DATA_TYPE * input_img,  data_t * result, unsigned int functionality, int *status);
#else //USING_XILINX_VITIS
	extern "C" void parzen_master(INPUT_DATA_TYPE * input_img,  data_t * result, unsigned int functionality, int *status);
#endif //USING_XILINX_VITIS

#endif // CACHING

#endif //PARZEN_HPP
