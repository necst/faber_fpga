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
           
IMG_DIM=512

PYCODE_Powell=fabersw-unique.py
PYCODE_oneplusone=fabersw-unique.py

DATASET_FLDR=../Test/ST
CT_PATH=SE0
PET_PATH=SE4
RES_PATH=results

metric=( mi cc mse nmi)
opt=( plone powell )

for i in "${metric[@]}"
do

        echo "python3 $PYCODE_Powell -pt 1 -o 0 -cp $CT_PATH -pp $PET_PATH -rp $RES_PATH/powell_${i} -t 1 -px $DATASET_FLDR -im $IMG_DIM -mtr $i -opt 'powell' -exp -tx 'wax'"
        python3 $PYCODE_Powell -pt 1 -o 0 -cp $CT_PATH -pp $PET_PATH -rp $RES_PATH/powell_${i} -t 1 -px $DATASET_FLDR -im $IMG_DIM -mtr $i -opt 'powell' -exp -tx 'wax'
        echo "python3 $PYCODE_oneplusone -pt 1 -o 0 -cp $CT_PATH -pp $PET_PATH -rp $RES_PATH/plone_${i} -t 1 -px $DATASET_FLDR -im $IMG_DIM -mtr $i -opt 'plone' -tx 'wax' "
        python3 $PYCODE_oneplusone -pt 1 -o 0 -cp $CT_PATH -pp $PET_PATH -rp $RES_PATH/plone_${i} -t 1 -px $DATASET_FLDR -im $IMG_DIM -mtr $i -opt 'plone' -tx 'wax'
done
