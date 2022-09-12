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
PYCODE_MI=iron-single-.py
PYCODE_Powell=iron-powell.py
PYCODE_oneplusone=iron-oneplusone.py
TRGT_PLT=$2
#Assuming that in $FLDR there are a plethora of config folders bitstreams
${TOP:=$(pwd)}
arr_config=( $(ls $FLDR) )

echo -en "Configuration,mean_time_hw,std_time_hw,mean_diff,std_diffs,Powell App time[s], Powell AVG x Img [s], Powell Std dev x Img,1+1 App time[s], 1+1 AVG x Img [s], 1+1 Std dev x Img\n">> res_${2}.csv
# echo -en "Configuration,powell,plone\n">> power_${2}.csv
for i in ${arr_config[@]}
do

    config_fldr="$FLDR""$i"
    config_array=(${config_fldr//-/ });
    first=${config_array[0]}
    list_first=(${first//// })

    cd $config_fldr
    config_separation=(${config_fldr//// }); 
    config_paper=""
    echo "Config separation ${config_separation[@]}"
    echo "position $(( ${#config_separation[@]} - 1 ))"
    config_as_fldr=${config_separation[$(( ${#config_separation[@]} - 1 ))]}
    config_fldr_regex="[a-z]{2,6}-[0-4]-[0-9]+-8-(([a-z]+-[0-9]+-[0-9]+-[0-9]-[0-9]+(-(f|t))+))?(([0-9]+)+-(t|f)-[a-z]+-[a-z]{2,3}-(t|f))?"
    echo "$config_as_fldr and $config_fldr_regex"
    CORE_NR=0
    IMG_DIM=0
            if [[ $config_as_fldr =~ $config_fldr_regex ]] ; 
            then 
              echo $i;
              config_paper=
              conf_asfldr_array=(${config_as_fldr//-/ });
              CORE_NR=${conf_asfldr_array[1]}
              IMG_DIM=${conf_asfldr_array[2]}
              cachings="";
              urams="";
              datatype="FLT";
              #3 flt o fx
              if [ ${conf_asfldr_array[4]} == "fixed" ];
              then
                  datatype="FX";
              fi;
              #4 hpe
              #5 epe
              if [ ${conf_asfldr_array[9]} == "t" ];
              then
                  cachings="C";
                  if [ ${conf_asfldr_array[10]} == "t" ];
                  then
                      urams="U";
                  fi;
              fi;
              hpe=${conf_asfldr_array[5]}
              epe=${conf_asfldr_array[6]}
              it="nn"
              if [ "${conf_asfldr_array[9]}" == "bln" ] || [ "${conf_asfldr_array[16]}" == "bln" ];
              then
                  it="bln"
              fi;
              wau=""
              if [ "${conf_asfldr_array[10]}" == "t" ] || [ "${conf_asfldr_array[17]}" == "t" ];
              then
                  wau="WU"
              fi;

              case ${conf_asfldr_array[0]} in
                  "waxprz"|"waxmi"|"waxcc"|"waxmse")
                  str=${conf_asfldr_array[12]}
                  config_paper="${CORE_NR}${conf_asfldr_array[0]}$cachings$urams$wau$datatype-$hpe-$epe-$it-$str-$IMG_DIM"
                  ;;
                  "wax")
                  str=${conf_asfldr_array[5]}
                  hpe=${conf_asfldr_array[4]}
                  config_paper="${CORE_NR}${conf_asfldr_array[0]}$wau-$hpe-$it-$str-$IMG_DIM"

                  ;;
                  "prz"|"mse"|"mi"|"cc")
                  config_paper="${CORE_NR}${conf_asfldr_array[0]}$cachings$urams$datatype-$hpe-$epe-$IMG_DIM"
                  ;;
                  *)
                  echo "[ERROR] unknown kernel type"
                  exit     # unknown option
                  ;;
              esac
                echo $config_paper
            else 
                echo "$config_fldr not a config fldr";
            fi;  



   #mi_res=($(cat Time_mtrtx.csv | head -4 | tail -2))
   #mi_res_diffs=($(cat Time_mtrtx.csv |tail -2))
   if [ "$cachings" == "C" ]; then
     continue
   fi
   lelele=($(sed -e 's/^.*,//g' < Time_mtrtx*.csv ))


   cd -
   echo -en "$config_paper,">> res_${2}.csv
#    echo -en "$config_paper,">> power_${2}.csv
   echo -en "${lelele[2]},${lelele[3]},${lelele[6]},${lelele[7]},"  >> res_${2}.csv
   #echo -en "${mi_res[0]},${mi_res[1]},${mi_res_diffs[0]},${mi_res_diffs[1]}"  >> res_${2}.csv
   cd $config_fldr
#    power_pwll=($(cat powell/power-powell.csv | tail -1))
#    power_plone=($(cat oneplone/power-plone.csv | tail -1))
   pwll_res=($(cat powell/Time_powll_00.csv | tail -3))
   onpl_res=($(cat oneplone/Time_1+1_00.csv | tail -3))
   if [ "$CORE_NR" > 1 ]
   then
     for i in $(seq 1 $(expr $CORE_NR - 1) )
     do
      pwll_resi=($(cat powell/Time_powll_0${i}.csv | tail -3))
      cmp_res=$(python3 -c "print(${pwll_res[0]} < ${pwll_resi[0]})")
      if [ "$cmp_res" == True ]
      then
          echo "${pwll_res[0]} ${pwll_resi[0]} "
          pwll_res=(${pwll_resi[@]})
      fi
      onpl_resi=($(cat oneplone/Time_1+1_0${i}.csv | tail -3))
      cmp_res=$(python3 -c "print(${onpl_res[0]} < ${onpl_resi[0]})")
      if [ "$cmp_res" == True ]
      then
          onpl_res=(${onpl_resi[@]})
      fi
     done
   fi
   cd -
   echo -en "${pwll_res[0]},${pwll_res[1]},${pwll_res[2]} ,"   >> res_${2}.csv
   echo -en "${onpl_res[0]},${onpl_res[1]},${onpl_res[2]} ,"   >> res_${2}.csv
#    echo -en "${power_pwll},${power_plone}">> power_${2}.csv
   echo ""   >> res_${2}.csv
#    echo ""   >> power_${2}.csv

done
