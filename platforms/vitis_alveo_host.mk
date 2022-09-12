# #################TODO##################
# # #Host code
# HOST_SRC=$(HOSTCPP_DIR)/alveo/warptransform_host_alveo.cpp $(HOSTCPP_DIR)/alveo/xcl2/xcl2.cpp $(HLS_DIR)/$(TOP_FILE_NAME)
# HOST_HDRS= $(wildcard $(HOSTCPP_DIR)/alveo/*.hpp)

# HOST_CFLAGS= -std=c++14 -fPIC
# HOST_CFLAGS += -g  -D__SDSVHLS__ -DHLS_NO_XIL_FPO_LIB -DVIVADO_HLS_SIM  -I${XILINX_XRT}/include/ \
# 	-I $(HOSTCPP_DIR)/alveo/xcl2 \
# 	-I ${HLS_DIR}/ \
# 	-I ${HLS_DIR}/include \
# 	-I$(XILINX_XRT)/include -I$(XILINX_VIVADO)/include
#  	 #-O3 -I${XILINX_VITIS}/include/ --std=c++1y


# HOST_LFLAGS=-L${XILINX_XRT}/lib/ -lxilinxopencl -pthread \
# -L/xilinx/software/Vivado/2019.2/lnx64/tools/opencv/opencv_gcc/ \
# -lopencv_core -lopencv_imgproc -lopencv_highgui -lopencv_calib3d \
# -lopencv_features2d -lopencv_flann -L/xilinx/software/Vivado/2019.2/lnx64/tools/fpo_v7_0 \
# -Wl,--as-needed -lgmp -lmpfr -lIp_floating_point_v7_0_bitacc_cmodel 
# #-lopencv_core -lopencv_highgui -lopencv_imgproc \
# # 	-L$(XILINX_VITIS)/lnx64/tools/opencv


# ifndef LD_LIBRARY_PATHVTS_DST_DIR
#  	LD_LIBRARY_PATH=$(XILINX_VITIS)/lnx64/tools/opencv:/usr/lib/:/usr/local/lib64/:$(XILINX_VIVADO)/lnx64/tools/opencv/opencv_gcc:/usr/lib64/
# else
#  	LD_LIBRARY_PATH=$(LD_LIBRARY_PATH):$(XILINX_VITIS)/lnx64/tools/opencv:/usr/lib:/usr/local/lib64/:/usr/lib64/
# endif

# ifeq (,$(LD_LIBRARY_PATH))
# LD_LIBRARY_PATH = $(XILINX_XRT)/lib
# else
# LD_LIBRARY_PATH = $(XILINX_XRT)/lib:$(LD_LIBRARY_PATH)
# endif
# ifneq (,$(wildcard $(XILINX_VITIS)/bin/ldlibpath.sh))
# export LD_LIBRARY_PATH = $(shell $(XILINX_VITIS)/bin/ldlibpath.sh $(XILINX_VITIS)/lib/lnx64.o):$(LD_LIBRARY_PATH)
# endif

# #name of host executable
# HOST_EXE=$(KERNEL)_host_exe
# #argument passed to the execution of the kernel
# HOST_ARGS=$(KERNEL_EXE).xclbin ~/warpaffine/testdingo.png
# ################ENDTODO################

host:  check_TARGET $(HOST_SRC) $(HOST_HDRS)
	mkdir -p $(VTS_DST_DIR)
	$(XCC) $(HOST_SRC) $(HOST_HDRS) $(HOST_CFLAGS) $(HOST_LFLAGS) \
 	-o $(VTS_DST_DIR)/$(HOST_EXE)