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
/***************************************************************
*
* High-Level-Synthesis header file for Mutual Information computation
*
****************************************************************/
#ifndef ENTROPY_H
#define ENTROPY_H

#include "parzen.hpp"
#include "hls_stream.h"
#include "hls_math.h"
#include "utils.hpp"
#include "ap_fixed.h"

//#define THRESHOLD 0.000000001f
#define THRESHOLD 1

const ENTROPY_TYPE inverseLnOf2 = 1.4426950408889634f;
const ENTROPY_TYPE lnOf2 = 0.69314718055994529f;


template<typename Tin, typename Tout, unsigned int dim>
void compute_entropy(hls::stream<Tin> &in_stream, hls::stream<Tout> &out_stream){

#ifndef FIXED
        Tout entropy = 0;
        ENTROPY_TYPE tmp_entropy[ACC_SIZE] = {0};
#else
        ENTROPY_TYPE entropy = 0;
#endif

        for(int i = 0; i < dim; i++){
#pragma HLS PIPELINE
                Tin tmp = in_stream.read();
                if (tmp > THRESHOLD){
                		ENTROPY_TYPE tmpf = tmp;
#ifndef FIXED
                		ENTROPY_TYPE norm_tmp = tmpf * total_factor;
//                		ENTROPY_TYPE log2Value = hls::log(tmpf)/lnOf2;
                		ENTROPY_TYPE log2Value = hls::log(norm_tmp)/lnOf2;
//                        ENTROPY_TYPE prod = tmp*log2Value;
                		ENTROPY_TYPE prod = norm_tmp*log2Value;
                        tmp_entropy[i%ACC_SIZE] += prod;
#else
                        ENTROPY_TYPE logValue = hls::log((data_t)tmpf);
                        ENTROPY_TYPE log2Value = logValue*inverseLnOf2;
#pragma HLS RESOURCE variable=log2Value core=Mul_LUT
                        ENTROPY_TYPE prod = tmp*log2Value;
#pragma HLS RESOURCE variable=prod core=Mul_LUT
                        entropy += prod;
#endif
                }
        }

#ifndef FIXED
        for(int i = 0; i < ACC_SIZE; i++){
#pragma HLS UNROLL
                entropy += tmp_entropy[i];
        }
#endif

        Tout out_entropy = entropy;

        out_stream.write(out_entropy);

}


template<typename Tin, typename Tout, typename Ttmp, unsigned int tmp_bitwidth, unsigned int dim0, unsigned int dim1>
void hist_row_comp(hls::stream<Tin> &in_stream, hls::stream<Tout> &out_stream){

	static Tin acc_val[2][ACC_SIZE];
	#pragma HLS ARRAY_PARTITION variable=acc_val complete dim=1
	#pragma HLS ARRAY_PARTITION variable=acc_val complete dim=2

	for(int i = 0; i < dim0; i++){
		for(int j = 0; j < dim1; j++){
	#pragma HLS PIPELINE
#pragma HLS DEPENDENCE variable=acc_val RAW false
			Tin in = in_stream.read();
			if(j < ACC_SIZE){
				acc_val[i%2][j%ACC_SIZE] = in;
			} else if (j < dim1) {
				acc_val[i%2][j%ACC_SIZE] += in;
			}
			if(i > 0 && j == ACC_SIZE){
				Tout out_val;
				for(int k = 0; k < ACC_SIZE; k++){
					Tin tmp0 = acc_val[(i-1)%2][k];
					Ttmp tmp1 = *((Ttmp *)(&tmp0));
					out_val.range((k+1)*tmp_bitwidth -1, k*tmp_bitwidth) = tmp1;
				}
				out_stream.write(out_val);
			}
		}
	}
	Tout out_val;
	for(int k = 0; k < ACC_SIZE; k++){
#pragma HLS UNROLL
		Tin tmp0 = acc_val[(dim0-1)%2][k];
		Ttmp tmp1 = *((Ttmp *)(&tmp0));
		out_val.range((k+1)*tmp_bitwidth -1, k*tmp_bitwidth) = tmp1;
	}
	out_stream.write(out_val);
}

