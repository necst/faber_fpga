#!/bin/bash

# /******************************************
# *MIT License
# *
# *Copyright (c) [2022] [Eleonora D'Arnese, Davide Conficconi, Emanuele Del Sozzo, Luigi Fusco, Donatella Sciuto, Marco Domenico Santambrogio]# *
#
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
synth_res_vitis() {
    config_fldr=$1
    platform=$2
    kernel_name=$3
    config_as_fldr=$4
    first_exe=$5
    config_paper=$6
    trgt_platform=$7
    cfile_name=$8 

    echo "yeah Vitis"
    echo "[Analyzing Vitis Build] $cfile_name $trgt_platform $first_exe"
    clock_file=./${config_fldr}/hw/${platform}/link/v++_link_${kernel_name}_guidance.html
    res_file=./${config_fldr}/hw/${platform}/link/imp/kernel_util_placed.rpt


    if [ -f "$clock_file" ]
    then
          echo "$config_as_fldr has a timing file :D"
    else
        echo "$config_as_fldr does not have a timing file"
        exit
    fi
    if [ -f "$res_file" ]
    then
          echo "$config_as_fldr has a placed and routed design"
    else
        exit
    fi
    clk_freq_mhz=$(cat $clock_file | grep MHz | grep "clkwiz_kernel_clk_out1 =" | sed "s/.*= //" | sed "s/ MHz//")
    resources=$(cat $res_file | grep "Used Resources" | sed "s/|\s*Used Resources\s*|\s*//" | sed -e "s/[][]//g" | sed "s/%\s|//g" | sed "s/\s\{1,5\}/,/g")

    if [ "$first_exe" == true ]
    then
        echo -en "Config,FMHz,LUT,LUTAsMem,REG,BRAM,URAM,DSP\n" > ${cfile_name}${trgt_platform}.csv

    fi 
    echo -en "$config_paper,$clk_freq_mhz,$resources\n" >> ${cfile_name}${trgt_platform}.csv
    #config_array=(${config_fldr//_/ });

}
##################
synth_res_zynq(){

    config_fldr=$1
    prj_fldr=$2
    prj_name=$3
    dseign_name=$4
    config=$5
    trgt_period=$6
    first_exe=$7
    cfile_name=$8
    trgt_platform=$9

    echo "is more a zynq :D"

    timing_file=./${config_fldr}/${prj_fldr}/${prj_name}.runs/impl_1/${dseign_name}_timing_summary_postroute_physopted.rpt
    util_file=./${config_fldr}/${prj_fldr}/${prj_name}.runs/impl_1/${dseign_name}_utilization_placed.rpt


    if [ -f "$timing_file" ]
    then
          echo "$config is here :D"
    else
        echo $dseign_name
        echo "No timing postroute file"
        exit
    fi
    prova=($(cat ${timing_file} | grep "Slack" | cut -d":" -f 2 | sed "s/\(\ \)*//"))

    slack_ns=${prova[5]/ns,/ }
    slack_ns_dot=${slack_ns/./,}

    final_period=$(python3 -c "print($trgt_period - $slack_ns)")

    clk_freq_mhz=$(python3 -c "print((1 / $final_period)*1000)")
    CLB=$(cat $util_file | grep "Slice LUTs" | sed "s/ *$//" | sed "s/|\s* Slice LUTs\s*|\s*//" | sed "s/|\s*0 |\s* [0-9]*\s*|\s*//" | sed "s/ |//"| sed "s/\s/,/")

    #if zynq MPSoC
    if [ -z "$CLB" ]
    then

    CLB=$(cat $util_file | grep "CLB LUTs" | sed "s/ *$//" | sed "s/|\s* CLB LUTs\s*|\s*//" | sed "s/|\s*0 |\s* [0-9]*\s*|\s*//" | sed "s/ |//"| sed "s/\s/,/")

    fi

    FF=$(cat $util_file | grep "Slice Registers" | head -1 | sed "s/ *$//" | sed "s/| \s*Slice Registers \s*|\s*//" | sed "s/|\s*0 |\s* [0-9]*\s*|\s*//" | sed "s/ |//" | sed "s/\s/,/")

    #if zynq MPSoC
    if [ -z "$FF" ]
    then

    FF=$(cat $util_file | grep "CLB Registers" | head -1 | sed "s/ *$//" | sed "s/| \s*CLB Registers \s*|\s*//" | sed "s/|\s*0 |\s* [0-9]*\s*|\s*//" | sed "s/ |//" | sed "s/\s/,/")

    fi

    BRAM=$(cat $util_file | grep "Block RAM Tile" | head -1 | sed "s/ *$//" | sed "s/| Block RAM Tile\s*|\s*//" | sed "s/|\s*0 |\s* [0-9]*\s*|\s*//" | sed "s/ |//" | sed "s/\s/,/")


    DSP=$(cat $util_file | grep "DSPs" | head -1 | sed "s/ *$//" | sed "s/| DSPs\s*|\s*//" | sed "s/|\s*0 |\s* [0-9]*\s*|\s*//" | sed "s/ |//" | sed "s/\s/,/")


    URAM=$(cat $util_file | grep "URAM" | head -1 | sed "s/ *$//" | sed "s/| URAM\s*|\s*//" | sed "s/|\s*0 |\s* [0-9]*\s*|\s*//" | sed "s/ |//" | sed "s/\s/,/")

    if [ "$first_exe" == true ]
    then 
        echo -en "Configuration,Freq_mhz,CLB,FF,BRAM,DSP,URAM\n" > ${cfile_name}${trgt_platform}.csv
    fi
    echo -en "$config_paper,$clk_freq_mhz,$CLB,$FF,$BRAM,$DSP,$URAM\n" >> ${cfile_name}${trgt_platform}.csv
}

