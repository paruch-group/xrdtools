# -*- coding: utf-8 -*-
from setuptools import setup

from xrdtools import __version__, __name__ as package_name

requires = [
    'lxml>=3.0',
    'numpy>=1.7',
]

setup(
    name=package_name,
    packages=['xrdtools'],
    version=__version__,
    description='A library to read .xrdml files',
    author='Benedikt Ziegler',
    author_email='benediktziegler@gmail.com',
    url='https://github.com/paruch-group/xrdtools',
    download_url='https://github.com/paruch-group/xrdtools/tarball/0.1',
    keywords=['xrdml', 'loading'],
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
        'Topic :: Scientific/Engineering :: Physics',
    ],
    install_requires=requires,
)
