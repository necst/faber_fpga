#######################################################################################################################################
#
#   Basic Makefile for Vitis 2019.2
#   Davide Conficconi, Emanuele Del Sozzo
#   {davide.conficconi, emanuele.delsozzo}@polimi.it
#
# 
#  See https://www.xilinx.com/html_docs/xilinx2019_2/vitis_doc/Chunk1193338764.html#wrj1504034328013
#  for more information about Vitis compiler options:) 
#######################################################################################################################################
CORE_LIST_NR = $(shell seq 1 ${CORE_NR})
include platforms/alveo_u200_hw.mk
#BRD_PARTS= "xcu200-fsgd2104-2-e"
#
#TARGET_DEVICE=xilinx_u200_xdma_201830_2
# TARGET DSA # 

#kernel
#TODO for TX
KERNEL_SRC=$(HLS_CURR_DIR)/$(TOP_FILE_NAME).cpp
KERNEL_HDRS= $(HLS_CURR_DIR)/
KERNEL_SRC_CONFIG = $(HLS_CONFIG_DIR)/$(TOP_FILE_NAME).cpp
KERNEL_HDRS_CONFIG = $(HLS_CONFIG_DIR)/
KERNEL_FLAGS= -D USING_XILINX_VITIS ${CUSTOM_VTS_KRNL_PARAMS} -I $(HLS_DIR)
KERNEL_EXE=$(TOP_LVL_FN)
KERNEL_NAME=$(TOP_LVL_FN)

#######################################################

 XO_LIST = $(foreach core, $(CORE_LIST_NR), $(VTS_DST_DIR)/$(KERNEL_NAME)_$(core).xo )


#Port mapping for Vitis version up to 2019.2 and other advanced options
krnl_map_lcdlflags = --connectivity.nk $(KERNEL_NAME)_$(1):1 \
	--connectivity.sp $(KERNEL_NAME)_$(1)_1.m_axi_gmem0:DDR[$(2)] \
	--connectivity.sp $(KERNEL_NAME)_$(1)_1.m_axi_gmem1:DDR[$(2)] \
	--connectivity.sp $(KERNEL_NAME)_$(1)_1.m_axi_gmem2:DDR[$(2)]

#advanced options not used
#   --connectivity.slr $(KERNEL_NAME)_$(1)_1:SLR$(3) \
#   --hls.memory_port_data_width 256
#	--hls.max_memory_ports $(KERNEL_NAME)_$(1) \
#--advanced.prop kernel.$(KERNEL_NAME)_$(1).kernel_flags="-std=c++11"

KRNL_LDCLFLAGS_MULTI_CORE = 

XO_GEN_FLAGS = -D KERNEL_NAME=$(TOP_LVL_FN)_$(1) ${CUSTOM_VTS_KRNL_PARAMS}

ifeq ($(CORE_NR),1)
KRNL_LDCLFLAGS_MULTI_CORE += $(call krnl_map_lcdlflags,1,0,0)
else ifeq ($(CORE_NR), 2)
KRNL_LDCLFLAGS_MULTI_CORE += $(call krnl_map_lcdlflags,1,0,0)
KRNL_LDCLFLAGS_MULTI_CORE += $(call krnl_map_lcdlflags,2,1,1)
else ifeq ($(CORE_NR), 3)
KRNL_LDCLFLAGS_MULTI_CORE += $(call krnl_map_lcdlflags,1,0,0)
KRNL_LDCLFLAGS_MULTI_CORE += $(call krnl_map_lcdlflags,2,1,1)
KRNL_LDCLFLAGS_MULTI_CORE += $(call krnl_map_lcdlflags,3,2,1)
else ifeq ($(CORE_NR), 4)
KRNL_LDCLFLAGS_MULTI_CORE += $(call krnl_map_lcdlflags,1,0,0)
KRNL_LDCLFLAGS_MULTI_CORE += $(call krnl_map_lcdlflags,2,1,1)
KRNL_LDCLFLAGS_MULTI_CORE += $(call krnl_map_lcdlflags,3,2,1)
KRNL_LDCLFLAGS_MULTI_CORE += $(call krnl_map_lcdlflags,4,3,2)
endif

include platforms/vitis_alveo.mk