##################

derive_kernel_name(){
    config_as_fldr=$1
    kernel_name=
    conf_asfldr_array=(${config_as_fldr//-/ });
    case ${conf_asfldr_array[0]} in
        "waxmi")
        kernel_name="wax_mi_accel"
        ;;
        "waxcc")
        kernel_name="wax_cc_accel"
        ;;
        "waxmse")
        kernel_name="wax_mse_accel"
        ;;
        "waxprz")
        kernel_name="wax_prz_accel"
        ;;
        "wax")
        kernel_name="xf_warp_transform_accel"
        ;;
        "mse")
        kernel_name="mean_square_error_master"
        ;;
        "mi")
        kernel_name="mutual_information_master"
        ;;
        "cc")
        kernel_name="cross_correlation_master"
        ;;
        "prz")
        kernel_name="parzen_master"
        ;;
        *)
        echo "[ERROR] unknown kernel type"
        exit     # unknown option
        ;;
    esac
    echo $kernel_name
} 

derive_meaningful_config_name(){
    config_as_fldr=$1
    config_fldr_regex=$2
    #echo ""
    #echo "$config_as_fldr and $config_fldr_regex"
# PRE_CURR_CONFIG=${TRANSFORM}${METRIC}-${CORE_NR}-${D}-${IB}
# CURR_METRIC_CONFIG=-${HT}-${PE}-${PE_ENTROP}-${BV}-${ACC_SIZES}-${CONF_CACHING}-${CONF_URAM}
# CURR_TRANSFORM_CONFIG=-${PE}-${NUM_STORE_ROWS}-${NUM_START_PROC}-${CONF_RGB}-${CONF_TX_TYPE}-${CONF_INTERP_TYPE}-${CONF_WAX_URAM}

    config_paper=
    conf_asfldr_array=(${config_as_fldr//-/ });
    CORE_NR=${conf_asfldr_array[1]}
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
    if [ ${conf_asfldr_array[9]} == "bln" ] || [ ${conf_asfldr_array[16]} == "bln" ];
    then
        it="bln"
    fi;
    wau=""
    if [ ${conf_asfldr_array[10]} == "t" ] || [ ${conf_asfldr_array[17]} == "t" ];
    then
        wau="WU"
    fi;

    case ${conf_asfldr_array[0]} in
        "waxprz"|"waxmi"|"waxcc"|"waxmse")
        str=${conf_asfldr_array[12]}
        config_paper="${CORE_NR}${conf_asfldr_array[0]}$cachings$urams$wau$datatype-$hpe-$epe-$it-$str-${conf_asfldr_array[2]}"
        ;;
        "wax")
        str=${conf_asfldr_array[5]}
        hpe=${conf_asfldr_array[4]}
        config_paper="${CORE_NR}${conf_asfldr_array[0]}$wau-$hpe-$it-$str-${conf_asfldr_array[2]}"

        ;;
        "prz"|"mse"|"mi"|"cc")
        config_paper="${CORE_NR}${conf_asfldr_array[0]}$cachings$urams$datatype-$hpe-$epe-${conf_asfldr_array[2]}"
        ;;
        *)
        echo "[ERROR] unknown kernel type"
        exit     # unknown option
        ;;
    esac
    echo "$config_paper"

}

