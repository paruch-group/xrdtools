# -*- coding: utf-8 -*-
import os
import io
import re
from setuptools import setup


def read(*parts):
    here = os.path.abspath(os.path.dirname(__file__))
    with io.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


requires = [
    'lxml>=3.0',
    'numpy>=1.7',
]


with open('README.md') as f:
    long_description = f.read()


setup(
    name='xrdtools',
    version=find_version('xrdtools', '__init__.py'),
    packages=['xrdtools', 'xrdtools.tools'],
    description='A library to read .xrdml files',
    long_description=long_description,
    long_description_content_type="text/markdown",
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
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Physics',
    ],
    install_requires=requires,
)
