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
#/***************************************************************
#*
#* Makefile
#*
#****************************************************************/

##############################################################
#directory stuffs
SHELL = /bin/bash
TOP := $(shell pwd)
MAIN_PRJ=faber

PYTHON=python3
##############################################################
#Directories stuff 
SRC_DIR=$(TOP)/src
BUILD_DIR=$(TOP)/build
BUILD_PLAT_DIR ?= ${BUILD_DIR}/${TRGT_PLATFORM}
CURR_BUILD_DIR=$(BUILD_PLAT_DIR)/$(CURR_CONFIG)
HLS_CONFIG_DIR ?= $(CURR_BUILD_DIR)/src/hls
VTS_BUILD_DIR ?= $(CURR_BUILD_DIR)


HLS_DIR=$(SRC_DIR)/hls
HLS_INCLUDES=
HLS_DIR_VTS=$(HLS_DIR)
HLS_METRICS_DIR=$(HLS_DIR)/metrics
HLS_TX_DIR=$(HLS_DIR)/transform

HLS_CURR_METRIC_DIR=
HLS_CURR_TX_DIR=
HLS_CURR_DIR=

SCRIPT_DIR=$(SRC_DIR)/scripts
DRVR_DIR=$(SRC_DIR)/driver
DEPLOY_DIR=$(CURR_BUILD_DIR)/deploy
SW_DIR=$(SRC_DIR)/sw
HOSTS_DIR=$(SRC_DIR)/hosts
PRJ_NAME?=faber-hls


#######################################################
include platforms/configuration_parameters.mk
#######################################################
#HLS stuffs

HLS_INCL ?= /xilinx/software/Vivado/2019.2/include
VIVADO_VERSION = $(shell vivado -version | grep Vivado)
VIVADO_SCRIPT_DIR ?= $(SCRIPT_DIR)/$(TRGT_PLATFORM)

#######################################################

HLS_CONF_LOGGER = hls_verification.csv
 

HLS_OPTS?=5 
# 0 for only project build; 1 for sim only; 2 synth; 3 cosim; 4 synth and ip downto impl; 5 synth and ip; 6 for ip export
#######################################################
#vivado stuffs
IP_REPO ?= $(CURR_BUILD_DIR)/$(PRJ_NAME)/solution1/impl/ip
VIVADO_MODE ?= batch # or gui
FREQ_MHZ ?= 150

KERNEL = faber
#######################################################

LD_LIBRARY_PATH:=$(LD_LIBRARY_PATH):/usr/local/lib64

ACCEL_GENERATOR=generator.py
#######################################################

#deploying parameters
BRD_IP?=192.168.3.1
BRD_DIR?=/home/xilinx/faber/
BRD_USR?=xilinx
#######################################################
DPLY_PY ?= $(BUILD_PLAT_DIR)/sw_py
APP_PY ?= $(BUILD_DIR)/app_py
PY_DIR = $(SW_DIR)/python
PY_MI ?= faber-single-mi.py
PY_PWL ?= faber-powell-blocked.py
PY_ONPL ?= faber-oneplusone-blocked.py
PY_WAXMI ?= faber-single-waxmi.py
PY_GENERIC = $(SW_DIR)/faberRegistratorsTorch.py
PY_GENERIC += $(PY_DIR)/faberImageRegistration.py
PY_OPTS ?= $(SW_DIR)/faberOptimizersTorch.py
PY_SW_PURE ?= $(SW_DIR)/fabersw-unique.py
######################################################
.PHONY:help test_recipes print_config gen_hls_config gen_hls_config_vts

