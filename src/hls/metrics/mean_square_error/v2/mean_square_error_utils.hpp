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
#ifndef __MEAN_SQUARE_ERROR_UTILS_HPP___
#define __MEAN_SQUARE_ERROR_UTILS_HPP___
#include "mean_square_error.hpp"
#include "utils.hpp"

template<typename Tin, unsigned int dim, unsigned int pe, unsigned int numElem, typename Tunpack, unsigned int bitsTunpack, typename Tout>
void mse_computation(hls::stream<Tin> &ref_stream, hls::stream<Tin> &flt_stream, hls::stream<Tout> &mse_stream){
	static ap_uint<SUM_BITWIDTH> sum;
	sum = 0;

#if PE != 1
	static ap_uint<TMP_SUM_BITWIDTH> tmpSum[PE];
#pragma HLS ARRAY_PARTITION variable=tmpSum complete
#endif

	OUTER_MSE_LOOP:for(unsigned int i = 0; i < dim; i++){
#pragma HLS PIPELINE
		Tin ref_val = ref_stream.read();
		Tin flt_val = flt_stream.read();
#if PE != 1
		INNER_MSE_LOOP:for(unsigned int k = 0; k < pe; k++){
			Tunpack unpackedInRef = ref_val.range((k+1)*bitsTunpack-1, k*bitsTunpack);
			Tunpack tmpRef = unpackedInRef;

			Tunpack unpackedInFlt = flt_val.range((k+1)*bitsTunpack-1, k*bitsTunpack);
			Tunpack tmpFlt = unpackedInFlt;

			int diff = tmpRef - tmpFlt;
			unsigned int prod = diff*diff;
#pragma HLS RESOURCE variable=prod core=Mul_LUT

			ap_uint<TMP_SUM_BITWIDTH> currSum = tmpSum[k];
#pragma HLS RESOURCE variable=currSum core=AddSub
			currSum += prod;
			tmpSum[k] = currSum;
		}
#else
		int diff = ref_val - flt_val;
		unsigned int prod = diff*diff;
		sum += prod;
#pragma HLS RESOURCE variable=sum core=AddSub

#endif
	}

#if PE != 1
	for(unsigned int i = 0; i < pe; i++){
#pragma HLS UNROLL
		sum += tmpSum[i];
		tmpSum[i] = 0;
	}
#endif

	Tout out = (Tout)sum / (Tout)numElem;
	mse_stream.write(out);

}

#endif //__MEAN_SQUARE_ERROR_UTILS_HPP___