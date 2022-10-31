#!/bin/bash
cd ..
make hw_gen METRIC='mi' PE=1 CORE_NR=1 HT='float' FREQ_MHZ=200 TRGT_PLATFORM=alveo_u200;
make hw_gen METRIC='cc' PE=1 CORE_NR=1 FREQ_MHZ=200 TRGT_PLATFORM=alveo_u200;
make hw_gen METRIC='mse' PE=1 CORE_NR=1 FREQ_MHZ=200 TRGT_PLATFORM=alveo_u200;
make hw_gen METRIC='prz' PE=1 CORE_NR=1 HT='float' FREQ_MHZ=200 TRGT_PLATFORM=alveo_u200;
make resyn_extr_vts_alveo_u200

cd -