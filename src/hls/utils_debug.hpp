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
* Utilities functions for debugging purposes and/or simulation
*
****************************************************************/
#ifndef UTILS_DEBUG_HPP
#define UTILS_DEBUG_HPP


/*****************
* constexpr square root implementation that uses binary search. 
* It works correctly up to 2^64 with gcc and clang, other simpler versions often fail for numbers > 2^32 
* because compilers limit the recursion depth to e.g. 200.
******************/
// C++11 compile time square root using binary search

#define MID ((lo + hi + 1) / 2)

constexpr uint64_t sqrt_helper(uint64_t x, uint64_t lo, uint64_t hi)
{
  return lo == hi ? lo : ((x / MID < MID)
      ? sqrt_helper(x, lo, MID - 1) : sqrt_helper(x, MID, hi));
}

constexpr uint64_t ct_sqrt(uint64_t x)
{
  return sqrt_helper(x, 0, x / 2 + 1);
}


template<typename T>
void debugJointHisto(T joint_hist[J_HISTO_ROWS * J_HISTO_COLS], int idx){
    printf("*********************************************\n");
    printf("[DEBUG] debugging joint histogram :D\n");
    printf("*********************************************\n");

        for (int k = 0; k < J_HISTO_ROWS; k++)
        {
            for (int j = 0; j < J_HISTO_COLS; j++)
            {
                printf("PE:%d --  %d,%d= %d; ", idx ,k,j,(int) joint_hist[k * J_HISTO_COLS + j]);
            }
      printf("\n");

        }
    printf("******************End ******************\n");

}


void debugMatrix(MY_PIXEL matrix[DIM * DIM]){
      for (int i = 0; i < DIM; i++)
   {
      for (int j = 0; j < DIM; j++)
      {
         printf("m: %d,%d = %d ", i, j, matrix[i*DIM+j]);
      }
      printf("\n");

   }

}

void debugMatrixMinor(MY_PIXEL matrix[IN_ROWS_RED * IN_COLS_RED]){
      for (int i = 0; i < IN_ROWS_RED; i++)
   {
      for (int j = 0; j < IN_COLS_RED; j++)
      {
         printf("matrix: %d,%d = %d ", i, j, matrix[i*IN_COLS_RED+j]);
      }
      printf("\n");

   }

}

#endif // UTILS_DEBUG_HPP
