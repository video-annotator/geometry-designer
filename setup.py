#!/usr/bin/python
# -*- coding: utf-8 -*-


__author__ = "Ricardo Ribeiro"
__copyright__ = ""
__credits__ = "Ricardo Ribeiro"
__license__ = "MIT"
__version__ = "0.2"
__maintainer__ = ["Ricardo Ribeiro", "Carlos Mão de Ferro"]
__email__ = ["ricardojvr at gmail.com", "cajomferro at gmail.com"]
__status__ = "Development"
__updated__ = "2016-03-14"

from setuptools import setup, find_packages

setup(
    name='geometry_designer',
    version=__version__,
    description="""""",
    author='Ricardo Ribeiro',
    author_email='ricardo.ribeiro@sssssssss.fchampalimaud.org',
    license='MIT',
    url='https://github.com/UmSenhorQualquer/geometry-designer',
    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'examples', 'deploy', 'reports']),
    entry_points={
        'console_scripts': [
            'geometry-designer=geometry_designer.__main__',
        ],
    }
)