template<typename Tin, typename Tout, typename Ttmp, unsigned int tmp_bitwidth, unsigned int dim0>
void hist_row_out(hls::stream<Tin> &in_stream, hls::stream<Tout> &out_stream){

	for(int i = 0; i < dim0; i++){
#pragma HLS PIPELINE
		Tin in_val = in_stream.read();
		Tout out_val = 0;
		for(int j = 0; j < ACC_SIZE; j++){
			Ttmp inTmp = in_val.range((j+1)*tmp_bitwidth -1, j*tmp_bitwidth);
			Tout outTmp = *((Tout *)(&inTmp));
			out_val += outTmp;
		}
		out_stream.write(out_val);
	}

}

template<typename T, unsigned int dim0, unsigned int dim1>
void hist_row(hls::stream<T> &in_stream, hls::stream<T> &out_stream){
#pragma HLS INLINE
	hls::stream<ACC_PACK_TYPE> tmp_stream("tmp_stream");
#pragma HLS STREAM variable=tmp_stream depth=2 dim=1
	hist_row_comp<T, ACC_PACK_TYPE, ap_uint<ACC_BITWIDTH>, ACC_BITWIDTH, dim0, dim1>(in_stream, tmp_stream);
	hist_row_out<ACC_PACK_TYPE, T, ap_uint<ACC_BITWIDTH>, ACC_BITWIDTH, dim0>(tmp_stream, out_stream);


}

template<typename T, unsigned int dim0, unsigned int dim1>
void hist_row_simple(hls::stream<T> &in_stream, hls::stream<T> &out_stream) {
	T acc = 0;
	for (int i = 0; i < dim0; ++i) {
		for (int j = 0; j < dim1; ++j) {
			#pragma HLS PIPELINE
			T curr = in_stream.read();
			acc += curr;
			if (j == dim1 - 1) {
				out_stream.write(acc);
				acc = 0;
			}
		}
	}
}


template<typename T, unsigned int dim0, unsigned int dim1>
void hist_col(hls::stream<T> &in_stream, hls::stream<T> &out_stream){

	static T acc_array[dim1];

	for(int i = 0; i < dim0; i++){
		for(int j = 0; j < dim1; j++){
#pragma HLS PIPELINE
			T in = in_stream.read();
			if(i == 0){
				acc_array[j] = in;
			} else {
				acc_array[j] += in;
			}
		}
	}

	for(int i = 0; i < dim1; i++){
#pragma HLS PIPELINE
		T out = acc_array[i];
		out_stream.write(out);
	}

}


template<typename Tin, typename Tout>
void compute_mutual_information(hls::stream<Tin>& in0, hls::stream<Tin>& in1, hls::stream<Tin>& in2, hls::stream<Tout>& out){

        Tin tmp0 = in0.read();
        Tin tmp1 = in1.read();
        Tin tmp2 = in2.read();
#ifndef FIXED
        Tin tmp3 = tmp0 + tmp1 - tmp2;
#else
        int64_t tmp3 = tmp0 + tmp1 - tmp2;
#endif
//        Tout tmp4 = -tmp3*total_factor + log_bits;
        Tout tmp4 = -tmp3;

        out.write(tmp4);

}

template<typename Tin, typename Tout, int dim>
void sum_single_hist(hls::stream<Tin> &in0, hls::stream<Tin>& in1, hls::stream<Tout>& out){

	Tout out_val = 0;
	static Tout tmp_acc[ACC_SIZE];

	for(int i = 0; i < dim; i++){
#pragma HLS PIPELINE
		Tin tin0 = in0.read();
		Tin tin1 = in1.read();
		Tout tf0 = tin0;
		Tout tf1 = tin1;
		Tout tmp2 = 0;
		if (tf0 > 0.0) {
			Tout tmp0 = tf0 * hls::log2(tf0);
			tmp2 += tmp0;
		}

		if (tf1 > 0.0) {
			Tout tmp1 = tf1 * hls::log2(tf1);
			tmp2 += tmp1;
		}
		tmp_acc[i%ACC_SIZE] += tmp2;
		//out_val += tmp2;
	}

	for(int i = 0; i < ACC_SIZE; i++){
#pragma HLS UNROLL
		out_val -= tmp_acc[i];
		tmp_acc[i] = 0;
	}

	out.write(out_val);

}


#endif // ENTROPY_H
