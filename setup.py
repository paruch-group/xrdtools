# -*- coding: utf-8 -*-
from glob import glob
import os
from setuptools import setup

from xrdtools import __version__, __name__ as package_name


requires = [
    'lxml>=3.0',
    'numpy>=1.7',
]

setup(
    name=package_name,
    version=__version__,
    packages=['xrdtools', 'xrdtools.tools'],
    description='A library to read .xrdml files',
    author='Benedikt Ziegler',
    author_email='benediktziegler@gmail.com',
    include_package_data=True,
    package_data={
        'xrdtools': ['data/schemas/*.xsd'],
    },
    entry_points={
        'console_scripts': ['xrdml = xrdtools.tools.clt:xrdml']
    },
    url='https://github.com/paruch-group/xrdtools',
    keywords=['xrdml', 'read'],
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering :: Physics',
    ],
    install_requires=requires,
)
