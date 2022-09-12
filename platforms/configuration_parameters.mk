#/******************************************
#*MIT License
#*
#*Copyright (c) [2022] [Eleonora D'Arnese, Davide Conficconi, Emanuele Del Sozzo, Luigi Fusco, Donatella Sciuto, Marco Domenico Santambrogio]
#*
#*Permission is hereby granted, free of charge, to any person obtaining a copy
#*of this software and associated documentation files (the "Software"), to deal
#*in the Software without restriction, including without limitation the rights
#*to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#*copies of the Software, and to permit persons to whom the Software is
#*furnished to do so, subject to the following conditions:
#*
#*The above copyright notice and this permission notice shall be included in all
#*copies or substantial portions of the Software.
#*
#*THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#*IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#*FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#*AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#*LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#*OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#*SOFTWARE.
#*/
########################################################à
#Configuration stuffs
D=512
IB=8
HT=float
PE=2
BV=0
ACC_SIZES=16
PE_ENTROP=1
CACHING=false
URAM=false
METRIC=
#SUPPORTED_METRICS=( mi mse cc prz )
TRANSFORM=
#wax
RGB=false
WAX_URAM=false
TX_TYPE=affine
# perspective for defining the param
INTERP_TYPE=nearestn
# bilinear for defining the param
NUM_STORE_ROWS=100
NUM_START_PROC=50
CONF_RGB=f
CONF_WAX_URAM=f
CONF_TX_TYPE=affn
CONF_INTERP_TYPE=nn

OPTIMZER=
#plone powell
###TO ADD in the params
PORT_NR = 3
CORE_NR = 1

##############################################################
#Do not touch from here onwards :)
#Unless you are willing to modify Faber toolchain behavior
# and you know what you are doing.
#
CONFIG_FILE_NAME=
TOP_FILE_NAME=

GEN_CONFIG_DESIGN_OPTS= -ib ${IB} -id ${D} 
CONF_CACHING=f
CONF_URAM=f

PRE_CURR_CONFIG=${TRANSFORM}${METRIC}-${CORE_NR}-${D}-${IB}
CURR_CONFIG=
CURR_METRIC_CONFIG=
CURR_TRANSFORM_CONFIG=

ifdef METRIC
GEN_CONFIG_DESIGN_OPTS += -muse -mtrc ${METRIC}
CURR_METRIC_CONFIG=-${HT}-${PE}-${PE_ENTROP}-${BV}-${ACC_SIZES}-${CONF_CACHING}-${CONF_URAM}
GEN_CONFIG_DESIGN_OPTS+= -ht ${HT} -pe ${PE} -bv ${BV} -es ${ACC_SIZES} -pen ${PE_ENTROP}

#assuming default false
ifeq "$(CACHING)" "true"
	GEN_CONFIG_DESIGN_OPTS += -mem
	CONF_CACHING=t
endif

#assuming default false
ifeq "$(URAM)" "true"
	GEN_CONFIG_DESIGN_OPTS += -uram
	CONF_URAM=t
endif
endif #// METRIC

#assuming default false
ifdef TRANSFORM
ifeq "$(RGB)" "true"
	GEN_CONFIG_DESIGN_OPTS += -rgb
	CONF_RGB=t
endif

#assuming default false
ifeq "$(WAX_URAM)" "true"
	GEN_CONFIG_DESIGN_OPTS += -wau
	CONF_WAX_URAM=t
endif

#assuming default affn
ifeq "$(TX_TYPE)" "perspective"
	GEN_CONFIG_DESIGN_OPTS += -txt
	CONF_TX_TYPE=prsp
endif

#assuming default nn
ifeq "$(INTERP_TYPE)" "bilinear"
	GEN_CONFIG_DESIGN_OPTS += -int
	CONF_INTERP_TYPE=bln
endif

	CURR_TRANSFORM_CONFIG=-${PE}-${NUM_STORE_ROWS}-${NUM_START_PROC}-${CONF_RGB}-${CONF_TX_TYPE}-${CONF_INTERP_TYPE}-${CONF_WAX_URAM}

	GEN_CONFIG_DESIGN_OPTS+= -pe ${PE} -nstrw ${NUM_STORE_ROWS} -nrwproc ${NUM_START_PROC}
