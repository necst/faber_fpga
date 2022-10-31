#!/bin/bash

cd ..
make default_ultra96
make default_alveo_u200

make hw_gen PE=1 CORE_NR=2 TARGET=hw CLK_FRQ=200 TRGT_PLATFORM=ultra96_v2 METRIC="mse" TRANSFORM="wax";
make hw_gen PE=1 CORE_NR=2 TARGET=hw CLK_FRQ=200 TRGT_PLATFORM=ultra96_v2 METRIC="mi" TRANSFORM="wax";
make hw_gen PE=1 CORE_NR=2 TARGET=hw CLK_FRQ=200 TRGT_PLATFORM=ultra96_v2 METRIC="nmi" TRANSFORM="wax";

echo "Hello moto"

make hw_gen METRIC='cc' PE=32 CORE_NR=1 FREQ_MHZ=300 TRGT_PLATFORM=alveo_u200;
make hw_gen METRIC='mse' PE=32 CORE_NR=1 FREQ_MHZ=300 TRGT_PLATFORM=alveo_u200;
make hw_gen METRIC='prz' PE=16 CORE_NR=1 HT='float' FREQ_MHZ=300 TRGT_PLATFORM=alveo_u200;

make resyn_extr_zynq_ultra96_v2
make resyn_extr_vts_alveo_u200

cd -