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
print(json.dumps(vqmt.getVersion(), indent=2), end='\n\n')
print("1st Picture type")
print(json.dumps(vqmt.getPictureTypes()[0], indent=2), end='\n\n')
print("1st Colorspace")
print(json.dumps(vqmt.getColorspaces()[0], indent=2), end='\n\n')
print("1st Device")
print(json.dumps(vqmt.getDevices()[0], indent=2), end='\n\n')
print("1st Metric")
print(json.dumps(vqmt.getMetrics()[0], indent=2))