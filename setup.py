# This is a part of MSU VQMT Python Interface
# https://github.com/msu-video-group/vqmt_python
#
# This code can be used only with installed 
# MSU VQMT Pro, Premium, Trial, DEMO v14.1+
#
# Copyright MSU Video Group, compression.ru TEAM

from pathlib import Path
from setuptools import setup
import os

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    author="Video Compression Team & MSU G&M Lab.",
    author_email="video-measure@compression.ru",
    name='msu_vqmt',                           # package name
    description='MSU VQMT Python Wrapper package. This package requires installed MSU VQMT Pro or Premium',
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires=">=3.5",
    version='0.2',                             # version
                                               # short description
    url='https://github.com/msu-video-group/vqmt_python', # package URL
    install_requires=['numpy'],                # list of packages this package depends
                                               # on.
    packages=['msu_vqmt'],              # List of module names that installing
                                        # this package will provide.
    keywords=["video", "images", "compression", "codecs", "quality", "analysis"],
) 