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
import argparse
import params
import math
from boards import resources

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

correction_factor = 1.067

bram_confs = [(18, 1024), (9, 2048), (4, 4096), (2, 8192), (1, 16384)]

class MetricEstimator():

	def __init__(self, num_cores, bitwidth, dimension, pe, caching, transform, interpolation, uram, platform):
		self.num_cores = num_cores
		self.bitwidth = bitwidth
		self.dimension = dimension
		self.pe = pe
		self.caching = caching
		self.transform = transform
		self.interpolation = interpolation
		self.uram = uram
		self.platform = platform
		self.metric = ''
		pass

	def compute_latency(self):
		pass

	def compute_resources(self):
		pass

	def _linear_function(self, x, slope, intercept):
		y = intercept + slope * x
		return y

	def _check_feasibility(self, bram, dsp, ff, lut, uram):
		feasible = True
		feasible = feasible and bram <= resources[self.platform]["bram18k"]
		feasible = feasible and dsp <= resources[self.platform]["dsp"]
		feasible = feasible and ff <= resources[self.platform]["ff"]
		feasible = feasible and lut <= resources[self.platform]["lut"]
		feasible = feasible and uram <= resources[self.platform]["uram"]
		return feasible

	def _count_bram_block(self, n_elem, bitwidth):
		if n_elem <= 512 and bitwidth <= 32:
			return 1
		curr = bitwidth
		blocks = 0
		for b, s in bram_confs:
			q = curr // b
			curr = curr % b
			curr_blocks = math.ceil(q * n_elem/ s)
			if curr_blocks % 2 == 1:
				curr_blocks += 1
			blocks += curr_blocks
		return blocks

	def _compute_bram(self):
		bram = math.ceil(self.bitwidth * self.pe / 36) # brams required for AXI Master port
		bram += math.ceil(32 / 36) # brams required for AXI-LITE port
		if self.caching == False:
			bram += math.ceil(self.bitwidth * self.pe / 36) # brams required for AXI Master port
		else:
			bram += 1 # brams required for caching interface
		if self.transform == True:
			transform_local_array_num = 4 # According to Xilinx's WarpTransform code
			transform_local_array_rows = (params.transform_store_rows + 3) >> 2 # According to Xilinx's WarpTransform code
			if self.interpolation == "nn":
				transform_additional_bram = 13 # According to Xilinx's WarpTransform code
			else: # bln
				transform_additional_bram = 25 # According to Xilinx's WarpTransform code
			transform_bram = self._count_bram_block(self.dimension, self.bitwidth) * transform_local_array_rows
			transform_bram *= transform_local_array_num
			transform_bram += transform_additional_bram
			bram += transform_bram
		return bram

	def _compute_dsp(self):
		if self.transform == True:
			dsp = self._linear_function(self.pe, params.dsp_slope[self.metric], params.dsp_intercept_base[self.metric][self.interpolation])
		else:
			dsp = self._linear_function(self.pe, params.dsp_slope[self.metric], params.dsp_intercept_base[self.metric])
		return math.ceil(dsp)

	def _compute_ff(self):
		if self.caching == True:
			ff_intercept = params.ff_caching_intercept
		else:
			ff_intercept = params.ff_intercept_base
		if self.transform == True:
			ff = self._linear_function(self.pe, params.ff_slope[self.metric], ff_intercept[self.metric][self.interpolation])
		else:
			ff = self._linear_function(self.pe, params.ff_slope[self.metric], ff_intercept[self.metric])
		return math.ceil(ff)

	def _compute_lut(self):
		if self.caching == True:
			lut_intercept = params.lut_caching_intercept
		else:
			lut_intercept = params.lut_intercept_base
		if self.transform == True:
			lut = self._linear_function(self.pe, params.lut_slope[self.metric], lut_intercept[self.metric][self.interpolation])
		else:
			lut = self._linear_function(self.pe, params.lut_slope[self.metric], lut_intercept[self.metric])
		return math.ceil(lut)

	def _compute_uram(self):

		uram = 0
		if self.caching and self.uram:
			cell_per_elem = math.ceil((self.bitwidth * self.pe) / 72)
			total_bits = self.dimension * self.dimension / self.pe * 72 * cell_per_elem
			uram = math.ceil(total_bits / (288 * 1024))
			
		return uram



class CCMetricEstimator(MetricEstimator):

	def __init__(self, num_cores, bitwidth, dimension, pe, caching, transform, interpolation, uram, platform):
		super().__init__(num_cores, bitwidth, dimension, pe, caching, transform, interpolation, uram, platform)
		if transform == True:
			self.metric = 'waxcc'
		else:
			self.metric = 'cc'

	def compute_latency(self):
		if self.transform == True:
			latency = (self.dimension + 50) * self.dimension * correction_factor
		else:
			latency = self.dimension * self.dimension / self.pe
		return latency

	def __compute_bram(self):
		bram = super()._compute_bram()
		if self.caching == True and self.uram == False:
			bram += self._count_bram_block(self.dimension*self.dimension/self.pe, self.bitwidth*self.pe)
		return bram

	def compute_resources(self):
		bram = self.__compute_bram() * self.num_cores
		dsp = super()._compute_dsp() * self.num_cores
		ff = super()._compute_ff() * self.num_cores
		lut = super()._compute_lut() * self.num_cores
		uram = super()._compute_uram() * self.num_cores
		feasible = super()._check_feasibility(bram, dsp, ff, lut, uram)
		return bram, dsp, ff, lut, uram, feasible



