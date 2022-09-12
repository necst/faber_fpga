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

dsp_slope = {'cc': -0.01629106706, \
			 'mse': -0.005430355688, \
			 'mi': 0, \
			 'nmi': 0, \
			 'waxcc': -0.01629106706, \
			 'waxmse': -0.005430355688, \
			 'waxmi': 0, \
			 'waxnmi': 0}
ff_slope = {'cc': 205.8177211, \
			'mse': 155.3387637, \
			'mi': 237.4285714, \
			'nmi': 248.2142857, \
			'waxcc': 274.7920174, \
			'waxmse': 216.8345099, \
			'waxmi': 329.7142857, \
			 'waxnmi': 268.1428571}
lut_slope = {'cc': 333.3702145, \
			 'mse': 176.9318943, \
			 'mi': 274.1428571, \
			 'nmi': 282.2857143, \
			 'waxcc': 423.6111413, \
			 'waxmse': 262.3581772, \
			 'waxmi': 420, \
			 'waxnmi': 454.0714286}
uram_slope = {'cc': 0, \
			  'mse': 0, \
			  'mi': 0, \
			  'nmi': 0, \
			  'waxcc': 0, \
			  'waxmse': 0, \
			  'waxmi': 0, \
			 'waxnmi': 0}


dsp_intercept_base = {'cc': 3.724137931, \
					  'mse': 3.24137931, \
					  'mi': 59, \
					  'nmi': 65, \
					  'waxcc': {'bln': 52.72413793, 'nn': 30.72413793}, \
					  'waxmse': {'bln': 52.24137931, 'nn': 30.24137931}, \
					  'waxmi': {'bln': 108, 'nn': 86}, \
					  'waxnmi': {'bln': 114, 'nn': 92}}
ff_intercept_base = {'cc': 4046.735632, \
					 'mse': 2553.425287, \
					 'mi': 7842, \
					 'nmi': 8489.5, \
					 'waxcc': {'bln': 11300.10345, 'nn': 9642.344828}, \
					 'waxmse': {'bln': 10022.33333, 'nn': 8263.431034}, \
					 'waxmi': {'bln': 15321, 'nn': 13371}, \
					  'waxnmi': {'bln': 16212, 'nn': 14262}}
lut_intercept_base = {'cc': 3542.568966, \
					  'mse': 1611.235632, \
					  'mi': 8477, \
					  'nmi': 8969, \
					  'waxcc': {'bln': 12692.77011, 'nn': 10576.62644}, \
					  'waxmse': {'bln': 10825.08046, 'nn': 8685.787356}, \
					  'waxmi': {'bln': 17615, 'nn': 15479}, \
					  'waxnmi': {'bln': 18026.5, 'nn': 15872.5}}
uram_intercept_base = {'cc': 0, \
					   'mse': 0, \
					   'mi': 0, \
					   'nmi': 0, \
					   'waxcc': {'bln': 0, 'nn': 0}, \
					   'waxmse': {'bln': 0, 'nn': 0}, \
					   'waxmi': {'bln': 0, 'nn': 0}, \
					  'waxnmi': {'bln': 0, 'nn': 0}}

ff_caching_intercept = {'cc': 3762.609195, \
						'mse': 2763.471264, \
						'mi': 7991, \
						'nmi': 8785.5, \
						'waxcc': {'bln': 11793.16092, 'nn': 10192.58046}, \
						'waxmse': {'bln': 10496.22414, 'nn': 8457.597701}, \
						'waxmi': {'bln': 15856, 'nn': 13902}, \
					  'waxnmi': {'bln': 16969, 'nn': 14890}}
lut_caching_intercept = {'cc': 3878.54023, \
						'mse': 1848.37931, \
						'mi': 8764, \
						'nmi': 9275.5, \
						'waxcc': {'bln': 13105.23563, 'nn': 11042.21839}, \
						'waxmse': {'bln': 11201.01149, 'nn': 9043.603448}, \
						'waxmi': {'bln': 17784, 'nn': 15622}, \
					  'waxnmi': {'bln': 18406, 'nn': 16055}}

nmi_kernel_size = 3
transform_store_rows = 100 # Xilinx's WarpTransform default value
transform_start_row = 50