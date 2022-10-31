#!/bin/bash
cd ../src/model

python3 model.py -m cc -n 2 -pe 1 -b 8 -d 512 -p -t -i nn ultra96 > default_ultra96.log
python3 model.py -m mi -n 1 -pe 16 -b 8 -d 512 -p default_alveo_u200 > default_alveo_u200.log

python3 model.py -m cc -n 2 -pe 1 -b 8 -d 512 -p -t -i nn ultra96 > waxmse_u96.log
python3 model.py -m cc -n 2 -pe 1 -b 8 -d 512 -p -t -i nn ultra96 > waxmi_u96.log
python3 model.py -m cc -n 2 -pe 1 -b 8 -d 512 -p -t -i nn ultra96 > waxnmi_u96.log

python3 model.py -m cc -n 1 -pe 32 -b 8 -d 512 -p default_alveo_u200 > cc_alveo.log
python3 model.py -m mse -n 1 -pe 32 -b 8 -d 512 -p default_alveo_u200 > mse_alveo.log
python3 model.py -m nmi -n 1 -pe 16 -b 8 -d 512 -p default_alveo_u200 > nmi_alveo.log

cd -