class MSEMetricEstimator(MetricEstimator):

	def __init__(self, num_cores, bitwidth, dimension, pe, caching, transform, interpolation, uram, platform):
		super().__init__(num_cores, bitwidth, dimension, pe, caching, transform, interpolation, uram, platform)
		if transform == True:
			self.metric = 'waxmse'
		else:
			self.metric = 'mse'

	def compute_latency(self):
		if self.transform == True:
			latency = (self.dimension + 50) * self.dimension * correction_factor
		else:
			latency = self.dimension * self.dimension / self.pe
		return latency

	def __compute_bram(self):
		bram = super()._compute_bram()
		if self.caching == True and self.uram == False:
			bram += self._count_bram_block(self.dimension*self.dimension/self.pe, self.bitwidth*self.pe)
		return bram

	def compute_resources(self):
		bram = self.__compute_bram() * self.num_cores
		dsp = super()._compute_dsp() * self.num_cores
		ff = super()._compute_ff() * self.num_cores
		lut = super()._compute_lut() * self.num_cores
		uram = super()._compute_uram() * self.num_cores
		feasible = super()._check_feasibility(bram, dsp, ff, lut, uram)
		return bram, dsp, ff, lut, uram, feasible



class MIMetricEstimator(MetricEstimator):

	def __init__(self, num_cores, bitwidth, dimension, pe, caching, transform, interpolation, uram, platform):
		super().__init__(num_cores, bitwidth, dimension, pe, caching, transform, interpolation, uram, platform)
		self.entropy_bram = 2 # empirically derived, 2 brams for each entropy module
		if transform == True:
			self.metric = 'waxmi'
		else:
			self.metric = 'mi'

	def compute_latency(self):
		if self.transform == True:
			latency = (self.dimension + 50) * self.dimension * correction_factor + math.pow(2, self.bitwidth) * math.pow(2, self.bitwidth)
		else:
			latency = self.dimension * self.dimension / self.pe + math.pow(2, self.bitwidth) * math.pow(2, self.bitwidth)
		return latency

	def __compute_bram(self):
		bram = super()._compute_bram()
		if self.caching == True and self.uram == False:
			bram += self._count_bram_block(self.dimension*self.dimension/self.pe, self.bitwidth*self.pe)
		hist_bitwidth = math.log(self.dimension * self.dimension, 2) + 1 - math.log(self.pe, 2)
		jh = self._count_bram_block(math.pow(2, self.bitwidth) * math.pow(2, self.bitwidth), hist_bitwidth)*self.pe
		complete_hist_bitwidth = math.log(self.dimension * self.dimension, 2) + 1
		single_h = self._count_bram_block(math.pow(2, self.bitwidth), complete_hist_bitwidth) * 2 # 2 single histograms
		entropy = self.entropy_bram * 3 # 3 entropy modules
		print(bram, jh, single_h, entropy)
		bram += jh + single_h + entropy
		return bram

	def compute_resources(self):
		bram = self.__compute_bram() * self.num_cores
		dsp = super()._compute_dsp() * self.num_cores
		ff = super()._compute_ff() * self.num_cores
		lut = super()._compute_lut() * self.num_cores
		uram = super()._compute_uram() * self.num_cores
		feasible = super()._check_feasibility(bram, dsp, ff, lut, uram)
		return bram, dsp, ff, lut, uram, feasible


