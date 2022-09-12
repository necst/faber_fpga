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


make default_ultra96
make default_alveo_u200

make hw_gen PE=1 CORE_NR=2 TARGET=hw CLK_FRQ=200 TRGT_PLATFORM=ultra96_v2 METRIC="mse" TRANSFORM="wax";
make hw_gen PE=1 CORE_NR=2 TARGET=hw CLK_FRQ=200 TRGT_PLATFORM=ultra96_v2 METRIC="mi" TRANSFORM="wax";
make hw_gen PE=1 CORE_NR=2 TARGET=hw CLK_FRQ=200 TRGT_PLATFORM=ultra96_v2 METRIC="nmi" TRANSFORM="wax";

make hw_gen PE=1 CORE_NR=3 TARGET=hw CLK_FRQ=200 TRGT_PLATFORM=zcu104 METRIC="mse" TRANSFORM="wax";

echo "Hello moto"

make hw_gen METRIC='cc' PE=32 CORE_NR=1 FREQ_MHZ=300 TRGT_PLATFORM=alveo_u200;
make hw_gen METRIC='mse' PE=32 CORE_NR=1 FREQ_MHZ=300 TRGT_PLATFORM=alveo_u200;
make hw_gen METRIC='prz' PE=16 CORE_NR=1 HT='float' FREQ_MHZ=300 TRGT_PLATFORM=alveo_u200;
