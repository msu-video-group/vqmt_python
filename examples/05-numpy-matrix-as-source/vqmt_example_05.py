# This is a part of MSU VQMT Python Interface
# https://github.com/msu-video-group/vqmt_python
#
# This code can be used only with installed 
# MSU VQMT Pro, Premium, Trial, DEMO v14.1+
#
# Copyright MSU Video Group, compression.ru TEAM

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
