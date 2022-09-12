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
* High-Level-Synthesis testbench file for Warp Transform and Mutual Information computation
*
****************************************************************/
#include <iostream>
#include <cstdlib>
#include <cmath>
#include <random>
#include <stdio.h>
#include <chrono>
#include <fstream>
#include <string>
#include <cstring>
#include <vector>
#include "common/xf_headers.hpp"
#include "wax_mi.hpp"



#define INPUT_SIZE 65536

#define MAGIC_NUMBER 1000
#define BANDWIDTH 512
#define HOST_DATA_BITWIDTH 32
#define AP_UINT_FACTOR BANDWIDTH / HOST_DATA_BITWIDTH
#define ARRAY_TEST_DIM MAGIC_NUMBER * AP_UINT_FACTOR
#define RANGE_UPPER_BOUND 255

#if RGB == 1
#define CHANNELS 3
#else
#define CHANNELS 1
#endif 

#define MAGIC_BUFFER_SIZE (int)(8 * CHANNELS *HEIGHT * WIDTH / PTR_WIDTH)

// changing transformation matrix dimensions with transform Affine 2x3, Perspecitve 3x3
#if TRANSFORM_TYPE == 1
#define TRMAT_DIM2 3
#define TRMAT_DIM1 3
#else
#define TRMAT_DIM2 3
#define TRMAT_DIM1 2
#endif

// Random Number generator limits
#define M_NUMI1 1
#define M_NUMI2 20
// image operations and transformation matrix input format
typedef float image_oper;

data_t comput_mi_sw(unsigned char ref[DIMENSION * DIMENSION], unsigned char flt[DIMENSION * DIMENSION]){
   
    double j_h[J_HISTO_ROWS][J_HISTO_COLS];
    for(int i=0;i<J_HISTO_ROWS;i++){
        for(int j=0;j<J_HISTO_COLS;j++){
            j_h[i][j]=0.0;
        }
    }

    std::cout << "Joint SW " << std::endl;
    for(int i=0;i<DIMENSION;i++){
        for(int j=0;j<DIMENSION;j++){
            unsigned int a=ref[i *DIMENSION + j];
            unsigned int b=flt[i *DIMENSION + j];
            j_h[a][b]= (j_h[a][b])+1;
        }
    }

    double href_tmp[ANOTHER_DIMENSION];
    for(int i=0;i<ANOTHER_DIMENSION;i++){
    	href_tmp[i]=0.0;
    }

    for (int i=0; i<ANOTHER_DIMENSION; i++) {
        for (int j=0; j<ANOTHER_DIMENSION; j++) {
        	href_tmp[i] += j_h[i][j];
        }
		if(href_tmp[i]!=0){
			std::cout << "href " <<href_tmp[i]<< " row " << i << std::endl;
		}
    }

    double hflt_tmp[ANOTHER_DIMENSION];
    for(int i=0;i<ANOTHER_DIMENSION;i++){
    	hflt_tmp[i]=0.0;
    }

    for (int i=0; i<J_HISTO_ROWS; i++) {
        for (int j=0; j<J_HISTO_COLS; j++) {
        	hflt_tmp[i] += j_h[j][i];
        }
		if(hflt_tmp[i]!=0){
			std::cout << "hflt " <<hflt_tmp[i]<< " col " << i << std::endl;
		}
    }


    for (int i=0; i<J_HISTO_ROWS; i++) {
        for (int j=0; j<J_HISTO_COLS; j++) {
//        	printf("%lf ",j_h[i][j]);
//			if(j_h[i][j]!=0){
//				std::cout << "val " <<j_h[i][j]<< " row " << i << " col " << j << std::endl;
//			}
            j_h[i][j] = j_h[i][j]/(1.0*DIMENSION*DIMENSION);
        }
//        std::cout << std::endl;
    }

    float entropy = 0.0;
    for (int i=0; i<J_HISTO_ROWS; i++) {
        for (int j=0; j<J_HISTO_COLS; j++) {
            float v = j_h[j][i];
            if (v > 0.000000000000001) {
                entropy += v*log2(v);///log(2);
            }
        }
    }
    entropy *= -1;

    double href[ANOTHER_DIMENSION];
    for(int i=0;i<ANOTHER_DIMENSION;i++){
        href[i]=0.0;
    }

    for (int i=0; i<ANOTHER_DIMENSION; i++) {
        for (int j=0; j<ANOTHER_DIMENSION; j++) {
            href[i] += j_h[i][j];
        }
		if(href[i]!=0){
			std::cout << "href " <<href[i]<< " row " << i << std::endl;
		}
    }

    double hflt[ANOTHER_DIMENSION];
    for(int i=0;i<ANOTHER_DIMENSION;i++){
        hflt[i]=0.0;
    }

    for (int i=0; i<J_HISTO_ROWS; i++) {
        for (int j=0; j<J_HISTO_COLS; j++) {
            hflt[i] += j_h[j][i];
        }
		if(hflt[i]!=0){
			std::cout << "hflt " <<hflt[i]<< " col " << i << std::endl;
		}
    }


    double eref = 0.0;
    for (int i=0; i<ANOTHER_DIMENSION; i++) {
        if (href[i] > 0.000000000001) {
            eref += href[i] * log2(href[i]);///log(2);
        }
    }
    eref *= -1;


    double eflt = 0.0;
    for (int i=0; i<ANOTHER_DIMENSION; i++) {
        if (hflt[i] > 0.000000000001) {
            eflt += hflt[i] * log2(hflt[i]);///log(2);
        }
    }
    eflt =  eflt * (-1);

    data_t mutualinfo = eref + eflt - entropy;
    printf("eref MI %lf\n",eref);
    printf("eflt MI %lf\n",eflt);
    printf("joint MI %lf\n",entropy);
    printf("Software MI %lf\n",mutualinfo);

    return mutualinfo;
}

