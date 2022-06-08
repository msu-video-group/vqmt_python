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

config = msu_vqmt.Config()

# adding files with different reslution and a metric
config.addFile('../media/sunflower720.mp4')
config.addFile('../media/sunflower540.mp4')
config.addMetric('psnr', component='Y')

# vqmt will fail because geometry correction is disabled by default
invoke = vqmt.invoke(config)
invoke.start()
assert invoke.getExitStatus() == 200  # Status 200 - failed


# Create another configuration with enabled geometry.
# The complete configuration description can be found at
# https://videoprocessing.ai/vqmt/online-help-last/config/
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