endif # TRANSFORM
##############################################################


##############################################################
#Target boards 

TRGT_PLATFORM ?= ultra96_v2
GENERIC_TRGT_PLATFORM ?=zynq

SUPPORTED_ZYNQ_MPSOC=( ultra96_v2 zcu104 )
SUPPORTED_ZYNQ_SOC=( pynqz2 )
SUPPORTED_ALVEO=( alveo_u200 )
SUPPORTED_ZYNQ+=$(SUPPORTED_ZYNQ_SOC)
SUPPORTED_ZYNQ+=$(SUPPORTED_ZYNQ_MPSOC)

ifneq ($(filter $(TRGT_PLATFORM),$(SUPPORTED_ZYNQ_MPSOC)),)
    $(info $(TRGT_PLATFORM) exists in $(SUPPORTED_ZYNQ_MPSOC))
    GENERIC_TRGT_PLATFORM=zynq_mpsoc
else ifneq ($(filter $(TRGT_PLATFORM),$(SUPPORTED_ZYNQ_SOC)),)
    $(info $(TRGT_PLATFORM) exists in $(SUPPORTED_ZYNQ_SOC))
    GENERIC_TRGT_PLATFORM=zynq_soc
else ifneq ($(filter $(TRGT_PLATFORM),$(SUPPORTED_ALVEO)),)
    $(info $(TRGT_PLATFORM) exists in $(SUPPORTED_ALVEO))
    GENERIC_TRGT_PLATFORM=alveo
else
    $(info $(TRGT_PLATFORM) not supported)
    GENERIC_TRGT_PLATFORM=
endif

##############################################################



##############################################################
#TARGET METRICS
SUPPORTED_METRICS=( mi mse cc prz )
METRIC_CODE_VERSION=v2
EXTENDED_METRIC_NAME=
HLS_CURR_METRIC_DIR=
ifeq ($(METRIC),mi)
EXTENDED_METRIC_NAME=mutual_information
HLS_CURR_METRIC_DIR=$(HLS_METRICS_DIR)/$(EXTENDED_METRIC_NAME)
CONFIG_FILE_NAME=mutual_information.hpp
TOP_FILE_NAME=mutual_information
else ifeq ($(METRIC), mse)
EXTENDED_METRIC_NAME=mean_square_error
HLS_CURR_METRIC_DIR=$(HLS_METRICS_DIR)/$(EXTENDED_METRIC_NAME)/$(METRIC_CODE_VERSION)
CONFIG_FILE_NAME=mean_square_error.hpp
TOP_FILE_NAME=mean_square_error
else ifeq ($(METRIC), cc)
EXTENDED_METRIC_NAME=cross_correlation
HLS_CURR_METRIC_DIR=$(HLS_METRICS_DIR)/$(EXTENDED_METRIC_NAME)/$(METRIC_CODE_VERSION)
CONFIG_FILE_NAME=cross_correlation.hpp
TOP_FILE_NAME=cross_correlation
else ifeq ($(METRIC), prz)
EXTENDED_METRIC_NAME=parzen
HLS_CURR_METRIC_DIR=$(HLS_METRICS_DIR)/$(EXTENDED_METRIC_NAME)
CONFIG_FILE_NAME=parzen.hpp
TOP_FILE_NAME=parzen
else
ifndef TRANSFORM
$(info Apologize, Metric not supported)
endif
endif



####################################################################


SUPPORTED_TX=( wax )
EXTENDED_TRANSFORM_NAME=
ifeq ($(TRANSFORM),wax)