void software_test(cv::Mat image_input,  cv::Mat * opencv_image, cv::Mat _transformation_matrix_2){

#if TRANSFORM_TYPE == 1
#if INTERPOLATION == 1
    cv::warpPerspective(image_input, *opencv_image, _transformation_matrix_2,
                        cv::Size(image_input.cols, image_input.rows), cv::INTER_LINEAR + cv::WARP_INVERSE_MAP,
                        cv::BORDER_TRANSPARENT, 80);
#else
    cv::warpPerspective(image_input, *opencv_image, _transformation_matrix_2,
                        cv::Size(image_input.cols, image_input.rows), cv::INTER_NEAREST + cv::WARP_INVERSE_MAP,
                        cv::BORDER_TRANSPARENT, 80);
#endif
#else
#if INTERPOLATION == 1
    cv::warpAffine(image_input, *opencv_image, _transformation_matrix_2, cv::Size(image_input.cols, image_input.rows),
                   cv::INTER_LINEAR + cv::WARP_INVERSE_MAP, cv::BORDER_TRANSPARENT, 80);
#else
    cv::warpAffine(image_input, *opencv_image, _transformation_matrix_2, cv::Size(image_input.cols, image_input.rows),
                   cv::INTER_NEAREST);// + cv::WARP_INVERSE_MAP, cv::BORDER_TRANSPARENT, 80);
#endif // INTERPOLATION
#endif // TX TYPE

}


cv::Mat generateRandomInputMatrix(int rows, int cols){
    cv::Mat mean = cv::Mat::zeros(1,1,CV_64FC1);
    cv::Mat sigma= cv::Mat::ones(1,1,CV_64FC1);
    cv::RNG rng(1234);
    cv::Mat matrixRowsxCols(rows,cols,CV_8UC1);
    rng.fill(matrixRowsxCols, cv::RNG::NORMAL, mean, sigma);    
    return matrixRowsxCols;
}

cv::Mat generateZeroValuesInputMatrix(int rows, int cols){
 // OpenCV reference:
    cv::Mat opencv_image;
#if GRAY
    opencv_image.create(rows, cols, CV_8UC1);
#else
    opencv_image.create(rows, cols, CV_8UC3);
#endif

    for (int I1 = 0; I1 < rows; I1++) {
        for (int J1 = 0; J1 < cols; J1++) {
#if GRAY
            opencv_image.at<ap_uint8_t>(I1, J1) = 0;
#else
            opencv_image.at<cv::Vec3b>(I1, J1) = 0;
#endif
        }
    }

    return opencv_image;
}



cv::Mat readInputImageOpenCV(const char* filenamepath){
   cv::Mat image_input;
// Reading in the image:
#if GRAY
    image_input = cv::imread(filenamepath, 0);
#else
    image_input = cv::imread(filenamepath, 1);
#endif
    if (!image_input.data) {
        std::cout << "ERROR: Cannot open image " << filenamepath[1] << std::endl;
        return image_input;
    }
 return image_input;
}

