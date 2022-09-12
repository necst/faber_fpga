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
#ifndef CONVOLUTION_H
#define CONVOLUTION_H

#include "parzen.hpp"

template<typename Tin, typename Tout, unsigned int rows, unsigned int cols, unsigned int kernel_size>
void horizontal_convolution(hls::stream<Tin> &input_stream, hls::stream<Tout> &output_stream){

	const unsigned int pad = kernel_size/2;

	Tout window[kernel_size];
#pragma HLS ARRAY_PARTITION variable=window complete dim=1

	h_loop:for(int i = 0; i < rows; i++){
		w_loop:for(int j = 0; j < cols + (2*pad); j++){
#pragma HLS PIPELINE
			Tout val;
			if (j >= pad && j < cols + pad) {
				val = input_stream.read();
			} else {
				val = 0;
			}

			for(int k = 0; k < kernel_size-1; k++){
				window[k] = window[k+1];
			}

			window[kernel_size-1] = val;

			if(j >= kernel_size - 1){
				Tout out = 0;
				k_loop:for(int k = 0; k < kernel_size; k++){
					out += window[k] * b_spline_kernel[k];

				}
				output_stream.write(out);
			}
		}
	}
}


template<typename Tin, typename Tout, unsigned int rows, unsigned int cols, unsigned int kernel_size>
void vertical_convolution(hls::stream<Tin> &input_stream, hls::stream<Tout> &output_stream){

	const unsigned int pad = kernel_size/2;
	Tout window[kernel_size];
#pragma HLS ARRAY_PARTITION variable=window complete dim=1
	Tout lineBuffer[kernel_size - 1][cols];
#pragma HLS ARRAY_PARTITION variable=lineBuffer complete dim=1

	h_loop:for(int i = 0; i < rows + (2*pad); i++){
		w_loop:for(int j = 0; j < cols; j++){
#pragma HLS PIPELINE
			Tout val;
			if (i >= pad && i < rows + pad) {
				val = input_stream.read();
			} else {
				val = 0;
			}

			//for(int k = 0; k < kernel_size-1; k++){
			//	window[k] = lineBuffer[k+1][j];
			//}
			for(int k = 0; k < kernel_size-1; k++){
				window[k] = lineBuffer[k][j];
			}

//			for(int k = 0; k < kernel_size-1; k++){
//				lineBuffer[k][j] = lineBuffer[k+1][j];
//			}
			for(int k = 0; k < kernel_size-2; k++){
				lineBuffer[k][j] = lineBuffer[k+1][j];
			}

			window[kernel_size-1] = val;
			lineBuffer[kernel_size-2][j] = val;

			if(i >= kernel_size - 1){
				Tout out = 0;
				k_loop:for(int k = 0; k < kernel_size; k++){
					out += window[k] * b_spline_kernel[k];

				}
				output_stream.write(out);
			}
		}
	}
}

#endif
