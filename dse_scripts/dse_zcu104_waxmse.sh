#!/bin/bash

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


PES=(1)
CORE_NRS=(3 2 1)
HTYPS=('float')
CACHING=(false)
URAM=(false)
FREQZ=200
INTERPOLATIONS=('nearestn')
#'bilinear')
#change this value if using a zynq-based, use 200MHz / 250 MHz


for p in ${PES[@]}; do
    for cn in ${CORE_NRS[@]}; do
            for it in ${INTERPOLATIONS[@]}; do
                for c in ${CACHING[@]}; do
                    for u in ${URAM[@]}; do
                    for wu in ${CACHING[@]}; do
                        #make xclbin_config PE=$p CORE_NR=$cn HT=$h TARGET=hw OPT_LVL=3 \
                         #CLK_FRQ=$FREQZ PE_ENTROP=$pe CACHING=$c URAM=$u TRGT_PLATFORM=alveo_u200;
                         make hw_gen PE=$p CORE_NR=$cn FREQ_MHZ=$FREQZ WAX_URAM=$wu \
                         CACHING=$c URAM=$u TRGT_PLATFORM=zcu104 METRIC="mse" INTERP_TYPE=$it TRANSFORM="wax";
                    done;
                done; 
            done;
        done;
    done;
done;
