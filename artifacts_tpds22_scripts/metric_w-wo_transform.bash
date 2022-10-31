#!/bin/bash
cd ..
############## Zynq builds
make hw_gen PE=1 CORE_NR=2 TARGET=hw CLK_FRQ=200 TRGT_PLATFORM=ultra96_v2 METRIC="mi" TRANSFORM="wax";
make hw_gen PE=2 CORE_NR=2 TARGET=hw CLK_FRQ=200 TRGT_PLATFORM=ultra96_v2 METRIC="mi" ;

make hw_gen PE=1 CORE_NR=2 TARGET=hw CLK_FRQ=200 TRGT_PLATFORM=zcu104 METRIC="mi" TRANSFORM="wax";
make hw_gen PE=2 CORE_NR=2 TARGET=hw CLK_FRQ=200 TRGT_PLATFORM=zcu104 METRIC="mi" ;

make resyn_extr_zynq_ultra96_v2

############## Alveo builds
PES=(32 16 8 4 2 1)
CORE_NRS=(1)
HTYPS=('float')
PE_ENTROP=(1)
CACHING=(false)
URAM=(false)
FREQZ=200
INTERPOLATIONS=('nearestn')

for p in ${PES[@]}; do
    for cn in ${CORE_NRS[@]}; do
        for h in ${HTYPS[@]}; do
            for pe in ${PE_ENTROP[@]}; do
            for it in ${INTERPOLATIONS[@]}; do
                for c in ${CACHING[@]}; do
                    for u in ${URAM[@]}; do
                    for wu in ${CACHING[@]}; do
                        make hw_gen PE=$p CORE_NR=$cn HT=$h TARGET=hw OPT_LVL=3 \
                         FREQ_MHZ=$FREQZ PE_ENTROP=$pe CACHING=$c URAM=$u TRGT_PLATFORM=alveo_u200 \
						WAX_URAM=$wu METRIC="mi" INTERP_TYPE=$it TRANSFORM="wax";
                    done;
                    done; 
                done;
            done;
            done;
        done;
    done;
done;


for p in ${PES[@]}; do
    for cn in ${CORE_NRS[@]}; do
        for h in ${HTYPS[@]}; do
            for pe in ${PE_ENTROP[@]}; do
                for c in ${CACHING[@]}; do
                    for u in ${URAM[@]}; do
                        make hw_gen PE=$p CORE_NR=$cn HT=$h TARGET=hw OPT_LVL=3 \
                         FREQ_MHZ=$FREQZ PE_ENTROP=$pe CACHING=$c URAM=$u TRGT_PLATFORM=alveo_u200 METRIC="mi";
                    done;
                done; 
            done;
        done;
    done;
done;

make resyn_extr_vts_alveo_u200

cd -