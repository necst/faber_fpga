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
#include <iostream>
#include <cmath>
#include <random>
#include <stdio.h>
#include "mean_squared_error.hpp"

typedef ap_uint<8> MY_PIXEL;
#define MAX_RANGE 255

int main(){

   MY_PIXEL ref[DIMENSION * DIMENSION];
   MY_PIXEL flt[DIMENSION * DIMENSION];

   int myseed = 1234;

   std::default_random_engine rng(myseed);
   std::uniform_int_distribution<unsigned int> rng_dist(0, MAX_RANGE);

   data_t mse_sw, mse_hw_0, mse_hw_1, mse_hw_2;
   ap_uint<SUM_BITWIDTH> sum = 0;

   for(int i=0;i<DIMENSION;i++){
      for(int j=0;j<DIMENSION;j++){
         ref[i *DIMENSION + j]=static_cast<unsigned char>(rng_dist(rng));
      }
   }

#ifdef CACHING
   int status = 0;
   printf("Loading image...\n");
   mean_squared_error_master((INPUT_DATA_TYPE*)ref, &mse_hw_0, 0, &status);
   printf("Status %d\n", status);
#endif

   for(int i=0;i<DIMENSION;i++){
      for(int j=0;j<DIMENSION;j++){
         flt[i *DIMENSION + j]=static_cast<unsigned char>(rng_dist(rng));
      }
   }


   for(int i=0;i<DIMENSION*DIMENSION;i++){
	   int diff = ref[i] - flt[i];
	   unsigned int prod = diff*diff;
	   sum += prod;
   }

   mse_sw = (data_t)sum/(data_t)NUM_DATA;

   printf("SW MSE %lf\n",mse_sw);

#ifndef CACHING
   mean_squared_error_master((INPUT_DATA_TYPE*)flt, (INPUT_DATA_TYPE*)ref, &mse_hw_0);

   printf("First Hardware MSE %f\n", mse_hw_0);

   mean_squared_error_master((INPUT_DATA_TYPE*)flt, (INPUT_DATA_TYPE*)ref, &mse_hw_1);
   printf("Second Hardware MSE %f\n", mse_hw_1);

#else
   mean_squared_error_master((INPUT_DATA_TYPE*)flt, &mse_hw_0, 1, &status);

   printf("First Hardware MSE %f\n", mse_hw_0);
   printf("Status %d\n", status);

   mean_squared_error_master((INPUT_DATA_TYPE*)flt, &mse_hw_1, 1, &status);
   printf("Second Hardware MSE %f\n", mse_hw_1);
   printf("Status %d\n", status);

   mean_squared_error_master((INPUT_DATA_TYPE*)flt, &mse_hw_2, 2, &status);
   printf("Status %d\n", status);
#endif

   if((fabs(mse_sw - mse_hw_0) > 0.01) || (fabs(mse_sw - mse_hw_1 > 0.01))){
       return 1;
   }

   return 0;
}