void  generateRandomTxMatrixOpenCV(int rows, int cols, int mat_dim1, int mat_dim2, float * R, cv::Mat*transformation_matrix_2){
    
    cv::Mat _transformation_matrix(mat_dim1, mat_dim2, CV_32FC1);
    cv::Mat _transformation_matrix_2(mat_dim1, mat_dim2, CV_32FC1);
    cv::RNG rng;

#if TRANSFORM_TYPE == 1
    cv::Point2f src_p[4];
    cv::Point2f dst_p[4];
    src_p[0] = cv::Point2f(0.0f, 0.0f);
    src_p[1] = cv::Point2f(cols - 1, 0.0f);
    src_p[2] = cv::Point2f(cols - 1, rows - 1);
    src_p[3] = cv::Point2f(0.0f, rows - 1);
    //    to points
    dst_p[0] = cv::Point2f(rng.uniform(int(M_NUMI1), int(M_NUMI2)), rng.uniform(int(M_NUMI1), int(M_NUMI2)));
    dst_p[1] = cv::Point2f(cols - rng.uniform(int(M_NUMI1), int(M_NUMI2)), rng.uniform(int(M_NUMI1), int(M_NUMI2)));
    dst_p[2] =
        cv::Point2f(cols - rng.uniform(int(M_NUMI1), int(M_NUMI2)), rows - rng.uniform(int(M_NUMI1), int(M_NUMI2)));
    dst_p[3] = cv::Point2f(rng.uniform(int(M_NUMI1), int(M_NUMI2)), rows - rng.uniform(int(M_NUMI1), int(M_NUMI2)));

    _transformation_matrix = cv::getPerspectiveTransform(dst_p, src_p);
#else
    cv::Point2f src_p[3];
    cv::Point2f dst_p[3];
    src_p[0] = cv::Point2f(0.0f, 0.0f);
    src_p[1] = cv::Point2f(cols - 1, 0.0f);
    src_p[2] = cv::Point2f(0.0f, rows - 1);
    //    to points
    dst_p[0] = cv::Point2f(rng.uniform(int(M_NUMI1), int(M_NUMI2)), rng.uniform(int(M_NUMI1), int(M_NUMI2)));
    dst_p[1] = cv::Point2f(cols - rng.uniform(int(M_NUMI1), int(M_NUMI2)), rng.uniform(int(M_NUMI1), int(M_NUMI2)));
    dst_p[2] = cv::Point2f(rng.uniform(int(M_NUMI1), int(M_NUMI2)), rows - rng.uniform(int(M_NUMI1), int(M_NUMI2)));

    _transformation_matrix = cv::getAffineTransform(dst_p, src_p);
#endif

    
    int i = 0, j = 0;

    std::cout << "INFO: Transformation Matrix is:";
    for (i = 0; i < 3; i++) {
        for (j = 0; j < 3; j++) {
#if TRANSFORM_TYPE == 1
            R[i * 3 + j] = image_oper(_transformation_matrix.at<double>(i, j));
            _transformation_matrix_2.at<image_oper>(i, j) = image_oper(_transformation_matrix.at<double>(i, j));
#else
            if (i == 2) {
                R[i * 3 + j] = 0;
            } else {
                R[i * 3 + j] = image_oper(_transformation_matrix.at<double>(i, j));
                _transformation_matrix_2.at<image_oper>(i, j) = image_oper(_transformation_matrix.at<double>(i, j));
            }
#endif
            std::cout << R[i * 3 + j] << " ";
        }
        std::cout << "\n";
    }
    std::cout << "GNE " << std::endl;
    *transformation_matrix_2= _transformation_matrix_2;
}

