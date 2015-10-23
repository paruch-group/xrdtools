from __future__ import unicode_literals, print_function, division, absolute_import

import sys
from argparse import ArgumentParser

import numpy as np
import xrdtools


def xrdml():
    """Command line tool to export measurement data from xrdml files.

    Allowed keyword arguments:
    --------------------------
    -o, --output : str
        Choices: 'stdout', 'txt' [default: 'txt']
    --delimiter : str
        Default: '\t'
    --fmt : str
        Default: '%.18e'
    """

    parser = ArgumentParser('Export measurement data for xrdml files.')
    parser.add_argument('filenames', metavar='filenames', type=str, nargs='+',
                        help='filenames for which to export the data')
    parser.add_argument('-o', '--output', metavar='output', choices=['stdout', 'txt'],
                        default='txt',
                        help='the format to which the data should be exported')
    parser.add_argument('--delimiter', metavar='delimiter', type=str, default='\t',
                        help='define a delimiter')
    parser.add_argument('--fmt', metavar='fmt', type=str, default='%.18e',
                        help='define the output format')

    args = parser.parse_args()

    for filename in args.filenames:
        data = xrdtools.read_xrdml(filename)

        output = np.array([])
        labels = []

        if data['measType'] == 'Scan':
            output = np.vstack([data['x'], data['data']])
            labels = [data.get('xlabel', ''), 'Intensity']

        elif data['measType'] == 'Area measurement':
            output = np.vstack([data['2Theta'].ravel(), data['Omega'].ravel(), data['data'].ravel()])
            labels = [data.get('xlabel', ''), data.get('ylabel', ''), 'Intensity']

        else:
            print('Measurement type is not supported.')
            continue

        if args.output == 'txt':
            file_out = filename.replace('.xrdml', '.txt')
        elif args.output == 'stdout':
            file_out = sys.stdout

        delimiter = args.delimiter.decode('string-escape')
        fmt = args.fmt
        np.savetxt(file_out, output.T,
                   fmt=fmt,
                   delimiter=delimiter,
                   header=delimiter.join(labels))
