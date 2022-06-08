# This is a part of MSU VQMT Python Interface
# https://github.com/msu-video-group/vqmt_python
#
# This code can be used only with installed 
# MSU VQMT Pro, Premium, Trial, DEMO v14.1+
#
# Copyright MSU Video Group, compression.ru TEAM

import msu_vqmt
import json

def value_cb(invoke, frame, col, val): 
    print('Frame %d col %d: %f' % (frame, col, val))
    
def event_cb(data):
	print(json.dumps(data,indent=2))

# creating vqmt and config...
vqmt = msu_vqmt.find()

# creating configuration
config = msu_vqmt.Config()
config.addMetric('psnr', component='Y')
config.addFile('../media/sunflower720.mp4')
config.addFile('../media/sunflower720lq.mp4', endFrame=10)

# running measure
invoke = vqmt.invoke(config, event_cb, value_cb)
invoke.start()