GEN_CONFIG_DESIGN_OPTS += -wax
EXTENDED_TRANSFORM_NAME=xf_warp_transform
HLS_CURR_TX_DIR=$(HLS_TX_DIR)/$(EXTENDED_TRANSFORM_NAME)
# wax specific stuffs
HLS_INCLUDES=$(HLS_DIR)/include -D__SDSVHLS__ -DHLS_NO_XIL_FPO_LIB
CONFIG_FILE_NAME=xf_warp_transform_config.hpp
TOP_FILE_NAME=xf_warp_transform_accel
else
$(info Apologize, Transform not supported)
endif
##############################################################
GEN_CONFIG_DESIGN_OPTS += -cfg $(CONFIG_FILE_NAME)
HLS_METRIC_TB_DIR=$(HLS_CURR_METRIC_DIR)/testbench
HLS_TRANSFORM_TB_DIR=$(HLS_CURR_TX_DIR)/testbench

HLS_CURR_MIX_DIR=$(HLS_DIR)/txmetric/${TRANSFORM}_${METRIC}
HLS_MIXED_TB_DIR=$(HLS_CURR_MIX_DIR)/testbench

#############################################################

#######################################################
#hls stuffs


hls_curr_metric_code = $(wildcard $(HLS_CURR_METRIC_DIR)/*.cpp)
hls_curr_metric_code += $(wildcard $(HLS_CURR_METRIC_DIR)/*.hpp)
hls_curr_metric_code += $(wildcard $(HLS_CURR_METRIC_DIR)/*.h)

hls_curr_tx_code = $(wildcard $(HLS_CURR_TX_DIR)/*.cpp)
hls_curr_tx_code += $(wildcard $(HLS_CURR_TX_DIR)/*.hpp)
hls_curr_tx_code += $(wildcard $(HLS_CURR_TX_DIR)/*.h)


hls_curr_mix_code = $(wildcard $(HLS_CURR_MIX_DIR)/*.cpp)
hls_curr_mix_code += $(wildcard $(HLS_CURR_MIX_DIR)/*.hpp)
hls_curr_mix_code += $(wildcard $(HLS_CURR_MIX_DIR)/*.h)
##############################################################
#TARGET OPTIMIZER
SUPPORTED_OPTIMIZER=( plone powell )
TRGT_OPTIMZR=${PY_ONPL}
ifeq ($(OPTIMZER),plone)
TRGT_OPTIMZR=${PY_PWL}
else ifeq ($(OPTIMZER), powell)
TRGT_OPTIMZR=${PY_PWL}
else
$(info Apologize, Optimizer not supported)
endif

####################################################################
# Faber combination code

HLS_TB_DIR=
HLS_TB_NAME=
HLS_TB=
hls_curr_tb=
hls_curr_header=
hls_curr_code=

TOP_LVL_FN=
CORE_NAME=
CUSTOM_VTS_KRNL_PARAMS=

ifdef METRIC
ifndef TRANSFORM
#Only Metric defined
$(info Metric $(METRIC) without a transform)
HLS_TB_DIR=$(HLS_METRIC_TB_DIR)
HLS_TB_NAME=hls_${METRIC}_testbench
HLS_TB=$(HLS_TB_DIR)/$(HLS_TB_NAME).cpp

hls_curr_tb = $(HLS_TB_DIR)/hls_${METRIC}_testbench.cpp
hls_curr_header = $(wildcard $(HLS_CURR_METRIC_DIR)/*.hpp)
hls_curr_header += $(wildcard $(HLS_CURR_METRIC_DIR)/*.h)
hls_curr_code += $(hls_curr_metric_code)

TOP_LVL_FN=$(EXTENDED_METRIC_NAME)_master
CORE_NAME=$(EXTENDED_METRIC_NAME)_master
CURR_CONFIG=${PRE_CURR_CONFIG}${CURR_METRIC_CONFIG}
HLS_CURR_DIR=$(HLS_CURR_METRIC_DIR)
CUSTOM_VTS_KRNL_PARAMS=
else # ndef  TRANSFORM

#Mixed Case
$(info Mixed Metric Transform)


HLS_TB_DIR=$(HLS_MIXED_TB_DIR)
HLS_TB_NAME=hls_${TRANSFORM}_${METRIC}_testbench
HLS_TB=$(HLS_TB_DIR)/$(HLS_TB_NAME).cpp

hls_curr_tb = $(HLS_TB_DIR)/hls_${TRANSFORM}_${METRIC}_testbench.cpp
hls_curr_header = $(wildcard $(HLS_CURR_MIX_DIR)/*.hpp)
hls_curr_header += $(wildcard $(HLS_CURR_MIX_DIR)/*.h)
hls_curr_code += $(hls_curr_tx_code)
hls_curr_code += $(hls_curr_metric_code)
hls_curr_code += $(hls_curr_mix_code)
TOP_FILE_NAME=${TRANSFORM}_${METRIC}
TOP_LVL_FN=${TRANSFORM}_${METRIC}_accel
CORE_NAME=${TRANSFORM}_${METRIC}_accel
CURR_CONFIG=${PRE_CURR_CONFIG}${CURR_METRIC_CONFIG}${CURR_TRANSFORM_CONFIG}
HLS_CURR_DIR=$(HLS_CURR_MIX_DIR)
CUSTOM_VTS_KRNL_PARAMS=-D USING_XILINX_VITIS -D__SDSVHLS__ \
-DHLS_NO_XIL_FPO_LIB -I ${HLS_DIR}/include 

endif # ndef  TRANSFORM

else # def METRIC

ifndef TRANSFORM
$(info Apologize, but no tx no metric, currently combo not supported)
else# ndef  TRANSFORM
$(info Transform $(TRANSFORM) without a metric)

HLS_TB_DIR=$(HLS_TRANSFORM_TB_DIR)
HLS_TB_NAME=hls_${EXTENDED_TRANSFORM_NAME}_testbench
HLS_TB=$(HLS_TB_DIR)/$(HLS_TB_NAME).cpp

hls_curr_tb = $(HLS_TB_DIR)/hls_${EXTENDED_TRANSFORM_NAME}_testbench.cpp
hls_curr_header = $(wildcard $(HLS_CURR_TX_DIR)/*.hpp)
hls_curr_header += $(wildcard $(HLS_CURR_TX_DIR)/*.h)
hls_curr_code += $(hls_curr_tx_code)

TOP_LVL_FN=$(EXTENDED_TRANSFORM_NAME)_accel
CORE_NAME=$(EXTENDED_TRANSFORM_NAME)_accel
CURR_CONFIG=${PRE_CURR_CONFIG}${CURR_TRANSFORM_CONFIG}
HLS_CURR_DIR=$(HLS_CURR_TX_DIR)
CUSTOM_VTS_KRNL_PARAMS=-D USING_XILINX_VITIS -D__SDSVHLS__ \
-DHLS_NO_XIL_FPO_LIB -I ${HLS_DIR}/include 

endif# ndef  TRANSFORM
endif # def METRIC
####################################################################

hls_curr_code += $(HLS_DIR)/utils.hpp

hls_curr_tb_code += $(HLS_DIR)/utils_debug.hpp
hls_curr_tb_code += $(wildcard $(HLS_TB_DIR)/*.cpp)
hls_curr_tb_code += $(wildcard $(HLS_TB_DIR)/*_testbench.cpp)

HLS_CLK=10

################
hls_curr_code_filtered = $(filter-out $(hls_curr_tb_code), $(hls_curr_code))
#######################################################
hls_curr_vts_code= $(hls_curr_code)
#######################################################
#variables for hls gen
hls_gen_code = $(wildcard $(HLS_CONFIG_DIR)/*.cpp)
hls_gen_code += $(wildcard $(HLS_CONFIG_DIR)/*.hpp)
hls_gen_code += $(wildcard $(HLS_CONFIG_DIR)/*.h)
hls_tb_code_gen = $(wildcard $(HLS_CONFIG_DIR)/${HLS_TB_NAME}.cpp)
HLS_GEN_CODE_RUN_WITH_TB = $(shell echo $(HLS_CONFIG_DIR)/*pp )
HLS_GEN_CODE_RUN_WITH_TB +=  $(shell echo $(HLS_CONFIG_DIR)/*.h )
HLS_GEN_CODE_RUN = $(filter-out $(hls_tb_code_gen), $(HLS_GEN_CODE_RUN_WITH_TB))
