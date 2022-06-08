## Conditions
This package is a wraper over [MSU VQMT](https://compression.ru/vqmt). It can be used **only if you have installed MSU VQMT [Pro or Premium](https://compression.ru/vqmt-pro) version 14.1 or higher**. There also possible to test the wrapper with [DEMO version](https://compression.ru/video/quality_measure/vqmt_download.html#free). If you are representing a company you can also [ask for trial](https://compression.ru/video/quality_measure/vqmt_download.html#free).

The package can perform measures only with the activated VQMT. However, if you have a valid activation code, VQMT can be activated using this package. Please, don't spread MSU VQMT activation code with your sources.

Python wrapper is in BETA stage now, supplied "as is". You can report issues to video-measure@compression.ru.

*It's not possible to use the wrapper with MSU VQMT 14.0 or earlier. It won't work with the free version either.*

## How it works
This package will try to find VQMT shared library. In case of portable installation you should manually specify VQMT path. On Linux you should find `libvqmt.so`, on Windows -- `vqmt_finder.dll`.

Shared library is the part of MSU VQMT since version 14.1. It's not recommended (but possible) to use the shared library directly. You shouldn't distribute this shared library with your software or use it as a part of public service. If you need this, please refer to [MSU VQMT SDK](https://compression.ru/video/quality_measure/vqmt_sdk.html#sdk-back).

The package will load library as instalnce of `msu_vqmt.SharedInterface` class and will initialize VQMT. Using this object you can run any number of measurements without reinitialization.

*To configure measurement use JSON-configuration as described in the [configuration description](https://videoprocessing.ai/vqmt/online-help-last/config/).*

## Installation
This package is compatible with Python >=3.5. Run the following command to install (replacing `python3` with the local python command):
```
python3 -m pip install msu_vqmt
```

## Checking
To check if the package is able to find MSU VQMT shared library try the following code:
```Python
import msu_vqmt
vqmt = msu_vqmt.find()
```
More details:
```Python
import msu_vqmt

try :
    vqmt = msu_vqmt.find()
except Exception as e:
    print('Unable to find or load VQMT: %s' % str(e))
    exit(1)
    
vqmt_ver = vqmt.getVersionObject()
print('Found MSU VQMT %d.%d' % (vqmt_ver.maj, vqmt_ver.min))
```
If you have a portable installation use `loadByDir` instead of `find`:
```Python
import msu_vqmt
vqmt = msu_vqmt.loadByDir(your_vqmt_path)
```
You should specify path to
* `libvqmt.so` On Linux, 
* `vqmt_finder.dll` on Windows.

By default `msu_vqmt.find` will try to find the latest VQMT. You can also specify desired version: `msu_vqmt.find(14)` or `msu_vqmt.find('14.1')`.

## Activation
If your VQMT installation is already activated, skip this step. With MSU VQMT Pro of Premium activation code you have two alternatives:
* activation via GUI (on Windows) or command-line (on Windows or Linux),
* activation via Python-wrapper.

The first alternative is described in [MSU VQMT Documentation](https://videoprocessing.ai/vqmt/vqmt-doc-toc/).
To activate via Python-wrapper use the following scheme:
```python
import msu_vqmt

# replace the following line if you have portable installation:
vqmt = msu_vqmt.find()

if not vqmt.isActivated():
    # premium activation:
    result = vqmt.activate_premium(yout_premium_code)
    
    # or pro activation:
    result = vqmt.activate_pro(your_pro_code)
    
    if not result:
        print('Could not activate VQMT: %s' % vqmt.getError())
    else:
        print('Activation passed')
```
## Examples
### Running measure
```Python
import msu_vqmt
import json
vqmt = msu_vqmt.find()

# creating configuration
config = msu_vqmt.Config()
config.addMetric('psnr', component='Y')
config.addFile('/path/to/source.mp4')
config.addFile('/path/to/dist.mp4', startFrame=10, endFrame=20)

# running configuration
invoke = vqmt.invoke(config)
invoke.start()

# printing results
print(json.dumps(invoke.getColumns(), indent=2))       # columns of values table
print(invoke.getFrameNumbersAsArray())                 # returns numpy array
print(invoke.getValuesAsArray())                       # returns numpy matrix
print(json.dumps(invoke.getAccumulators(), indent=2))  # accumulators
```
You can get list of all supported metrics. See section [Getting information](#Getting_information)
### Troubleshooting
```Python
# creating vqmt and config...

invoke = vqmt.invoke(config)
if not invoke:
	print(invoke.getInitError())
	sys.exit(1)
	
# running invoke..
```
### Running asynchronous
```Python
import msu_vqmt
import json
import time

vqmt = msu_vqmt.find()

# add a lot of metrics
config = msu_vqmt.Config()
for c in list('YUVRGBL') + ['YUV', 'RGB']:
	config.addMetric('psnr', component=c)
for c in list('YUVRGB'):
	config.addMetric('ssim', component=c)
	config.addMetric('msssim', component=c)
config.addMetric('vmaf', component='Y')

# and some files
config.addFile('original.mp4')
config.addFile('distorted.mp4')

# running configuration
invoke = vqmt.invoke(config)
invoke.startAsynch()

# wait initialization
invoke.waitPrepareComplete()
print('Initialization complete')

# printing information about files and metrics
print(json.dumps(invoke.getColumns(), indent=2))
print(json.dumps(invoke.getFiles(), indent=2))

# let VQMT run for 1s
time.sleep(1)
invoke.pause()

# give it time to rest and then resume
print('Pause 3 sec.')
time.sleep(3)

print('Resuming')
invoke.resume()

# finally wait for the end and print results
invoke.wait()
print('Complete measure')
print(json.dumps(invoke.getAccumulators(), indent=2))
```
### Getting values interactively
The following example will print computed values and log messages immediately.
```Python
def value_cb(invoke, frame, col, val): 
    print('Frame %d col %d: %f' % (frame, col, val))
    
def event_cb(data):
	print(json.dumps(data,indent=2))

# creating vqmt and config...

# running measure
invoke = vqmt.invoke(config, event_cb, value_cb)
invoke.start()
```
### Configuring
The object of `msu_vqmt.Config` can be initialized using JSON-configuration as described in [configuration description](https://videoprocessing.ai/vqmt/online-help-last/config/).
```Python
import msu_vqmt
import json

vqmt = msu_vqmt.find()

config = msu_vqmt.Config()

# adding files with different reslution and a metric
config.addFile('../media/sunflower720.mp4')
config.addFile('../media/sunflower540.mp4')
config.addMetric('psnr', component='Y')

# vqmt will fail because geometry correction is disabled by default
invoke = vqmt.invoke(config)
invoke.start()
assert invoke.getExitStatus() == 200  # Status 200 - failed


# create another configuration with enabled geometry
config_data = {
    # configuring visualization
    'vis': {
        'enabled': True,
        'output_directory': '/vis/path',
        'compressor': 'h264'
    },
    # enabling input image resize
    'geometry': {
        'enabled': True
    },
    # configuring concurrency
    'performance': {
        'threads_number': 2,
        'metric_parallelism': 2
    }
}
config = msu_vqmt.Config(config_data)

# adding files with different reslution and a metric
config.addFile('../media/sunflower720.mp4')
config.addFile('../media/sunflower540.mp4')
config.addMetric('psnr', component='Y')

# now should be ok
invoke = vqmt.invoke(config)
invoke.start()
assert invoke.getExitStatus() == 100  # Status 100 - OK
```
### Using numpy matrix as source of input frames
```Python
import msu_vqmt
import json
import numpy as np

vqmt = msu_vqmt.find()

# the callback will be invoked as soon as a frame is needed
def input_cb(invoke_id, file, frame, data, chan_mask):
    # return None for error
    if file not in ['file1', 'file2']: return       
        
    # return False for EOF
    if frame >= 10: return False 

    # create solid image
    multiplier = 10 if file == 'file1' else 8
    img = np.ndarray([1280,720], dtype=np.ubyte)
    img.fill(50 + frame * multiplier)
    
    # copy image to VQMT buffer
    vqmt.copyImage(img, data, chan_mask)
    
    # return True for success
    return True

config = msu_vqmt.Config()

# Adding two files. We specified fmt gray to have monochrome frames.
# It's possible to use any picture type from 
# https://videoprocessing.ai/vqmt/online-help-last/picture-types/
config.addFile("file1", mode="callback", 
               props={"frames":10, "fmt":"gray", "w": 1280, "h": 720})
config.addFile("file2", mode="callback", 
               props={"frames":10, "fmt":"gray", "w": 1280, "h": 720})

# adding metrics
config.addMetric('psnr', component='Y')
config.addMetric('ssim', component='Y')

# setting up invoke object and running
invoke = vqmt.invoke(config)
invoke.setInputCallback(input_cb)
invoke.start()

# printing results
print("Columns:")
print(json.dumps(invoke.getColumns(), indent=2))
print("\n\nComputed values:")
frames = invoke.getFrameNumbersAsArray()
values = invoke.getValuesAsArray()
print(np.column_stack((frames,values)))
print("\n\nAccumulators:")
print(json.dumps(invoke.getAccumulators(), indent=2))
```

Output of this script:
```
Columns:
[
  {
    "metric_name": "psnr",
    "metric_variation": "",
    "metric_aliases": [
      "apsnr"
    ],
    "info_url": "https://www.compression.ru/video/quality_measure/info.html#psnr",
    "device": "CPU",
    "color_specification": "unspecified YUV-Y quantized",
    "actual_colorspace": "YUV BT.709 Quantized",
    "color_component": "Y",
    "requested_components": [
      "Y'/BT.709 Quantized",
      "Y'/BT.709 Quantized"
    ],
    "compaired_files": [
      0,
      1
    ],
    "config_summary": "",
    "uv-scale": {
      "expected": {
        "x": 1,
        "y": 1
      },
      "real": {
        "x": 1,
        "y": 1
      }
    },
    "value_id": "",
    "col": "A"
  },
  {
    "metric_name": "ssim",
    "metric_variation": "superfast",
    "metric_aliases": [
      "ssim_superfast"
    ],
    "info_url": "https://www.compression.ru/video/quality_measure/info.html#ssim",
    "device": "CPU",
    "color_specification": "unspecified YUV-Y quantized",
    "actual_colorspace": "YUV BT.709 Quantized",
    "color_component": "Y",
    "requested_components": [
      "Y'/BT.709 Quantized",
      "Y'/BT.709 Quantized"
    ],
    "compaired_files": [
      0,
      1
    ],
    "config_summary": "",
    "uv-scale": {
      "expected": {
        "x": 1,
        "y": 1
      },
      "real": {
        "x": 1,
        "y": 1
      }
    },
    "value_id": "",
    "col": "B"
  }
]


Computed values:
[[  0.         100.           1.        ]
 [  1.          42.1102066    0.99942541]
 [  2.          36.08960342   0.99827111]
 [  3.          32.56777954   0.99696863]
 [  4.          30.06900406   0.99568194]
 [  5.          28.13080215   0.99447572]
 [  6.          26.54718018   0.99336535]
 [  7.          25.20824242   0.99235517]
 [  8.          24.04840469   0.9914369 ]
 [  9.          23.02535248   0.99060369]]


Accumulators:
{
  "total psnr": {
    "A": 27.56175422668457
  },
  "mean": {
    "A": 36.779659271240234,
    "B": 0.9952583909034729
  },
  "harmonic mean": {
    "A": 30.929319381713867,
    "B": 0.9952482581138611
  },
  "min. val": {
    "A": 23.025352478027344,
    "B": 0.9906036853790283
  },
  "max. val": {
    "A": 100.0,
    "B": 1.0
  },
  "min. frame": {
    "A": 9,
    "B": 9
  },
  "max. frame": {
    "A": 0,
    "B": 0
  },
  "std dev": {
    "A": 21.801708221435547,
    "B": 0.0031768325716257095
  },
  "variance": {
    "A": 475.31451416015625,
    "B": 1.009226525638951e-05
  }
}
```
### Getting information
```Python
import msu_vqmt
import json

vqmt = msu_vqmt.find()
print(json.dumps(vqmt.getVersion(), indent=2), end='\n\n')
print("1st Picture type")
print(json.dumps(vqmt.getPictureTypes()[0], indent=2), end='\n\n')
print("1st Colorspace")
print(json.dumps(vqmt.getColorspaces()[0], indent=2), end='\n\n')
print("1st Device")
print(json.dumps(vqmt.getDevices()[0], indent=2), end='\n\n')
print("1st Metric")
print(json.dumps(vqmt.getMetrics()[0], indent=2))
```
Possible output:
```
{
  "program_fullname": "MSU Video Quality Measurement Tool",
  "program_shortname": "MSU VQMT",
  "developer": "COMPRESSION.RU Team & MSU G&M Lab. Video Group",
  "email": "video-measure@compression.ru",
  "web_page": [
    "https://compression.ru/vqmt",
    "https://videoprocessing.ai/vqmt"
  ],
  "version": {
    "full": "14.1 r12828",
    "maj": 14,
    "min": 1,
    "rev": 12828,
    "extra": ""
  },
  "edition": "Pro/Premium",
  "system": "Windows",
  "build_date": "May 26 2022",
  "activation": {
    "type": "Premium",
    "activated": true,
    "status": "Licensed at Jan 01 2010 for Company Name;"
  }
}

1st Picture type
{
  "key": "ABGR32",
  "name": "ABGR32",
  "bps": 8,
  "sample_type": "8-bit int",
  "color_model": "RGB",
  "subsampling": "Packed_444",
  "order": "ABGR",
  "description": "packed ABGR 444 8bps"
}

1st Colorspace
{
  "full_name": "CIE LUV",
  "base_name": "LUV",
  "model": "LUV",
  "components": [
    {
      "short_name": "L",
      "full_name": "L",
      "min": 0.0,
      "max": 100.0
    }
  ],
  "standards": [
    "CIE"
  ],
  "is_basic": false,
  "is_linear": true,
  "is_quantized": false
}

1st Device
{
  "id": "CPU",
  "fullname": "CPU",
  "variation": "[CPU] CPU",
  "is_available": true,
  "is_recommended": true,
  "is_not_recommended": false,
  "comment": "",
  "technology": "general",
  "type": "CPU"
}

1st Metric
{
  "usage": "psnr",
  "info": {
    "name": "psnr",
    "variation": "",
    "device": "CPU",
    "inputs": 2,
    "long_name": "Peak signal-to-noise ratio",
    "url": "https://www.compression.ru/video/quality_measure/info.html#psnr",
    "interface_name": "PSNR",
    "interface_group_name": "PSNR",
    "library_file": "",
    "aliases": [
      "apsnr"
    ]
  },
  "possible_colors": [
    "Y",
    "U",
    "V",
    "R",
    "G",
    "B",
    "LUV-L",
    "RGB",
    "YUV"
  ],
  "parameters": {}
}
```