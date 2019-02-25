#!/usr/bin/env python
# coding: utf-8
from setuptools import setup, find_packages, Extension
from labnote import __author__, __version__, __license__
 
setup(
        name             = 'lab-note',
        version          = __version__,
        description      = '.',
        license          = __license__,
        author           = __author__,
        author_email     = 'atsushi.hashimoto@sinicx.com',
        url              = 'https://AtsushiHashimoto.github.io/lab-note',
        keywords         = 'laboratory note, experiments, archive',
        packages         = find_packages(),
	include_package_data = True,
        install_requires = ['pipreqs','easydict','pyyaml','jupyter>1.0.0','requests'],
        )
 
