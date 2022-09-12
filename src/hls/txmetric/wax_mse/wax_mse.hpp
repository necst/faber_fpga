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
* High-Level-Synthesis implementation file for Warp Transform and Mean Squared Error computation
*
****************************************************************/
#ifndef WA_XIL_MSE_HPP
#define WA_XIL_MSE_HPP
#include "mean_square_error.hpp"
#include "mean_square_error_utils.hpp"
#include "xf_warp_transform_config.hpp"
#include <string.h>
#include "assert.h"
#include "hls_math.h"
#include "utils.hpp"

#ifndef CACHING
#ifndef USING_XILINX_VITIS
	extern void wax_mse_accel(INPUT_DATA_TYPE * input_img, INPUT_DATA_TYPE * input_ref, data_t * mutual_info,float* transform, int rows, int cols);
#else
	extern "C" void wax_mse_accel(INPUT_DATA_TYPE * input_img, INPUT_DATA_TYPE * input_ref, data_t * mutual_info,float* transform, int rows, int cols);

#endif //USING_XILINX_VITIS
#else
#ifndef USING_XILINX_VITIS
	extern void wax_mse_accel(INPUT_DATA_TYPE * input_img,  data_t * mutual_info, unsigned int functionality, int *status, float* transform, int rows, int cols);
#else
#endif //USING_XILINX_VITIS
	extern "C" void wax_mse_accel(INPUT_DATA_TYPE * input_img,  data_t * mutual_info, unsigned int functionality, int *status, float* transform, int rows, int cols);

#endif //CACHING


#endif //WA_XIL_MI_HPP
