# Artifacts for IEEE Transaction on Parallel and Distributed Systems (TPDS) Open Initiative

Paper Title: Faber a Hardware/Software Toolchain for Image Registration 
Authors: Eleonora D'Arnese, Davide Conficconi, Emanuele Del Sozzo, Luigi Fusco, Donatella Sciuto, Marco D. Santambrogio.
Affiliation: Politecnico di Milano

Paper Main Contributions:
* The first open-source HW/SW toolchain to automatically create custom Image Registration (IRG) pipelines exploiting FPGA-based accelerators.
* Three levels of customization hyperparameters to support users in building IRG pipelines
* A design automation methodology for non-FPGA experts to exploit default HW configurations as off-the-shelf SW
* A latency and resource model to guide HW expert users during the customization of the HW accelerators 

Faber achieves up to 54xin speedup and 177x in energy efficiency improvements over State of the Art

## Artifacts' Objectives

With this repo all the Faber's manuscript results can be reproduced:
* HW generation
* Single accelerator testing
* Resource prediction and actual usage extraction
* IRG application execution
* Accuracy Extraction
* Latency prediction
* State of the Art comparison

We exclude the biomedical dataset since it is open and available, as well as Matlab and SimpleITK applications, and to respect their intellectual property.
Please Artifact Evaluators contact us for more details or for ready to use setup.