help:
	@echo "*****************************************************************"
	@echo "*****************************************************************"
	@echo "*****************************************************************"
	@echo "                      Faber makefile helper                       "
	@echo "*****************************************************************"
	@echo "*****************************************************************"
	@echo "*****************************************************************"
	@echo ""
	@echo " [HELP] 'make' shows this helper"
	@echo ""
	@echo " [HELP] 'make print_config'  print Faber current config generation"
	@echo ""
	@echo " [HELP] 'make curr_config'  print Faber config generation parameters"
	@echo ""
	@echo "*****************************************************************"
	@echo ""
	@echo " [INFO] 'make all' prepare everything, sw, hls, hw"
	@echo ""
	@echo "[INFO] 'make gen_hls_config'  generate the HLS configuration "
	@echo "[INFO] 'make gen_hls_config_vts'  generate Vitis configuration"
	@echo ""
	@echo "*****************************************************************"
	@echo ""
	@echo " [INFO] extract specific board results"
	@echo " 'make resyn_extr_zynq_%' or 'make resyn_extr_vts_%'"
	@echo ""
	@echo "*****************************************************************"
	@echo ""
	@echo " [INFO] 'make deploy' copy the deployable to the target dir"
	@echo " default configuration: micro-usb addr 'BRD_URI?=192.168.3.1'"
	@echo " default target directory on the board 'BRD_DIR?=/home/xilinx/Faber/'"
	@echo ""
	@echo "*****************************************************************"
	@echo ""
	@echo "                     Clean utilities                             "
	@echo ""
	@echo "*****************************************************************"
	@echo ""
	@echo "[INFO] 'make cleanhls' cleans hls project "
	@echo "[INFO] 'make cleanvivado' cleans vivado project, only for Zynq"
	@echo "[INFO] 'make cleanreport' cleans everything in the report folder"
	@echo "[INFO] 'make cleanall' cleans everything in the build folder"
	@echo "[INFO] 'make cleanplat' cleans everything in the plat folder"
	@echo ""
	@echo ""
	@echo "*****************************************************************"
	@echo "*****************************************************************"
	@echo "*****************************************************************"
	@echo ""
	@echo "              End of general Faber makefile helper                "
	@echo ""
	@echo "*****************************************************************"
	@echo "*****************************************************************"
	@echo "*****************************************************************"
	@make helplat
	@make helparam
	@make helptargets



#######################################################
# platform-specific Makefile include for bitfile synthesis
include platforms/$(TRGT_PLATFORM).mk


################################################################
# HLS config stuffs
################################################################

print_config:
	@echo $(CURR_CONFIG)

