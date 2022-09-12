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
#
#
#
#/***************************************************************
#   TCL for project creation
#***************************************************************/


if {$argc < 7} {
  puts "Expected: <prj_root> <proj name> <proj dir> <ip_dir> <freq> <core_nr> <core_name> <wrapper_name>"
  exit
}


proc string_insert {prefix suffix core_number} \
{
    set ret ${prefix}${core_number}${suffix}
    return "${ret}"
}

proc core_add_19 {core_number trgt_freq core_name} \
{
    set axi_port [expr ${core_number} + 0]
    set axi_master 0
    puts "\[INFO\] TCL-19 Axi port: ${axi_port} and core_nr ${core_number}"
    create_bd_cell -type ip -vlnv xilinx.com:hls:${core_name}:1.0 ${core_name}_${core_number}
    set_property -dict [list CONFIG.PCW_USE_S_AXI_HP${axi_port} {1}] [get_bd_cells processing_system7_0]
	set_property -dict [list CONFIG.PCW_USE_M_AXI_GP${axi_port} {1} ] [get_bd_cells processing_system7_0]

    set v1_0 /processing_system7_0/M_AXI_GP${axi_master}
    set v2_0 /${core_name}_${core_number}/s_axi_control
    set v2_1 /${core_name}_${core_number}/m_axi_gmem0
    set v2_2 /${core_name}_${core_number}/m_axi_gmem1
    set v2_3 /${core_name}_${core_number}/m_axi_gmem2
    set v1_1 /processing_system7_0/S_AXI_HP${core_number}
    set clk "/processing_system7_0/FCLK_CLK0 (${trgt_freq} MHz)"

	apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config [list  Clk_master {Auto} Clk_slave {Auto} Clk_xbar {Auto} Master $v1_0 Slave $v2_0 ddr_seg {Auto} intc_ip {New AXI Interconnect} master_apm {0} ]  [get_bd_intf_pins ${core_name}_${core_number}/s_axi_control]
	apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config [list  Clk_master {Auto} Clk_slave {Auto} Clk_xbar {Auto} Master $v2_1 Slave $v1_1 ddr_seg {Auto} intc_ip {New AXI Interconnect} master_apm {0} ]  [get_bd_intf_pins processing_system7_0/S_AXI_HP${core_number}]

	apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config [list   Clk_master $clk Clk_slave $clk Clk_xbar $clk Master $v2_2 Slave $v1_1 ddr_seg {Auto} intc_ip {/axi_mem_intercon} master_apm {0} ] [get_bd_intf_pins ${core_name}_${core_number}/m_axi_gmem1]
	apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config [list Clk_master $clk Clk_slave $clk Clk_xbar $clk Master $v2_3 Slave $v1_1 ddr_seg {Auto} intc_ip {/axi_mem_intercon} master_apm {0} ]  [get_bd_intf_pins ${core_name}_${core_number}/m_axi_gmem2]
}


proc core_add_18 {core_number trgt_freq core_name} \
{

    set axi_port [expr ${core_number} + 0]
    set axi_master 0

    puts "\[INFO\] TCL-18 Axi port: ${axi_port} and core_nr ${core_number}"

    create_bd_cell -type ip -vlnv xilinx.com:hls:${core_name}:1.0 ${core_name}_${core_number}
    set_property -dict [list CONFIG.PCW_USE_M_AXI_GP${axi_port} {1}] [get_bd_cells processing_system7_0]
    set_property -dict [list CONFIG.PCW_USE_S_AXI_HP${axi_port} {1}] [get_bd_cells processing_system7_0]

    set v1_0 /processing_system7_0/M_AXI_GP${axi_master}
    set v2_0 /${core_name}_${core_number}/s_axi_control
    set v2_1 /${core_name}_${core_number}/m_axi_gmem0
    set v2_2 /${core_name}_${core_number}/m_axi_gmem1
    set v2_3 /${core_name}_${core_number}/m_axi_gmem2
    set v1_1 /processing_system7_0/S_AXI_HP${core_number}
    set clk "/processing_system7_0/FCLK_CLK0 (${trgt_freq} MHz)"

    apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config [list Clk_master {Auto} Clk_slave {Auto} Clk_xbar {Auto} Master $v1_0 Slave $$v2_0 intc_ip {New AXI Interconnect} master_apm {0} ] [get_bd_intf_pins ${core_name}_${core_number}/s_axi_control]
    apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config [list Clk_master {Auto} Clk_slave {Auto} Clk_xbar {Auto} Master $v2_1 Slave $v1_1 intc_ip {Auto} master_apm {0} ] [get_bd_intf_pins processing_system7_0/S_AXI_HP${core_number}]

    apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config [list Clk_master $clk Clk_slave $clk Clk_xbar $clk Master $v2_2 Slave $v1_1 intc_ip {/axi_smc} master_apm {0} ]  [get_bd_intf_pins ${core_name}_${core_number}/m_axi_gmem1]
    apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config [list Clk_master $clk Clk_slave $clk Clk_xbar $clk Master  $v2_3  Slave $v1_1 intc_ip {/axi_smc} master_apm {0} ]  [get_bd_intf_pins ${core_name}_${core_number}/m_axi_gmem2]



}



