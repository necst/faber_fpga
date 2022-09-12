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
class TransformerConfigurationGenerator:
	
	def __init__(self):
		pass


	def printwarpTransform_Xilconfig(self,img_dim, n_str_rws, start_proc, \
		rgba, gray, \
		interpolation, tx_type, \
		uram, ptr_width,\
		vitis,out_path,\
		clean,top_name):
		if vitis:
			vitis_externC="\"C\""
		else:
			vitis_externC=""
		if clean:
			os.remove(out_path+top_name)
		txheader = open(out_path+top_name,"w+")
		txheader.write("/* \n \
 * Copyright 2019 Xilinx, Inc. \n \
 * \n \
 * Licensed under the Apache License, Version 2.0 (the \"License\"); \n \
 * you may not use this file except in compliance with the License. \n \
 * You may obtain a copy of the License at \n \
 * \n \
 *     http://www.apache.org/licenses/LICENSE-2.0 \n \
 * \n \
 * Unless required by applicable law or agreed to in writing, software \n \
 * distributed under the License is distributed on an \"AS IS\" BASIS, \n \
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. \n \
 * See the License for the specific language governing permissions and \n \
 * limitations under the License. \n \
 */ \n \
 \n \
#ifndef __XF_TRANSFORM_CONFIG__ \n \
#define __XF_TRANSFORM_CONFIG__ \n \
#include <ap_int.h> \n \
#include <cmath> \n \
#include <iostream> \n \
#include <math.h> \n \
#include \"hls_stream.h\" \n \
#include \"common/xf_common.hpp\" \n \
#include \"common/xf_utility.hpp\" \n \
#include \"imgproc/xf_warp_transform.hpp\" \n \
\n \
#define RO 0 // 8 Pixel Processing\n \
#define NO 1 // 1 Pixel Processing\n \
\n \
// Number of rows in the input image\n \
#define HEIGHT {0}//2160\n \
const int max_image_height = HEIGHT;\n \
// Number of columns in  in the input image\n \
#define WIDTH {0}//3840\n \
const int max_image_width = WIDTH;\n \
\n \
// Number of rows of input image to be stored\n \
#define NUM_STORE_ROWS {1}\n \
\n \
// Number of rows of input image after which output image processing must start\n \
#define START_PROC {2}\n \
\n \
#define RGBA {3}\n \
#define GRAY {4}\n \
\n \
// transform type 0-NN 1-BILINEAR\n \
#define INTERPOLATION {5}\n \
\n \
// transform type 0-AFFINE 1-PERSPECTIVE\n \
#define TRANSFORM_TYPE {6}\n \
#define XF_USE_URAM {7}\n \
\n \
\n \
\n \
\n \
// Set the pixel depth:\n \
#if RGBA\n \
#define TYPE XF_8UC3\n \
#else\n \
#define TYPE XF_8UC1\n \
#endif\n \
#define PTR_WIDTH {8}\n \
\n \
// Set the optimization type:\n \
#define NPC1 XF_NPPC1\n \
\n \
const int max_image_bitshifted = WIDTH / NPC1;\n \
\n \
//#define UNPACK_DATA_BITWIDTH 8\n \
//#define TMP_FACTOR 4\n \
//#define INPUT_DATA_BITWIDTH (TMP_FACTOR*UNPACK_DATA_BITWIDTH)\n \
//#define INPUT_DATA_TYPE ap_uint<INPUT_DATA_BITWIDTH>\n \
//#define INTERMEDIATE_TYPE XF_TNAME(TYPE, NPC1)\n \
\n \
#ifndef USING_XILINX_VITIS\n\
	extern {9} void xf_warp_transform_accel(ap_uint<PTR_WIDTH>* img_in, float* \
	transform, ap_uint<PTR_WIDTH>* img_out, int rows, int cols);\n\
#else\n\
	extern {9}  void xf_warp_transform_accel(ap_uint<PTR_WIDTH>* img_in, \
	float* transform, ap_uint<PTR_WIDTH>* img_out, int rows, int cols);\n\
\n\
#endif //USING_XILINX_VITIS\n\
\n \
#endif //__XF_TRANSFORM_CONFIG__".format(img_dim, n_str_rws, start_proc, rgba, gray, interpolation, tx_type, uram, ptr_width,vitis_externC) )
		txheader.close()