## Testing Environment <a name="testing_env"></a>
1. We tested the hardware code generation on two different machines based on Ubuntu 18.04/20.4 and Centos OS 7.6 respectively.
2. We used Xilinx Vitis Unified Platform and Vivado HLx toolchains 2019.2.
3. We used Python 3 with `argparse` `numpy` `math` packets on the generation machine.
4. a) On the host machines, or hardware design machines, we used Pynq 2.5 on the Zynq based platforms (Pynq-Z2, Ultra96, Zcu104), where we employ `cv2`, `numpy`, `pandas`, `multiprocessing`, `statistics`, `argparse`, `pydicom`, and `scipy` packetes. For pure SW deployment the user will also need `torch` and `kornia` packets.
4. b) We tested the Alveo u200 on a machine with CentOS 7.6, i7-4770 CPU @ 3.40GHz, and 16 GB of RAM, and we installed Pynq 2.5.1 following the [instructions by the Pynq team](https://pynq.readthedocs.io/en/v2.5.1/getting_started/alveo_getting_started.html) with the same packets as point 4a.
5. [Optional] Possible issues with locale: export LANG="en_US.utf8".

## Artifact Installation and Deployment Process
1. Make sure to have installed Vitis and Vivado 2019.2, the Alveo u200 and the U96 devices, as well as Python 3 and its packages.
2. Follow the [PYNQ's team instruction to setup your devices](https://pynq.readthedocs.io/en/v2.5.1/) (Note: the FPGAs can be on a completly different place than the building system)
2. Clone the repo `https://github.com/necst/faber_fpga.git -b artifacts_tpds22`
3. Prepare the environment e.g., `source </my/path/to/xilinx/tools/Vitis/settings64.sh` and `source /opt/xilinx/xrt/setup.sh`
4. Start with one or alle the following reproduction steps
5. All the on-board executions refer to [Testing a HW Design](#testing_designs) or [Deployment Example and example of Dataset Structuring](#deploymentexample)

## Artifacts Reproduction
Follows all the possible manuscript reproduction instructions.

### Table 2: Performance analysis of the MI similarity metric with and without the HW transformation at 200MHz.
Expected time: consider 16 builds (12 Vitis 4-6 hours each; 4 Vivado 2-3 hours each) it is extremely machine dependent, and then the time to collect the results, Worst case 16\*5\*2 minutes..
1. Prepare the environment e.g., `source </my/path/to/xilinx/tools/Vitis/settings64.sh` and `source /opt/xilinx/xrt/setup.sh`
2. build the accelerators (i.e., `bash metric_w-wo_transform.bash`) 
3. check in `build/ultra96_v2` and `build/alveo_u200` the presence of a CSV with the resources of such builds
4. Deploy your solution according to [Testing a HW Design](#testing_designs)
5. To compute the performance values extract the run-time values and then apply for Powell's method `=(EXETIME*1000)/((246*512*512)/10^6)/(3*246)` for 1+1 `=(EXETIME*1000)/((246*512*512)/10^6)/(100*246)` since they employ generally different iterations (i.e., 3 for Powell's and 100 for 1+1).
6. For the Energy Efficiency the ZCU104 and the Alveo U200 have an example PYNQ-based code in `faber_fpga/src/sw/example_measurements` to collect the overall power consumption, while for the U96 we instrumented the plug of the device.

### Figure 6: Resource and FPS Scaling for defaults and image size scaling
Expected time: consider six builds (3 Vitis 4-6 hours each; 3 Vivado 2-3 hours each) it is extremely machine dependent, and then the time to collect the results (5/10 minutes).
1. Prepare the environment e.g., `source </my/path/to/xilinx/tools/Vitis/settings64.sh` and `source /opt/xilinx/xrt/setup.sh`
2. build the accelerators (i.e., `bash fps.bash`) 
3. check in `build/ultra96_v2` and `build/alveo_u200` the presence of a CSV with the resources of such builds
4. Deploy your solution according to [Testing a HW Design](#testing_designs)

### Figure 7, Figure 9: Execution Time, Model accuracy
Expected time: consider 8 builds (4 Vitis 4-6 hours each; 4 Vivado 2-3 hours each) it is extremely machine dependent, and then the time to collect the results , Worst case 8\*5\*2 minutes..
1. Prepare the environment e.g., `source </my/path/to/xilinx/tools/Vitis/settings64.sh` and `source /opt/xilinx/xrt/setup.sh`
2. build the accelerators (i.e., `bash build_top_bits.bash`) 
3. check in `build/ultra96_v2` and `build/alveo_u200` the presence of a CSV with the resources of such builds
4. Deploy your solution according to [Testing a HW Design](#testing_designs)
5. To compute the performance values extract the run-time values and then apply for Powell's method `=(EXETIME*1000)/((246*512*512)/10^6)/(3*246)` for 1+1 `=(EXETIME*1000)/((246*512*512)/10^6)/(100*246)` since they employ generally different iterations (i.e., 3 for Powell's and 100 for 1+1).
6. For the Energy Efficiency the ZCU104 and the Alveo U200 have an example PYNQ-based code in `faber_fpga/src/sw/example_measurements` to collect the overall power consumption, while for the U96 we instrumented the plug of the device.
7. For the model evaluation `bash evaluate_model.bash` and check the results in that folder (i.e., files `*.log`)
 

### Table 4: State of the Art comparison table
Expected time: consider 9 builds (4 Vitis 4-6 hours each; 5 Vivado 2-3 hours each) it is extremely machine dependent, and then the time to collect the results for each build, Worst case 9\*5\*2 minutes.
1. Prepare the environment e.g., `source </my/path/to/xilinx/tools/Vitis/settings64.sh` and `source /opt/xilinx/xrt/setup.sh`
2. build the accelerators (i.e., `bash build_soa.bash` or if done the previous step `cd ..; make hw_gen PE=1 CORE_NR=3 TARGET=hw CLK_FRQ=200 TRGT_PLATFORM=zcu104 METRIC="mse" TRANSFORM="wax"; cd -`) 
3. check in `build/ultra96_v2` and `build/alveo_u200` the presence of a CSV with the resources of such builds
4. Deploy your solution according to [Testing a HW Design](#testing_designs)
5. To compute the performance values extract the run-time values and then apply for Powell's method `=(EXETIME*1000)/((246*512*512)/10^6)/(3*246)` for 1+1 `=(EXETIME*1000)/((246*512*512)/10^6)/(100*246)` since they employ generally different iterations (i.e., 3 for Powell's and 100 for 1+1).
6. For the Energy Efficiency the ZCU104 and the Alveo U200 have an example PYNQ-based code in `faber_fpga/src/sw/example_measurements` to collect the overall power consumption, while for the U96 we instrumented the plug of the device.

### Table 3: Accuracy Evaluation
Expected time: consider 4 builds (4 Vitis 4-6 hours each or 4 Vivado 2-3 hours each) it is extremely machine dependent, and then the time to collect the results for each build, Worst case 4\*5\*2 minutes.

1. Prepare the environment e.g., `source </my/path/to/xilinx/tools/Vitis/settings64.sh` and `source /opt/xilinx/xrt/setup.sh`
2. Build and execute on whatever kind of platform the accelerators for every similarity metric without the transform (e.g., for the ALVEO with 1 PE `bash accuracy_eval.bash`, otherwise the one of the previous build)
3. check in `build/ultra96_v2` and `build/alveo_u200` the presence of a CSV with the resources of such builds
4. Deploy your solution according to [Testing a HW Design](#testing_designs)
5. Execute the `src/sw/res_extraction.py` to extract the single image accuracy and then compute the average (e.g., `python3 res_extreaction.py -f 0 -rg <path/to/gold/images/folder> -rt <where/to/find/registered/images> -l <optimizer_label> -rp <where/to/store/results>`).


### Testing a HW Design <a name="testing_designs"></a>

1. Complete at least one design in the previous section, and prepare the HW design for deployment (i.e., `make resyn_extr_zynq_ultra96_v2 ` or `make resyn_extr_vts_alveo_u200`, done by all the bash for the artifacts).
2. `make pysw` creates a deploy folder for the Python code.
3. `make deploybitstr` or `make deployxclbin` `BRD_IP=<target_ip> BRD_USR=<user_name_on_remote_host> BRD_DIR=<path_to_copy>` copy onto the deploy folders the needed files.
4. connect to the remote device, i.e., via ssh `ssh <user_name_on_remote_host>@<target_ip>`.
5. [Optional] install all needed Python packages as above, or the pynq package on the Alveo host machine.
6. Navigate to the `<path/where/deployed>/sw_py`.
7. 
    * 7a) Launch the script `python_tester_launcher.sh <path/where/deployed>/bitstream_ultra96` (or where you transferred the folder of the .bit) for the Ultra96 testing.
    * 7b) Modify the script with PLATFORM=Alveo, and launch the script `python_tester_launcher.sh <path/where/deployed>/xclbn_alveo_u200` (or where you transfered the folder of the .xclbin) for the Alveo testing.
    * 7c) the script will automatically detect the accelerator configuraiton (based on the folder name) and setup the testing of both, single accelerator, powell's, and 1+1 registrations, with a dataset structured as [descirbed here](#dataset_description).
8. `python_tester_extractor.sh <path/where/deployed>/bitstream_ultra96 <name for the csv result>` to automatically derive a .csv with most of the useful results of the experimental campaign.

If you wish to have a **single test of the accelerator** for a single bitstream please follow these steps after previous step 6.
7. set `BITSTREAM=<path_to_bits>`, `CLK=200`, `CORE_NR=<target_core_numbers>`, `PLATFORM=Alveo|Zynq`, `RES_PATH=path_results`, and source xrt on the Alveo host machine,  e.g., `source /opt/xilinx/xrt/setup.sh`.
8. [Optional] `python3 test-single-mi.py --help` for a complete view of input parameters.
9. Execute the test `python3 test-single-mi.py -ol $BITSTREAM -clk $CLK -t $CORE_NR -p $PLATFORM -im 512 -rp $RES_PATH` (if on Zynq you will need `sudo`).

To execute a **single registration**, follow similar steps such as the previous single accelerator test, or [have a look here](#deploymentexample).
`python3 faber-powell-blocked.py --help` will show a complete view of input parameters for powell HW-based registration procedure.


### <a name="deploymentexample"></a>  Deployment Example on Ultra96/Alveo u200/ Pure SW
An example of deployment is `make deploybitstr TRGT_PLATFORM=ultra96_v2 BRD_USR=xilinx BRD_IP=<board ip> BRD_DIR=/home/xilinx/faber` on the Ultra96.
For an Alveo u200 device `make deployxclbin TRGT_PLATFORM=alveo_u200 BRD_USR=<machine user> BRD_IP=<server ip> BRD_DIR=<path of where to deploy>`.

Connect to the host machine and go the target folder.