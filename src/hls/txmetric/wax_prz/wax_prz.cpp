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
* High-Level-Synthesis implementation file for Warp Transform and Parzen Normalized Mutual Information computation
*
****************************************************************/
#include "wax_prz.hpp"
#include "utils.hpp"

void compute(INPUT_DATA_TYPE * input_img, INPUT_DATA_TYPE * input_ref, data_t * mutual_info,
		float* transform, int rows, int cols){


#ifndef CACHING
	#pragma HLS INLINE
#endif

#pragma HLS DATAFLOW

static  hls::stream<INPUT_DATA_TYPE> ref_stream("ref_stream");
#pragma HLS STREAM variable=ref_stream depth=2 dim=1
static  hls::stream<INPUT_DATA_TYPE> flt_stream("flt_stream");
#pragma HLS STREAM variable=flt_stream depth=2 dim=1

static  hls::stream<UNPACK_DATA_TYPE> ref_pe_stream[HIST_PE];
#pragma HLS STREAM variable=ref_pe_stream depth=2 dim=1
static  hls::stream<UNPACK_DATA_TYPE> flt_pe_stream[HIST_PE];
#pragma HLS STREAM variable=flt_pe_stream depth=2 dim=1

static  hls::stream<PACKED_HIST_PE_DATA_TYPE> j_h_pe_stream[HIST_PE];
#pragma HLS STREAM variable=j_h_pe_stream depth=2 dim=1

static  hls::stream<PACKED_HIST_DATA_TYPE> joint_j_h_stream("joint_j_h_stream");
#pragma HLS STREAM variable=joint_j_h_stream depth=2 dim=1
static  hls::stream<COMPUTATION_TYPE> h_conv_stream("h_conv_stream");
#pragma HLS STREAM variable=h_conv_stream depth=2 dim=1
static  hls::stream<COMPUTATION_TYPE> v_conv_stream("v_conv_stream");
#pragma HLS STREAM variable=v_conv_stream depth=2 dim=1
static  hls::stream<COMPUTATION_TYPE> joint_j_h_stream_0("joint_j_h_stream_0");
#pragma HLS STREAM variable=joint_j_h_stream_0 depth=2 dim=1
static  hls::stream<COMPUTATION_TYPE> joint_j_h_stream_1("joint_j_h_stream_1");
#pragma HLS STREAM variable=joint_j_h_stream_1 depth=2 dim=1
static  hls::stream<COMPUTATION_TYPE> joint_j_h_stream_2("joint_j_h_stream_2");
#pragma HLS STREAM variable=joint_j_h_stream_2 depth=2 dim=1

static  hls::stream<COMPUTATION_TYPE> row_hist_stream("row_hist_stream");
#pragma HLS STREAM variable=row_hist_stream depth=2 dim=1
static  hls::stream<COMPUTATION_TYPE> col_hist_stream("col_hist_stream");
#pragma HLS STREAM variable=col_hist_stream depth=2 dim=1

static  hls::stream<OUT_ENTROPY_TYPE> full_entropy_stream("full_entropy_stream");
#pragma HLS STREAM variable=full_entropy_stream depth=2 dim=1
static  hls::stream<OUT_ENTROPY_TYPE> row_entropy_stream("row_entropy_stream");
#pragma HLS STREAM variable=row_entropy_stream depth=2 dim=1
static  hls::stream<OUT_ENTROPY_TYPE> col_entropy_stream("col_entropy_stream");
#pragma HLS STREAM variable=col_entropy_stream depth=2 dim=1

static  hls::stream<data_t> mutual_information_stream("mutual_information_stream");
#pragma HLS STREAM variable=mutual_information_stream depth=2 dim=1


// clang-format off
	#pragma HLS DATAFLOW
 // clang-format on

    xf::cv::Mat<TYPE, HEIGHT, WIDTH, NPC1> imgInput(rows, cols);
    xf::cv::Mat<TYPE, HEIGHT, WIDTH, NPC1> imgOutput(rows, cols);

// clang-format off
    #pragma HLS STREAM variable=imgInput.data depth=2
    #pragma HLS STREAM variable=imgOutput.data depth=2
// clang-format on

  // Copy transform data from global memory to local memory:
    float transform_matrix[9];

    for (unsigned int i = 0; i < 9; ++i) {
// clang-format off
        #pragma HLS PIPELINE
        // clang-format on
        transform_matrix[i] = transform[i];
    }

    // Retrieve xf::Mat objects from img_in data:
    xf::cv::Array2xfMat<PTR_WIDTH, TYPE, HEIGHT, WIDTH, NPC1>(input_img, imgInput);

    // Run xfOpenCV kernel:
    xf::cv::warpTransform<NUM_STORE_ROWS, START_PROC, TRANSFORM_TYPE, INTERPOLATION, TYPE, HEIGHT, WIDTH, NPC1,
                          XF_USE_URAM>(imgInput, imgOutput, transform_matrix);

    // Convert _dst xf::Mat object to output array:
    //xf::cv::xfMat2Array<PTR_WIDTH, TYPE, HEIGHT, WIDTH, NPC1>(imgOutput, img_out);
    xf::cv::xfMat2hlsStrm<PTR_WIDTH,TYPE,HEIGHT, WIDTH,NPC1>(imgOutput, flt_stream);

	// Step 1: read data from DDR and split them
//	axi2stream<INPUT_DATA_TYPE, NUM_INPUT_DATA>(flt_stream, input_img);
#ifndef CACHING
	axi2stream<INPUT_DATA_TYPE, NUM_INPUT_DATA>(ref_stream, input_ref);
#else
	bram2stream<INPUT_DATA_TYPE, NUM_INPUT_DATA>(ref_stream, input_ref);
#endif

    split_stream<INPUT_DATA_TYPE, UNPACK_DATA_TYPE, UNPACK_DATA_BITWIDTH, NUM_INPUT_DATA, HIST_PE>(ref_stream, ref_pe_stream);
    split_stream<INPUT_DATA_TYPE, UNPACK_DATA_TYPE, UNPACK_DATA_BITWIDTH, NUM_INPUT_DATA, HIST_PE>(flt_stream, flt_pe_stream);


	// Step 2: Compute two histograms in parallel
    WRAPPER_HIST(HIST_PE)<UNPACK_DATA_TYPE, NUM_INPUT_DATA, HIST_PE_TYPE, PACKED_HIST_PE_DATA_TYPE, MIN_HIST_PE_BITS, PADDING>(ref_pe_stream, flt_pe_stream, j_h_pe_stream);
    sum_joint_histogram<PACKED_HIST_PE_DATA_TYPE, J_HISTO_ROWS*J_HISTO_COLS/ENTROPY_PE, PACKED_HIST_DATA_TYPE, HIST_PE, HIST_PE_TYPE, MIN_HIST_PE_BITS, HIST_TYPE, MIN_HIST_BITS>(j_h_pe_stream, joint_j_h_stream);
    // End Step 2

    horizontal_convolution<PACKED_HIST_DATA_TYPE, COMPUTATION_TYPE, J_HISTO_ROWS, J_HISTO_COLS/ENTROPY_PE, KERNEL_SIZE>(joint_j_h_stream, h_conv_stream);
    vertical_convolution<COMPUTATION_TYPE, COMPUTATION_TYPE, J_HISTO_ROWS, J_HISTO_COLS/ENTROPY_PE, KERNEL_SIZE>(h_conv_stream, v_conv_stream);

	// Step 3: Compute histograms per row and column
    tri_stream<COMPUTATION_TYPE, J_HISTO_ROWS*J_HISTO_COLS>(v_conv_stream, joint_j_h_stream_0, joint_j_h_stream_1, joint_j_h_stream_2);

    hist_row_simple<COMPUTATION_TYPE, J_HISTO_ROWS, J_HISTO_COLS>(joint_j_h_stream_0, row_hist_stream);
    hist_col<COMPUTATION_TYPE, J_HISTO_ROWS, J_HISTO_COLS>(joint_j_h_stream_1, col_hist_stream);

    compute_entropy<COMPUTATION_TYPE, OUT_ENTROPY_TYPE, J_HISTO_ROWS>(row_hist_stream, row_entropy_stream);
    compute_entropy<COMPUTATION_TYPE, OUT_ENTROPY_TYPE, J_HISTO_COLS>(col_hist_stream, col_entropy_stream);
    compute_entropy<COMPUTATION_TYPE, OUT_ENTROPY_TYPE, J_HISTO_ROWS*J_HISTO_COLS>(joint_j_h_stream_2, full_entropy_stream);
    // End Step 3

    compute_mutual_information<OUT_ENTROPY_TYPE, data_t>(row_entropy_stream, col_entropy_stream, full_entropy_stream, mutual_information_stream);

    // Step 7: Write result back to DDR
    stream2axi<data_t, fifo_out_depth>(mutual_info, mutual_information_stream);
}


