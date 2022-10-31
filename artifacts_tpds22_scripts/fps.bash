#!/bin/bash
cd  ../; make default_ultra96; make default_ultra96 D=1024; make default_ultra96 D=2048; cd -
cd  ../; make default_alveo_u200; make default_alveo_u200 D=1024; make default_alveo_u200 D=2048; cd -
cd ../; make resyn_extr_zynq_ultra96_v2; make resyn_extr_vts_alveo_u200; cd -