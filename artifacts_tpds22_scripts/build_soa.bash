#!/bin/bash
bash build_top_bits.bash
cd ..
make hw_gen PE=1 CORE_NR=3 TARGET=hw CLK_FRQ=200 TRGT_PLATFORM=zcu104 METRIC="mse" TRANSFORM="wax"
make resyn_extr_zynq_zcu104

cd -