class NMIMetricEstimator(MetricEstimator):

	def __init__(self, num_cores, bitwidth, dimension, pe, caching, transform, interpolation, uram, platform):
		super().__init__(num_cores, bitwidth, dimension, pe, caching, transform, interpolation, uram, platform)
		self.entropy_bram = 2 # empirically derived, 2 brams for each entropy module
		if transform == True:
			self.metric = 'waxnmi'
		else:
			self.metric = 'nmi'

	def compute_latency(self):
		if self.transform == True:
			latency = (self.dimension + params.transform_start_row) * self.dimension * correction_factor + \
				(math.pow(2, self.bitwidth) + (params.nmi_kernel_size - 1)) * (math.pow(2, self.bitwidth) + (params.nmi_kernel_size - 1))
		else:
			latency = self.dimension * self.dimension / self.pe + \
				(math.pow(2, self.bitwidth) + (params.nmi_kernel_size - 1)) * (math.pow(2, self.bitwidth) + (params.nmi_kernel_size - 1))
		return latency

	def __compute_bram(self):
		bram = super()._compute_bram()
		if self.caching == True and self.uram == False:
			bram += self._count_bram_block(self.dimension*self.dimension/self.pe, self.bitwidth*self.pe)

		hist_bitwidth = math.log(self.dimension * self.dimension, 2) + 1 - math.log(self.pe, 2)
		jh = self._count_bram_block(math.pow(2, self.bitwidth) * math.pow(2, self.bitwidth), hist_bitwidth)*self.pe
		
		conv_bitwidth = 32
		conv = self._count_bram_block(math.pow(2, self.bitwidth), conv_bitwidth) * (params.nmi_kernel_size - 1)
		single_h = self._count_bram_block(math.pow(2, self.bitwidth), conv_bitwidth)
		entropy = self.entropy_bram * 3
		bram += jh + conv + single_h + entropy
		return bram

	def compute_resources(self):
		bram = self.__compute_bram() * self.num_cores
		dsp = super()._compute_dsp() * self.num_cores
		ff = super()._compute_ff() * self.num_cores
		lut = super()._compute_lut() * self.num_cores
		uram = super()._compute_uram() * self.num_cores
		feasible = super()._check_feasibility(bram, dsp, ff, lut, uram)
		return bram, dsp, ff, lut, uram, feasible


estimators = {'cc': CCMetricEstimator, 'mse': MSEMetricEstimator, 'mi': MIMetricEstimator, 'nmi': NMIMetricEstimator}



def build_model(metric, num_cores, pe, bit, dim, cache, uram, transform, interpolation, platform):
	model = estimators[metric](num_cores, bit, dim, pe, cache, transform, interpolation, uram, platform)
	return model


def is_power_of_two(n):
    return (n != 0) and (n & (n-1) == 0)


def main():
	my_parser = argparse.ArgumentParser()
	my_parser.add_argument('-m', '--metric', type=str, choices=['cc', 'mse', 'mi', 'nmi'], required=True, help='similarity metric')
	my_parser.add_argument('-n', '--num_cores', type=int, default=1, help='number of cores')
	my_parser.add_argument('-pe', '--processing_element', type=int, required=True, help='number of processing elements (power of 2)')
	my_parser.add_argument('-b', '--input_bitwidth', type=int, choices=[8, 16, 32, 64, 128, 256, 512], required=True, help='input bitwidth (power of 2)')
	my_parser.add_argument('-d', '--input_dimension', type=int, required=True, help='input image dimension')
	my_parser.add_argument('-c', '--caching', action='store_true', help='enable caching')
	my_parser.add_argument('-u', '--uram', action='store_true', help='use uram if caching is enabled')
	my_parser.add_argument('-t', '--transform', action='store_true', help='enable transform')
	my_parser.add_argument('-i', '--interpolation', type=str, default='nn', choices=['nn', 'bln'], help='interpolation to use if transform is enabled')
	my_parser.add_argument('-p', '--platform', type=str, choices=['ultra96', 'zcu104', 'alveo_u200'], required=True, help='target platform')

	args = my_parser.parse_args()

	if is_power_of_two(args.processing_element) is False:
		print(bcolors.FAIL + "Error! The number of processing elements must be a power of 2" + bcolors.ENDC)
		exit(-1)

	estimator = estimators[args.metric](args.num_cores, args.input_bitwidth, args.input_dimension, args.processing_element, args.caching, args.transform, args.interpolation, args.uram, args.platform)
	
	print("\nEstimated latency:\n\t%d clock cycles" % (estimator.compute_latency()))
	hw_resources = estimator.compute_resources()
	
	bram_usage = hw_resources[0]
	dsp_usage = hw_resources[1]
	ff_usage = hw_resources[2]
	lut_usage = hw_resources[3]
	uram_usage = hw_resources[4] if resources[args.platform]["uram"] != 0 else 0
	bram_perc = bram_usage / resources[args.platform]["bram18k"] * 100
	dsp_perc = dsp_usage / resources[args.platform]["dsp"] * 100
	ff_perc = ff_usage / resources[args.platform]["ff"] * 100
	lut_perc = lut_usage / resources[args.platform]["lut"] * 100
	uram_perc = uram_usage / resources[args.platform]["uram"] * 100 if resources[args.platform]["uram"] != 0 else 0
	print("\nEstimated resource usage on %s:" % (args.platform))
	print("\tBRAM = %d (%.2f%%) \
		\n\tDSP  = %d (%.2f%%) \
		\n\tFF   = %d (%.2f%%) \
		\n\tLUT  = %d (%.2f%%) \
		\n\tURAM = %d (%.2f%%)" % \
		(bram_usage, bram_perc, dsp_usage, dsp_perc, ff_usage, ff_perc, lut_usage, lut_perc, uram_usage, uram_perc))
	
	if hw_resources[5] == True:
		print(bcolors.OKGREEN + "\nThe design is feasible\n" + bcolors.ENDC)
	else:
		print(bcolors.FAIL + "\nThe design is NOT feasible\n" + bcolors.ENDC)
	
	
if __name__ == '__main__':
	main()