derive_conf_list(){

    config_as_fldr=$1
    conf_asfldr_array=(${config_as_fldr//-/ });
    case ${conf_asfldr_array[0]} in
        "waxprz"|"waxmi"|"waxcc"|"waxmse")
        conf_list="TRANSFORM METRIC CORE_NR D IB HT PE PE_ENTROP BV ACC_SIZES CONF_CACHING CONF_URAM PE NUM_STORE_ROWS NUM_START_PROC CONF_RGB CONF_TX_TYPE CONF_TX_TYPE CONF_INTERP_TYPE CONF_WAX_URAM"
        ;;
        "wax")
        conf_list="TRANSFORM CORE_NR D IB PE NUM_STORE_ROWS NUM_START_PROC CONF_RGB CONF_TX_TYPE CONF_TX_TYPE CONF_INTERP_TYPE CONF_WAX_URAM"
        ;;
        "prz"|"mse"|"mi"|"cc")
        conf_list="METRIC CORE_NR D IB HT PE PE_ENTROP BV ACC_SIZES CONF_CACHING CONF_URAM"
        ;;
        *)
        echo "[ERROR] unknown kernel type"
        exit     # unknown option
        ;;
    esac
    echo "$conf_list"
}
##################
##################
##################
##################
##################
##################
##################
##################
##################
##################
##################
##################
##################
##################

echo "$@"
for i in "$@"
do
case $i in
    -cf=*|--config_fldr=*)
    config_fldr="${i#*=}"
    shift
    ;;
    -pb=*|--prep_bitstream=*)
    prep_bitstream="${i#*=}"
    shift
    ;;
    -v=*|--vitis=*)
    vitis="${i#*=}"
    shift
    ;;
    -tp=*|--trgt_platform=*)
    trgt_platform="${i#*=}"
    shift
    ;;
    -fe=*|--first_exe=*)
    first_exe="${i#*=}"
    shift
    ;;
    -fm=*|--freq_mhz=*)
    FREQ_MHZ="${i#*=}"
    shift
    ;;
    -vplt=*|--vitis_platform=*)
    vitis_platform="${i#*=}"
    shift
    ;;
    --default)
    DEFAULT=YES
    shift
    ;;
    *)
          # unknown option
    ;;
esac
done

if [ -z "$FREQ_MHZ" ]
then
    trgt_period=10
    echo "Not setted FREQ_MHZ"
else
    trgt_period=$(python3 -c "print((1 / $FREQ_MHZ)*1000)")
    echo "Setting Frequency to $FREQ_MHZ"
fi
prj_fldr="faber-vivado"
prj_name="faber-vivado"
dseign_name="faber_wrapper"

#platform="xilinx_u200_xdma_201830_2"
#kernel_name="mutual_information_master"


echo "current params are: $1 $2 $3 $4 $5 $6"
echo "config folder $config_fldr"
echo "prep bits $prep_bitstream"
echo "vitis $vitis"
echo "trgt $trgt_platform"
platform=$trgt_platform
echo "first exe $first_exe"
echo "freq mhz $FREQ_MHZ"