int main(int argc, char** argv) {


    if (argc < 1) {
    std::cout << "Usage: " << argv[0] << " <INPUT_IMAGE_PATH>" << std::endl;
    return EXIT_FAILURE;
    }

    // std::string binaryFile = argv[1];
    cv::Mat image_input, input_ref, image_output, diff_img;
    //tx matrix
    float R[9]; 

    // Reading in the image:
//    if (argv[1] != NULL)
//    {
//        image_input= readInputImageOpenCV(argv[1]);
//        std::cout << "INFO: Reading an input image" << std::endl;
//    }else{
//        image_input=generateRandomInputMatrix(WIDTH,HEIGHT);
//        std::cout << "INFO: Generating a random input image" << std::endl;
//
//    }
    std::string s1="/home/dave/Documenti/necst/ricerca/opening-tpds/build/zcu104/flt.png";
    std::string s2="/home/dave/Documenti/necst/ricerca/opening-tpds/build/zcu104/ref.png";
    image_input=readInputImageOpenCV(s1.c_str());
    input_ref=readInputImageOpenCV(s2.c_str());
    std::cout << "INFO: Input matrix has " << image_input.rows << " rows, and " << image_input.cols << " cols" << std::endl;
    cv::Mat transformation_matrix_2(TRMAT_DIM1, TRMAT_DIM2, CV_32FC1);
//    generateRandomTxMatrixOpenCV(WIDTH, HEIGHT, TRMAT_DIM1, TRMAT_DIM2, R, &transformation_matrix_2);

//    params = np.array([[0.996194698,0.087155743,0.0],[-0.087155743,0.996194698,0.0]])
    transformation_matrix_2.at<image_oper>(0, 0)=0.996194698;
    transformation_matrix_2.at<image_oper>(0, 1)=0.087155743;
    transformation_matrix_2.at<image_oper>(0, 2)=0.0;
    transformation_matrix_2.at<image_oper>(1, 0)=-0.087155743;
    transformation_matrix_2.at<image_oper>(1, 1)=0.996194698;
    transformation_matrix_2.at<image_oper>(1, 2)=0.0;

	R[0]=0.996194698;
	R[1]=-0.087155743;
	R[2]=-0.0;
	R[3]=0.087155743;
	R[4]=0.996194698;
	R[5]=-0.0;
	R[6]=0.0;
	R[7]=0.0;
	R[8]=0.0;

//      params[0][2]=-params[0][2]
//      params[1][2]=-params[1][2]
//
//      params[0][1]=-params[0][1]
//      params[1][0]=-params[1][0]
//    int i = 0, j = 0;
//
//    std::cout << "INFO: Transformation Matrix is:";
//    for (i = 0; i < 3; i++) {
//        for (j = 0; j < 3; j++) {
//            R[i * 3 + j] = image_oper(_transformation_matrix.at<double>(i, j));
//            transformation_matrix_2.at<image_oper>(i, j) = image_oper(_transformation_matrix.at<double>(i, j));
//            std::cout << R[i * 3 + j] << " ";
//        }
//        std::cout << "\n";
//    }
    std::cout << "INFO: tx matrix generated " << std::endl; 
    std::cout << "DEBUG: "<< R[0] << std::endl;
    std::cout << "DEBUG: "<< transformation_matrix_2.at<image_oper>(0,0) << std::endl;
    // Allocate memory for the output images:
    image_output.create(image_input.rows, image_input.cols, image_input.type());
    diff_img.create(image_input.rows, image_input.cols, image_input.type());

    // OpenCL section:
    //Bytes
#if GRAY
    size_t image_in_size_bytes = image_input.rows * image_input.cols * sizeof(unsigned char);

#else
    size_t image_in_size_bytes = image_input.rows * image_input.cols * 3 * sizeof(unsigned char);
#endif
    size_t image_out_size_bytes = image_in_size_bytes;
    size_t vec_in_size_bytes = 9 * sizeof(float);
    std::cout << "INFO: In size =" << image_in_size_bytes << "out size = " << image_out_size_bytes << std::endl;
    data_t mihls_0, misw;
//Launch kernel
    ap_uint<PTR_WIDTH> buf_input [MAGIC_BUFFER_SIZE],buf_output[MAGIC_BUFFER_SIZE], buf_ref [MAGIC_BUFFER_SIZE];
    memcpy(buf_input,image_input.data,image_in_size_bytes);
    memcpy(buf_ref,input_ref.data,image_in_size_bytes);


    wax_mi_accel(buf_input, buf_ref, &mihls_0, R, buf_output, image_input.rows, image_input.cols);

    std::cout << "INFO: Kernel finished" << std::endl;
    memcpy(image_output.data,buf_output,image_out_size_bytes);
    // OpenCV software part
    cv::Mat opencv_image = generateZeroValuesInputMatrix(image_input.rows, image_input.cols);
    std::cout << "INFO: Generated zero values input matrix" << std::endl;
    software_test(image_input, &opencv_image, transformation_matrix_2);
    std::cout << "INFO: End of SW test" << std::endl;
//Output verification
    // cv::imwrite("opencv_output.png", opencv_image);
    // std::cout << "INFO: Writing output image" << std::endl;

    float err_per;

    misw=comput_mi_sw(input_ref.data, opencv_image.data);
    
    printf("Hardware MI %lf\n",mihls_0);
    std::cout << "INFO: mi diffs " <<((data_t)misw - mihls_0) << std::endl;

    cv::absdiff(image_output, opencv_image, diff_img);
    std::cout << "INFO: abs diff" << std::endl;

    xf::cv::analyzeDiff(diff_img, 0, err_per);
    std::cout << "INFO: analyze diff" << std::endl;
    if (err_per > 0.05) {
        return -1;
    } else {
        return 0;
    }
}
