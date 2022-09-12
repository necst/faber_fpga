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


FLDR=$1
PYCODE_MI=faber-single-mi.py
PYCODE_AFFINE=faber-single-wax.py
PYCODE_AFFINAMI=faber-single-waxmi.py

PYCODE_SINGLE=
PYCODE_Powell=faber-powell-blocked.py
PYCODE_oneplusone=faber-oneplusone-blocked.py
CLK=200
DATASET_FLDR=../Test/ST
CT_PATH=SE0
PET_PATH=SE4

PLATFORM=Zynq
#PLATFORM=Alveo




BIT_NAME=deploy/faber_wrapper.bit
#BIT_NAME=mutual_information_master.xclbin

#Assuming that in $FLDR there are a plethora of config folders bitstreams

arr_config=( $(ls $FLDR) )
for i in ${arr_config[@]}
do
    NEED_SUDO=
    config_fldr="$FLDR""$i"
    if [[ $PLATFORM == "Zynq" ]]; then
        BITSTREAM=${config_fldr}/${BIT_NAME}
        NEED_SUDO=sudo

    else #not a Zynq
        BITSTREAM=$(ls ${config_fldr}/*.xclbin)
    fi
    
    RES_PATH="$FLDR""$i"

    #echo ""

    config_array=(${config_fldr//-/ });
    echo ${config_array[@]}
    first=${config_array[0]}
    #
    list_first=(${first//// })
    echo ${list_first[@]}

    TARGET_CORES=${list_first[$(( ${#list_first[@]} - 1 ))]}
    echo "target core $TARGET_CORES"
    OPTS=()
    EXPONENTIAL=()
    case $TARGET_CORES in
        "waxmi"|"waxcc"|"waxmse" | "waxprz")
            PYCODE_SINGLE=$PYCODE_AFFINAMI
            metric=$(expr substr $TARGET_CORES 4 3)
            tx=$(expr substr $TARGET_CORES 1 3)
            OPTS+=" -mtr=$metric"
            OPTS+=" -tx=$tx"
            if [ "waxmi" ] || [ "waxprz" ]; then
                EXPONENTIAL+=" --exponential"
            fi
        ;;
        "wax")
            PYCODE_SINGLE=$PYCODE_AFFINE
            tx=$(expr substr $TARGET_CORES 1 3)
            OPTS+=" -tx=$tx"
        ;;
        "mse"|"mi"|"cc"|"prz")
            PYCODE_SINGLE=$PYCODE_MI
            metric=$(expr substr $TARGET_CORES 1 3)
            OPTS+=" -mtr=$metric"
            if [ "mi" ] || [ "prz" ]; then
                EXPONENTIAL+=" --exponential"
            fi
        ;;
        *)
        echo "[ERROR] unknown kernel type"
        continue     # unknown option
        ;;
    esac


    CORE_NR=${config_array[1]}
   # echo "core number $CORE_NR"
    IMG_DIM=${config_array[2]}
    #echo $IMG_DIM
    CACHING=${config_array[9]} # or interpolation types
    #echo $CACHING
   
    if [ "$CACHING" == t ] 
    then
        OPTS+=" -mem"
    fi
   # echo "$OPTS"
   # echo ""

    
     echo "sudo python3 $PYCODE_SINGLE -ol $BITSTREAM -clk $CLK -t $CORE_NR -p $PLATFORM -im $IMG_DIM $OPTS -rp $RES_PATH $OPTS -c $i"
     $NEED_SUDO python3 $PYCODE_SINGLE -ol $BITSTREAM -clk $CLK -t $CORE_NR -p $PLATFORM -im $IMG_DIM $OPTS -rp $RES_PATH $OPTS -c $i
    # sleep 10
     echo "sudo python3 $PYCODE_Powell -pt 1 -o 0 -cp $CT_PATH -pp $PET_PATH -rp $RES_PATH  -ol $BITSTREAM -clk $CLK -t $CORE_NR -px $DATASET_FLDR -p $PLATFORM -im $IMG_DIM $OPTS -c $i $EXPONENTIAL"
     $NEED_SUDO python3 $PYCODE_Powell -pt 1 -o 0 -cp $CT_PATH -pp $PET_PATH -rp $RES_PATH/powell -ol $BITSTREAM -clk $CLK -t $CORE_NR -px $DATASET_FLDR -p $PLATFORM -im $IMG_DIM $OPTS -c $i $EXPONENTIAL
    # sleep 10
     echo "sudo python3 $PYCODE_oneplusone -pt 1 -o 0 -cp $CT_PATH -pp $PET_PATH -rp $RES_PATH  -ol $BITSTREAM -clk $CLK -t $CORE_NR -px $DATASET_FLDR -p $PLATFORM -im $IMG_DIM $OPTS -c $i "
     $NEED_SUDO python3 $PYCODE_oneplusone -pt 1 -o 0 -cp $CT_PATH -pp $PET_PATH -rp $RES_PATH/oneplone -ol $BITSTREAM -clk $CLK -t $CORE_NR -px $DATASET_FLDR -p $PLATFORM -im $IMG_DIM $OPTS -c $i

done