bitfilefldr=""
arrconfig=(${config_fldr//_/,}); 
config_separation=(${config_fldr//_/}); 

config=$arrconfig
cfile_name="config_res_mult"
config_as_fldr=$config_fldr
#config_fldr_regex="[0-9]-512-8-((float)|(fixed))-[0-9]+-[0-9]+-[0-9]-[0-9]+-((true|false))-((true|false))"
config_fldr_regex="[a-z]{2,6}-[0-4]-[0-9]+-8-(([a-z]+-[0-9]+-[0-9]+-[0-9]-[0-9]+(-(f|t))+))?(([0-9]+)+-(t|f)-[a-z]+-[a-z]{2,3}-(t|f))?"
echo "$config_as_fldr and $config_fldr_regex"
kernel_name=$(derive_kernel_name $config_as_fldr)
echo "Kernel Name $kernel_name"
if [ -d $config_fldr ]; 
    then 
        if [[ $config_as_fldr =~ $config_fldr_regex ]] ; 
        then 
            config_paper=$(derive_meaningful_config_name $config_as_fldr $config_fldr_regex)
            echo $config_paper
        else 
            echo "$config_fldr not a config fldr";
            exit
        fi;  
    else 
        echo "$config_fldr not a folder";
        exit
fi;


if [ "$vitis" == true ]
then
    synth_res_vitis $config_fldr $vitis_platform $kernel_name $config_as_fldr $first_exe $config_paper $trgt_platform $cfile_name
    bitfilefldr="xclbin_${trgt_platform}"


#end vitis
else
    synth_res_zynq $config_fldr $prj_fldr $prj_name $dseign_name $config $trgt_period $first_exe $cfile_name $trgt_platform
    bitfilefldr="bitstream_${trgt_platform}"

fi
#end if vitis

echo "check if need to prepare"


#conf_list=(CORE_NR D IB HT PE PE_ENTROP BV ACC_SZ CACHING URAM CODE_VERS)
echo "$config_as_fldr"

conf_list=( $(derive_conf_list $config_as_fldr) )
echo "${conf_list[@]}"
if [ "$prep_bitstream" == true ]
then
if [ "$vitis" == true ] 
then

xclbin_file=./${config_fldr}/hw/${vitis_platform}/${kernel_name}.xclbin

if [ -f "$xclbin_file" ]
then
      echo "there is an xclbin!"
else
    echo "there is NO xclbin :("
    exit
fi
 #mkdir -p  ~/../../shared_data/davide.conficconi/faber_bitstreams/xclbin_alveo_nags21/${config_fldr}
 #cp -R $xclbin_file   ~/../../shared_data/davide.conficconi/faber_bitstreams/xclbin_alveo_nags21/${config_fldr}/
mkdir -p ../${bitfilefldr}/${config_fldr}
cp -R $xclbin_file  ../${bitfilefldr}/${config_fldr}/
else #vitis

    bitstream_file=./${config_fldr}/${prj_fldr}/${prj_name}.runs/impl_1/${dseign_name}.bit
    deploy_dir=./${config_fldr}/deploy

    config_array=(${config_fldr//-/ });

    if [ -d "$deploy_dir" ]
    then
          echo "there is already a deploy dir is here :D"
    else
        conf_mk=(); 
        k=0; 
        for j in ${config_array[@]}; 
        do 
            if [[ $k == 0 ]]; then
                    case $j in
                    "waxprz"|"waxmi"|"waxcc"|"waxmse")
                         tmp1="${conf_list[$k]}=$(expr substr $j 1 3)";
                         ((k=k+1));
                         conf_mk+=($tmp1);
                         tmp1="${conf_list[$k]}=$(expr substr $j 4 3)";
                    ;;
                    "wax")
                        tmp1="${conf_list[$k]}=$j";
                        #conf_mk+=($tmp1);
                        #((k=k+1));
                        #tmp1=""
                    ;;
                    "prz"|"mse"|"mi"|"cc")
                        #tmp1="${conf_list[$k]}=''";
                        #conf_mk+=($tmp1);
                        #((k=k+1));
                        tmp1="${conf_list[$k]}=$j";
                    ;;
                    *)
                    echo "[ERROR] unknown kernel type"
                    exit     # unknown option
                    ;;
                esac
            else
                tmp1="${conf_list[$k]}=$j";
            fi
            echo $tmp1;
            conf_mk+=($tmp1); 
            ((k=k+1));
        done; 
        echo "reading the conf_mk"; 
        echo ${conf_mk[@]};
        echo ${config_array}; 
        cd ../../; make hw_pre ${conf_mk[@]} TRGT_PLATFORM=$platform; cd -
    fi
    #mkdir -p  ~/../../shared_data/davide.conficconi/faber_bitstreams/bitstream_ultra96_nags25/${config_fldr}
    #mv -f $deploy_dir/*  ~/../../shared_data/davide.conficconi/faber_bitstreams/bitstream_ultra96_nags21/${config_fldr}/
    mkdir -p ../${bitfilefldr}/${config_fldr}
    cp -R $deploy_dir/  ../${bitfilefldr}/${config_fldr}/
fi #vitis
fi #prep_bitstream

