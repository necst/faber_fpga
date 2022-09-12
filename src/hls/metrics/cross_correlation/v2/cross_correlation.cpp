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
#ifndef __CROSS_CORR_CPP__
#define __CROSS_CORR_CPP__
#include "cross_correlation.hpp"
#include "cross_correlation_utils.hpp"
#include "utils.hpp"


void compute_metric(INPUT_DATA_TYPE* input_img, INPUT_DATA_TYPE* input_ref, data_t *result){

#ifndef CACHING
	#pragma HLS INLINE
#endif

#pragma HLS DATAFLOW

static	hls::stream<INPUT_DATA_TYPE> ref_stream("ref_stream");
#pragma HLS STREAM variable=ref_stream depth=2 dim=1
static	hls::stream<INPUT_DATA_TYPE> flt_stream("flt_stream");
#pragma HLS STREAM variable=flt_stream depth=2 dim=1
static	hls::stream<data_t> cc_stream("cc_stream");
#pragma HLS STREAM variable=cc_stream depth=2 dim=1

	axi2stream<INPUT_DATA_TYPE, NUM_INPUT_DATA>(flt_stream, input_img);
#ifndef CACHING
	axi2stream<INPUT_DATA_TYPE, NUM_INPUT_DATA>(ref_stream, input_ref);
#else
	bram2stream<INPUT_DATA_TYPE, NUM_INPUT_DATA>(ref_stream, input_ref);
#endif

	cross_correlation_computation<INPUT_DATA_TYPE, NUM_INPUT_DATA, PE, NUM_DATA, UNPACK_DATA_TYPE, UNPACK_DATA_BITWIDTH, data_t>(ref_stream, flt_stream, cc_stream);

	stream2axi<data_t>(result, cc_stream);

}



#ifndef CACHING
#ifdef KERNEL_NAME
extern "C"{
	void KERNEL_NAME
#else
	void cross_correlation_master
#endif //KERNEL_NAME
(INPUT_DATA_TYPE* input_img, INPUT_DATA_TYPE* input_ref, data_t *result){
	#pragma HLS INTERFACE m_axi port=input_img depth=fifo_in_depth offset=slave bundle=gmem0
	#pragma HLS INTERFACE m_axi port=input_ref depth=fifo_in_depth offset=slave bundle=gmem1
	#pragma HLS INTERFACE m_axi port=result depth=fifo_out_depth offset=slave bundle=gmem2

	#pragma HLS INTERFACE s_axilite port=input_img bundle=control
	#pragma HLS INTERFACE s_axilite port=input_ref bundle=control
	#pragma HLS INTERFACE s_axilite port=result register bundle=control
	#pragma HLS INTERFACE s_axilite port=return bundle=control

	compute_metric(input_img, input_ref, result);

}

#ifdef KERNEL_NAME

} // extern "C"

#endif //KERNEL_NAME



#else // CACHING
#ifdef KERNEL_NAME
extern "C"{
	void KERNEL_NAME
#else
	void cross_correlation_master
#endif //KERNEL_NAME
(INPUT_DATA_TYPE * input_img,  data_t * result, unsigned int functionality, int *status){
#pragma HLS INTERFACE m_axi port=input_img depth=fifo_in_depth offset=slave bundle=gmem0
#pragma HLS INTERFACE m_axi port=result depth=1 offset=slave bundle=gmem2
#pragma HLS INTERFACE m_axi port=status depth=1 offset=slave bundle=gmem1

#pragma HLS INTERFACE s_axilite port=input_img bundle=control
#pragma HLS INTERFACE s_axilite port=result register bundle=control
#pragma HLS INTERFACE s_axilite port=functionality register bundle=control
#pragma HLS INTERFACE s_axilite port=status register bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control


	static INPUT_DATA_TYPE ref_img[NUM_INPUT_DATA] = {0};
#ifdef URAM
#pragma HLS RESOURCE variable=ref_img core=RAM_1P_URAM
#endif //URAM

	switch(functionality){
	case LOAD_IMG:	copyData<INPUT_DATA_TYPE, NUM_INPUT_DATA>(input_img, ref_img);
					*status = 1;
					*result = 0.0;
					break;
	case COMPUTE:	compute_metric(input_img, ref_img, result);
					*status = 1;
					break;
	default:		*status = -1;
					*result = 0.0;
					break;
	}


}

#ifdef KERNEL_NAME

} // extern "C"

#endif //KERNEL_NAME
#endif //CACHING
#endif //__CROSS_CORR_CPP__
