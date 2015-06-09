# -*- coding: utf-8 -*-
from distutils.core import setup, Extension
from distutils.sysconfig import get_python_lib
from os.path import join

from xrd import __version__, __name__ as package_name


# numpydir = join(get_python_lib(plat_specific=1), 'numpy')

setup(name=package_name,
      version=__version__,
      maintainer='Benedikt Ziegler',
      maintainer_email='benedikt.ziegler@unige.ch',
      packages=['xrd'],
      requires=['lxml', 'numpy', 'logger'],
      )