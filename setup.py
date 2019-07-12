#!/usr/bin/python
# -*- coding: utf-8 -*-


__author__ = "Ricardo Ribeiro"
__copyright__ = ""
__credits__ = "Ricardo Ribeiro"
__license__ = "MIT"
__maintainer__ = ["Ricardo Ribeiro", "Carlos Mão de Ferro"]
__email__ = ["ricardojvr at gmail.com", "cajomferro at gmail.com"]
__status__ = "Development"
__updated__ = "2016-03-14"

from setuptools import setup, find_packages
import re, os

PACKAGE_PATH = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(PACKAGE_PATH, 'geometry_designer','__init__.py'), 'r') as fd:
    content = fd.read()
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', content, re.MULTILINE).group(1)



setup(
    name='geometry_designer',
    version=version,
    description="""""",
    author='Ricardo Ribeiro',
    author_email='ricardo.ribeiro@research.fchampalimaud.org',
    license='MIT',
    url='https://github.com/UmSenhorQualquer/geometry-designer',
    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'examples', 'deploy', 'reports'])
)