copy_hls_code: check_accelerator
	mkdir -p $(HLS_CONFIG_DIR)
	cp -f $(hls_curr_code_filtered) $(HLS_CONFIG_DIR)
	cp -f $(hls_curr_tb) $(HLS_CONFIG_DIR)
	rm -f $(HLS_CONFIG_DIR)/*_testbench.cpp

check_accelerator:
ifndef METRIC
ifndef TRANSFORM
	$(error You must define either METRIC or TRANSFORM to generate an accelerator)
endif
endif

default_ultra96:
	make hw_gen D=${D} IB=${IB} OPTIMZER=plone TRGT_PLATFORM=ultra96_v2 \
	METRIC=cc TRANSFORM=wax PE=1 CORE_NR=2 FREQ_MHZ=200 HTYPS=float \
	CACHING=false URAM=false INTERP_TYPE=nearestn
	make pysw


default_alveo_u200:
	make hw_gen D=${D} IB=${IB} OPTIMZER=powell TRGT_PLATFORM=alveo_u200 \
	METRIC=mi PE=16 CORE_NR=1 PE_ENTROP=1 CACHING=false URAM=false\
	CLK_FRQ=300 TARGET=hw OPT_LVL=3
	make pysw

pure_sw:
	mkdir -p $(APP_PY)
	cp $(PY_GENERIC) $(APP_PY)/
	cp $(PY_SW_PURE) $(APP_PY)/
	cp $(PY_OPTS) $(APP_PY)/

#TODO
#I have some doubts about the copy and remove of tb code. might fix this :D
gen_hls_config: copy_hls_code
	$(PYTHON) $(SCRIPT_DIR)/generators/$(ACCEL_GENERATOR) -c -op $(HLS_CONFIG_DIR)/ $(GEN_CONFIG_DESIGN_OPTS)


gen_hls_config_vts:copy_hls_code
	$(PYTHON) $(SCRIPT_DIR)/generators/$(ACCEL_GENERATOR) -c -op $(HLS_CONFIG_DIR)/ $(GEN_CONFIG_DESIGN_OPTS) -vts

all: | sw hls hw

all_config : | sw hw_gen

resyn_extr_zynq_%:
	$(SCRIPT_DIR)/extract_all_synt_res.sh $* false true ${FREQ_MHZ}

resyn_extr_vts_%:
	$(eval include platforms/$*_hw.mk)
	echo $(TARGET_DEVICE)
	$(SCRIPT_DIR)/extract_all_synt_res.sh $* true true ${FREQ_MHZ} $(TARGET_DEVICE)

deploynewpy:
	mkdir -p $(BUILD_DIR)

deploy: deploypy
	rsync -avz $(DEPLOY_DIR) $(BRD_USR)@$(BRD_IP):$(BRD_DIR)

deploypy: pysw
	rsync -avz $(DPLY_PY) $(BRD_USR)@$(BRD_IP):$(BRD_DIR)

deploybitstr:deploypy
	rsync -avz $(BUILD_DIR)/bitstream_$(TRGT_PLATFORM) $(BRD_USR)@$(BRD_IP):$(BRD_DIR)

deployxclbin:deploypy
	rsync -avz $(BUILD_DIR)/xclbin_$(TRGT_PLATFORM) $(BRD_USR)@$(BRD_IP):$(BRD_DIR)

curr_config: print_config
	@echo $(GEN_CONFIG_DESIGN_OPTS)

## clean facilities
cleanconfig:
	rm -rf $(CURR_BUILD_DIR)

cleanvivado:
	rm -rf $(PRJDIR)

cleanhls:
	rm -rf $(CURR_BUILD_DIR)/$(PRJ_NAME)

cleanpysw:
	rm -rf $(DPLY_PY)

clean: cleanhls cleanvivado
	rm -f $(CURR_BUILD_DIR)/*.log $(CURR_BUILD_DIR)/*.jou


cleanplat:
	rm -rf $(BUILD_PLAT_DIR)/*

cleanall:
	rm -rf $(BUILD_DIR)/*

helparam:
	@echo ""
	@echo "*****************************************************************"
	@echo "" 
	@echo "                 Makefile parameters  helpers               "
	@echo ""
	@echo "*****************************************************************"
	@echo ""
	@echo " [INFO] using shell=$(SHELL), top directory=$(TOP)"
	@echo " [INFO] py version=$(PYTHON)"
	@echo ""
	@echo ""
	@echo " [PARAM] Image dimension (D) = $(D)"
	@echo " [PARAM] Image bit size (IB) = $(IB)"
	@echo " [PARAM] Computation type (HT) = $(HT)"
	@echo " [PARAM] Histogram PE (PE) = $(PE)"
	@echo " [PARAM] Entropy PE (PE_ENTROP) = $(PE_ENTROP)"
	@echo " [PARAM] Use caching (CACHING) = $(CACHING)"
	@echo " [PARAM] Use URAM caching (URAM) = $(URAM)"
	@echo " [PARAM] Core Number (CORE_NR) = $(CORE_NR)"
	@echo ""
	@echo " [PARAM] Similarity metric (METRIC) = $(METRIC)"
	@echo " [PARAM] Supported METRIC: $(SUPPORTED_METRICS)"
	@echo ""
	@echo " [PARAM] Image Transforamtion (TRANSFORM) = $(TRANSFORM)"
	@echo " [PARAM] Supported TRANSFORM: $(SUPPORTED_TX)"
	@echo ""
	@echo " [Help] Change those values for accelerator generation"
	@echo ""
	@echo ""
	@echo " [PARAM] HLS_CLK=$(HLS_CLK) clock period for hls"
	@echo " [PARAM] FREQ_MHZ=$(FREQ_MHZ) clock frequency for vivado bitstream"
	@echo ""
	@echo ""
	@echo "*****************************************************************"
	@echo "" 
	@echo "               END of Makefile parameters helper                     "
	@echo ""
	@echo "*****************************************************************"
	@echo ""


helptargets:
	@echo ""
	@echo "*****************************************************************"
	@echo "" 
	@echo "                 Target platforms helpers               "
	@echo ""
	@echo "*****************************************************************"
	@echo ""
	@echo " [HELP] Currently using Vivado version $(VIVADO_VERSION)"
	@echo ""
	@echo " [HELP] Supported Zynq boards: $(SUPPORTED_ZYNQ)"
	@echo ""
	@echo " [HELP] Supported Alveo boards: $(SUPPORTED_ALVEO)"
	@echo ""
	@echo " [HELP] add TRGT_PLATFORM=<one_of_the_previous_platform> to a command"
	@echo " [HELP] For example 'make TRGT_PLATFORM=zcu104'"
	@echo ""
	@echo "*****************************************************************"
	@echo "" 
	@echo "               END of Target platforms helpers                   "
	@echo ""
	@echo "*****************************************************************"
	@echo ""
