from __future__ import unicode_literals, print_function, division, absolute_import

from argparse import ArgumentParser


def xrdml():
    parser = ArgumentParser('Export measurement data for xrdml files.')
    parser.add_argument('files', metavar='files', type=str, nargs='+',
                        help='filenames for which to export the data')

    args = parser.parse_args()
    print(args.files)