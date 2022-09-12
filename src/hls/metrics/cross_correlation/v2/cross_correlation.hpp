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
#ifndef CROSS_CORRELATION_HPP
#define CROSS_CORRELATION_HPP
#include "string.h"
#include "ap_int.h"
#include "hls_math.h"

/*********** SIM used values **********/
#define DIMENSION 512
/*********** End **********/

#define MYROWS DIMENSION
#define MYCOLS DIMENSION

#define UNPACK_DATA_BITWIDTH 8
#define PE 2

typedef ap_uint<UNPACK_DATA_BITWIDTH> UNPACK_DATA_TYPE;

#define INPUT_DATA_BITWIDTH (PE * UNPACK_DATA_BITWIDTH)
typedef ap_uint<INPUT_DATA_BITWIDTH> INPUT_DATA_TYPE;

#define NUM_DATA (DIMENSION*DIMENSION)
#define NUM_INPUT_DATA (NUM_DATA/(PE))

#define SUM_BITWIDTH 34 //UNPACK_DATA_BITWIDTH*2+log2(DIMENSION)*2
#define TMP_SUM_BITWIDTH 33 //SUM_BITWIDTH - log2(PE)

typedef float data_t;

#define CACHING
#define URAM

const unsigned int fifo_in_depth = NUM_INPUT_DATA;
const unsigned int fifo_out_depth = 1;

#ifndef CACHING

#ifndef USING_XILINX_VITIS
	extern void cross_correlation_master(INPUT_DATA_TYPE* If, INPUT_DATA_TYPE* Im, data_t *result);
#else //USING_XILINX_VITIS
	extern "C" void cross_correlation_master(INPUT_DATA_TYPE* If, INPUT_DATA_TYPE* Im, data_t *result);
#endif //USING_XILINX_VITIS

#else // CACHING
	#ifndef USING_XILINX_VITIS
	extern void cross_correlation_master(INPUT_DATA_TYPE * input_img,  data_t * result, unsigned int functionality, int *status);
#else //USING_XILINX_VITIS
	extern "C" void cross_correlation_master(INPUT_DATA_TYPE * input_img,  data_t * result, unsigned int functionality, int *status);
#endif //USING_XILINX_VITIS

#endif // CACHING

#endif //CROSS_CORRELATION_HPP
