/*
 * Copyright 2019 Xilinx, Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
#pragma once
#ifndef __XF_TRANSFORM_CONFIG__
#define __XF_TRANSFORM_CONFIG__

#include <ap_int.h>
#include <cmath>
#include <iostream>
#include <math.h>
#include "hls_stream.h"
#include "common/xf_common.hpp"
#include "common/xf_utility.hpp"
#include "imgproc/xf_warp_transform.hpp"

#define RO 0 // 8 Pixel Processing
#define NO 1 // 1 Pixel Processing

// Number of rows in the input image
#define HEIGHT 512//2160
const int max_image_height = HEIGHT;
// Number of columns in  in the input image
#define WIDTH 512//3840
const int max_image_width = WIDTH;

// Number of rows of input image to be stored
#define NUM_STORE_ROWS 100

// Number of rows of input image after which output image processing must start
#define START_PROC 50

#define RGBA 0
#define GRAY 1

// transform type 0-NN 1-BILINEAR
#define INTERPOLATION 1

// transform type 0-AFFINE 1-PERSPECTIVE
#define TRANSFORM_TYPE 0
#define XF_USE_URAM false

// Set the pixel depth:
#if RGBA
#define TYPE XF_8UC3
#else
#define TYPE XF_8UC1
#endif
#define PTR_WIDTH 32

// Set the optimization type:
#define NPC1 XF_NPPC1

const int max_image_bitshifted = WIDTH / NPC1;

#ifndef USING_XILINX_VITIS
	extern void xf_warp_transform_accel(ap_uint<PTR_WIDTH>* img_in, float* transform, ap_uint<PTR_WIDTH>* img_out, int rows, int cols);
#else
	extern "C" void xf_warp_transform_accel(ap_uint<PTR_WIDTH>* img_in, float* transform, ap_uint<PTR_WIDTH>* img_out, int rows, int cols);

#endif //USING_XILINX_VITIS

#endif //