#ifndef CACHING

#ifdef KERNEL_NAME
extern "C"{
	void KERNEL_NAME
#else
	void wax_prz_accel
#endif //KERNEL_NAME
(INPUT_DATA_TYPE * input_img, INPUT_DATA_TYPE * input_ref, data_t * mutual_info,float* transform, int rows, int cols){
#pragma HLS INTERFACE m_axi port=input_img depth=fifo_in_depth offset=slave bundle=gmem0
#pragma HLS INTERFACE m_axi port=input_ref depth=fifo_in_depth offset=slave bundle=gmem1
#pragma HLS INTERFACE m_axi port=mutual_info depth=1 offset=slave bundle=gmem2
#pragma HLS INTERFACE m_axi port=transform depth=9 offset=slave bundle=gmem2 // keep this together?

#pragma HLS INTERFACE s_axilite port=input_img bundle=control
#pragma HLS INTERFACE s_axilite port=input_ref bundle=control
#pragma HLS INTERFACE s_axilite port=mutual_info register bundle=control
#pragma HLS INTERFACE s_axilite port=transform register bundle=control
#pragma HLS INTERFACE s_axilite port=rows register bundle=control
#pragma HLS INTERFACE s_axilite port=cols register bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control
#pragma HLS DATAFLOW

	compute(input_img, input_ref,mutual_info,transform, rows, cols);

}



#else // CACHING


#ifdef KERNEL_NAME
extern "C"{
	void KERNEL_NAME
#else
	void wax_prz_accel
#endif //KERNEL_NAME
(INPUT_DATA_TYPE * input_img,  data_t * mutual_info, unsigned int functionality, int *status, float* transform, int rows, int cols){
#pragma HLS INTERFACE m_axi port=input_img depth=fifo_in_depth offset=slave bundle=gmem0
#pragma HLS INTERFACE m_axi port=mutual_info depth=1 offset=slave bundle=gmem2 //TODO to swap with status
#pragma HLS INTERFACE m_axi port=status depth=1 offset=slave bundle=gmem1
#pragma HLS INTERFACE m_axi port=transform depth=9 offset=slave bundle=gmem2 // keep this together?

#pragma HLS INTERFACE s_axilite port=input_img bundle=control
#pragma HLS INTERFACE s_axilite port=mutual_info register bundle=control
#pragma HLS INTERFACE s_axilite port=functionality register bundle=control
#pragma HLS INTERFACE s_axilite port=status register bundle=control
#pragma HLS INTERFACE s_axilite port=transform register bundle=control
#pragma HLS INTERFACE s_axilite port=rows register bundle=control
#pragma HLS INTERFACE s_axilite port=cols register bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control


	static INPUT_DATA_TYPE ref_img[NUM_INPUT_DATA] = {0};

	INPUT_DATA_TYPE imageTransformed[NUM_INPUT_DATA];
   #pragma HLS STREAM variable=imageTransformed depth=2


#ifdef URAM
#pragma HLS RESOURCE variable=ref_img core=RAM_1P_URAM
#endif //URAM

	switch(functionality){
	case LOAD_IMG:	copyData<INPUT_DATA_TYPE, NUM_INPUT_DATA>(input_img, ref_img);
					*status = 1;
					*mutual_info = 0.0;
					break;
	case COMPUTE: compute(input_img, ref_img ,mutual_info,transform, rows, cols);
					*status = 1;
					break;
	default:		*status = -1;
					*mutual_info = 0.0;
					break;
	}


}

#endif //CACHING

#ifdef KERNEL_NAME

} // extern "C"

#endif //KERNEL_NAME
