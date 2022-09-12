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
#ifndef __CROSS_CORR_UTILS_HPP
#define __CROSS_CORR_UTILS_HPP
#include "cross_correlation.hpp"
#include "utils.hpp"
#include "hls_math.h"


template<typename Tin, unsigned int dim, unsigned int pe, unsigned int numElem, typename Tunpack, unsigned int bitsTunpack, typename Tout>
void cross_correlation_computation(hls::stream<Tin> &ref_stream, hls::stream<Tin> &flt_stream, hls::stream<Tout> &cc_stream){
	static ap_uint<SUM_BITWIDTH> sum;
	static ap_uint<SUM_BITWIDTH> sumRef;
	static ap_uint<SUM_BITWIDTH> sumFlt;
	sum = 0;
	sumRef = 0;
	sumFlt = 0;
#if PE != 1
	static ap_uint<TMP_SUM_BITWIDTH> tmpSum[PE];
#pragma HLS ARRAY_PARTITION variable=tmpSum complete
	static ap_uint<TMP_SUM_BITWIDTH> tmpSumRef[PE];
#pragma HLS ARRAY_PARTITION variable=tmpSumRef complete
	static ap_uint<TMP_SUM_BITWIDTH> tmpSumFlt[PE];
#pragma HLS ARRAY_PARTITION variable=tmpSumFlt complete
#endif

	OUTER_CC_LOOP:for(unsigned int i = 0; i < dim; i++){
#pragma HLS PIPELINE
		Tin ref_val = ref_stream.read();
		Tin flt_val = flt_stream.read();
#if PE != 1
		INNER_CC_LOOP:for(unsigned int k = 0; k < pe; k++){
			Tunpack unpackedInRef = ref_val.range((k+1)*bitsTunpack-1, k*bitsTunpack);
			Tunpack tmpRef = unpackedInRef;

			Tunpack unpackedInFlt = flt_val.range((k+1)*bitsTunpack-1, k*bitsTunpack);
			Tunpack tmpFlt = unpackedInFlt;

			unsigned int prod = tmpRef * tmpFlt;
#pragma HLS RESOURCE variable=prod core=Mul_LUT
			unsigned int prodRef = tmpRef * tmpRef;
#pragma HLS RESOURCE variable=prodRef core=Mul_LUT
			unsigned int prodFlt = tmpFlt * tmpFlt;
#pragma HLS RESOURCE variable=prodFlt core=Mul_LUT

			ap_uint<TMP_SUM_BITWIDTH> currSum = tmpSum[k];
#pragma HLS RESOURCE variable=currSum core=AddSub
			currSum += prod;
			tmpSum[k] = currSum;

			ap_uint<TMP_SUM_BITWIDTH> currSumRef = tmpSumRef[k];
#pragma HLS RESOURCE variable=currSumRef core=AddSub
			currSumRef += prodRef;
			tmpSumRef[k] = currSumRef;

			ap_uint<TMP_SUM_BITWIDTH> currSumFlt = tmpSumFlt[k];
#pragma HLS RESOURCE variable=currSumFlt core=AddSub
			currSumFlt += prodFlt;
			tmpSumFlt[k] = currSumFlt;

		}
#else
		unsigned int prod = ref_val * flt_val;
		unsigned int prodRef = ref_val * ref_val;
		unsigned int prodFlt = flt_val * flt_val;
		sum += prod;
#pragma HLS RESOURCE variable=sum core=AddSub
		sumRef += prodRef;
#pragma HLS RESOURCE variable=sumRef core=AddSub
		sumFlt += prodFlt;
#pragma HLS RESOURCE variable=sumFlt core=AddSub

#endif
	}

#if PE != 1
	for(unsigned int i = 0; i < pe; i++){
#pragma HLS UNROLL
		sum += tmpSum[i];
		sumRef += tmpSumRef[i];
		sumFlt += tmpSumFlt[i];
		tmpSum[i] = 0;
		tmpSumRef[i] = 0;
		tmpSumFlt[i] = 0;
	}
#endif

	Tout sqrtRef = hls::sqrtf(sumRef);
	Tout sqrtFlt = hls::sqrtf(sumFlt);
	Tout sqrtProd = sqrtRef*sqrtFlt;
	Tout out = (Tout)sum / sqrtProd;
	cc_stream.write(out);

}
#endif// __CROSS_CORR_UTILS_HPP