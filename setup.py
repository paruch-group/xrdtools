# -*- coding: utf-8 -*-
# created by Benedikt Ziegler
# date: 08 April 2013

from distutils.core import setup, Extension
from distutils.sysconfig import get_python_lib
from os.path import join

from xrd import __version__

package_name = 'xrd'

numpydir = join(get_python_lib(plat_specific=1), 'numpy')


setup(name=package_name,
      version=__version__,
      maintainer='B. Ziegler',
      maintainer_email='benedikt.ziegler@unige.ch',
      packages=['xrd', 'xrd.simulation'],
      requires=['lxml', 'numpy', 'matplotlib'],
      package_dir={'mypkg': 'xrd/simulation/'},
      package_data={'xrd.simulation': ['f0_CromerMann.dat']},
      )