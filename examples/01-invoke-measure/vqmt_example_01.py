# This is a part of MSU VQMT Python Interface
# https://github.com/msu-video-group/vqmt_python
#
# This code can be used only with installed 
# MSU VQMT Pro, Premium, Trial, DEMO v14.1+
#
# Copyright MSU Video Group, compression.ru TEAM

import msu_vqmt
import json
vqmt = msu_vqmt.find()

# creating configuration
config = msu_vqmt.Config()
config.addMetric('psnr', component='Y')
config.addFile('../media/sunflower720.mp4')
config.addFile('../media/sunflower720lq.mp4')

# running configuration
invoke = vqmt.invoke(config)
if not invoke:
    print(invoke.getInitError())
    sys.exit(1)
invoke.start()

# printing results
print(json.dumps(invoke.getColumns(), indent=2))       # columns of values table
print(invoke.getFrameNumbersAsArray())                 # returns numpy array
print(invoke.getValuesAsArray())                       # returns numpy matrix
print(json.dumps(invoke.getAccumulators(), indent=2))  # accumulators

# another attempt with same vqmt object
# now will shift the second file by 10 frames
config = msu_vqmt.Config()
config.addMetric('psnr', component='Y')
config.addFile('../media/sunflower720.mp4')
config.addFile('../media/sunflower720lq.mp4', startFrame=10, endFrame=20)

# running configuration
invoke = vqmt.invoke(config)
if not invoke:
    print(invoke.getInitError())
    sys.exit(1)
invoke.start()

# printing results
print(json.dumps(invoke.getColumns(), indent=2))       # columns of values table
print(invoke.getFrameNumbersAsArray())                 # returns numpy array
print(invoke.getValuesAsArray())                       # returns numpy matrix
print(json.dumps(invoke.getAccumulators(), indent=2))  # accumulators
print(json.dumps(invoke.getGeneralizedInfo(), indent=2))  # general information