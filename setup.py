# -*- coding: utf-8 -*-
from distutils.core import setup

from xrd import __version__, __name__ as package_name


requires = [
    'lxml==3.4.4',
    'numpy>=1.7',
]

setup(
    name=package_name,
    version=__version__,
    maintainer='Benedikt Ziegler',
    maintainer_email='benedikt.ziegler@unige.ch',
    packages=['xrd'],
    install_requires=requires,
)
