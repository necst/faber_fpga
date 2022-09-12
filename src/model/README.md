# Resource and latency model

**model.py** implements a resource and latency model to support expert users during the customization of the accelerators available within Faber.

To use the model, please provide the following arguments:
- Similarity metric (available metrics: cross-correlation, mean-squared error, mutual information, normalized mutual information): `-m/--metric {cc, mse, mi, nmi}`
- Number of cores (optional; default: 1): `-n/--num_cores NUM_CORES`
- Numer of Processing Elements (PEs) (must be a power of 2): `-pe PROCESSING_ELEMENT`
- Input bitwidth (must be a power of 2): `-b/--input_bitwidth {8,16,32,64,128,256,512}`
- Input dimension (assuming a squared image DxD, just provide D): `-d/--input_dimension INPUT_DIMENSION`
- Caching (optional): `-c/--caching`
- URAM usage for caching (optional): `-u/--uram`
- Enable HW transform (optional): `-t/-transform`
- Interpolation to use if transform is enabled (available interpolations: nearest neighbors, bilinear; default: nearest neighbors): `-i/--interpolation {nn, bln}`
- Target platform (available platforms: Ultra96, ZCU104, Alveo u200): `-p/--platform {ultra96, zcu104, alveo_u200}`

### Example
Let's consider the following configuration:
- Input image: 512x512 8-bit image
- Similarity metric: 2-core mutual information accelerator with 16 PEs
- URAM caching
- Target platform: Alveo u200

To estimate the resource usage and latency of this configuration, run the model as follows:

`python3 model.py -m mi -n 2 -pe 16 -b 8 -d 512 -c -u -p alveo_u200`