set prj_root  [lindex $argv 0]
set prj_root_build "$prj_root/build/"
set prj_name [lindex $argv 1]
set prj_dir [lindex $argv 2]
set ip_dir [lindex $argv 3]
set trgt_freq [lindex $argv 4]
set core_nr [lindex $argv 5]
set core_name [lindex $argv 6]
set wrapper_name [lindex $argv 7]

puts "\[TCL INFO\] Core Name $core_name"
puts "\[TCL INFO\] Block Design and wrapper name $wrapper_name"
if {$core_nr > 4} {
    puts "\[TCL Error\] cannot handle more than 4 core"
    exit
}
# fixed for platform
set prj_part "xc7z020clg400-1"
#unused
#set xdc_dir "$prj_root/src/scripts/pynqz2/building"

puts "$ip_dir"
#puts "$xdc_dir"
# set up project
create_project -force $prj_name $prj_dir -part $prj_part
update_ip_catalog

set_property board_part tul.com.tw:pynq-z2:part0:1.0 [current_project]

#Add PYNQZ2 XDC
#add_files -fileset constrs_1 -norecurse "${xdc_dir}/pynqz2.xdc"
update_compile_order -fileset sources_1

 
#add hls ip
set_property  ip_repo_paths $ip_dir [current_project]
update_ip_catalog

# create block design
create_bd_design "${wrapper_name}"


set vvd_version [version -short]
set vvd_version_split [split $vvd_version "."]
set vvd_vers_year [lindex $vvd_version_split 0]
#if the preset is present is useless right now
if {$vvd_vers_year < 2019} {
    create_bd_cell -type ip -vlnv xilinx.com:ip:processing_system7:5.5 processing_system7_0
} else {
    create_bd_cell -type ip -vlnv xilinx.com:ip:processing_system7:5.5 processing_system7_0
}

apply_bd_automation -rule xilinx.com:bd_rule:processing_system7 -config {make_external "FIXED_IO, DDR" apply_board_preset "1" Master "Disable" Slave "Disable" }  [get_bd_cells processing_system7_0]
regenerate_bd_layout

set_property -dict [list CONFIG.PCW_FPGA0_PERIPHERAL_FREQMHZ $trgt_freq] [get_bd_cells processing_system7_0]
set actual_freq [get_property CONFIG.FREQ_HZ [get_bd_pins processing_system7_0/FCLK_CLK0] ]
set actual_freq_mhz [expr $actual_freq / 1000000]
puts ""
puts ""
puts "***********************************************************************"
puts "  \[UTILS\] Targeting ${trgt_freq} MHz getting ${actual_freq_mhz} MHz "
puts "***********************************************************************"
puts ""
puts ""
puts ""


##########
#for each core setup the block design
#HP maximum of 4 :D

puts $core_nr
puts $vvd_vers_year
for {set i 0} {$i < $core_nr} {incr i} {
    puts $i
    if {$vvd_vers_year < 2019} {
        core_add_18 $i $actual_freq_mhz $core_name
    } else {
        core_add_19 $i $actual_freq_mhz $core_name
    }
}

regenerate_bd_layout
validate_bd_design
save_bd_design

# create HDL wrapper
make_wrapper -files [get_files $prj_dir/$prj_name.srcs/sources_1/bd/${wrapper_name}/${wrapper_name}.bd] -top
add_files -norecurse $prj_dir/$prj_name.srcs/sources_1/bd/${wrapper_name}/hdl/${wrapper_name}_wrapper.v
update_compile_order -fileset sources_1
update_compile_order -fileset sim_1

set_property source_mgmt_mode None [current_project]
set_property top ${wrapper_name}_wrapper [current_fileset]
set_property source_mgmt_mode All [current_project]
update_compile_order -fileset sources_1

set_property strategy Flow_PerfOptimized_high [get_runs synth_1]

set_property STEPS.SYNTH_DESIGN.ARGS.DIRECTIVE AlternateRoutability [get_runs synth_1]
set_property STEPS.SYNTH_DESIGN.ARGS.RETIMING true [get_runs synth_1]

set_property strategy Performance_ExtraTimingOpt [get_runs impl_1]
set_property STEPS.OPT_DESIGN.ARGS.DIRECTIVE Explore [get_runs impl_1]
set_property STEPS.POST_ROUTE_PHYS_OPT_DESIGN.ARGS.DIRECTIVE AggressiveExplore [get_runs impl_1]
set_property STEPS.PHYS_OPT_DESIGN.ARGS.DIRECTIVE AggressiveExplore [get_runs impl_1]
set_property STEPS.POST_ROUTE_PHYS_OPT_DESIGN.IS_ENABLED true [get_runs impl_1]
set_property STEPS.ROUTE_DESIGN.ARGS.DIRECTIVE AlternateCLBRouting [get_runs impl_1]
set_property STEPS.OPT_DESIGN.ARGS.DIRECTIVE ExploreWithRemap [get_runs impl_1]

write_bd_tcl -force $prj_dir/${wrapper_name}_wrapper.tcl
