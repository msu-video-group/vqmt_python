# This is a part of MSU VQMT Python Interface
# https://github.com/msu-video-group/vqmt_python
#
# This code can be used only with installed 
# MSU VQMT Pro, Premium, Trial, DEMO v14.1+
#
# Copyright MSU Video Group, compression.ru TEAM

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
config.addFile('../media/sunflower720.mp4')
config.addFile('../media/sunflower720lq.mp4')

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