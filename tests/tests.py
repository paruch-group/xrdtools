from __future__ import unicode_literals, print_function, division, absolute_import

import unittest

from xrdtools import read_xrdml


class TestXrdmlRead(unittest.TestCase):
    def test_read_xrdml_area_scan(self):
        data = read_xrdml('tests/test_area.xrdml')

        self.assertEqual(data['comment'], {'1': None})
        self.assertEqual(data['kAlpha1'], 1.540598)
        self.assertEqual(data['kAlpha2'], 1.544426)
        self.assertEqual(data['kBeta'], 1.39225)
        self.assertEqual(data['kAlphaRatio'], 0.5)
        self.assertEqual(data['kType'], 'K-Alpha 1')
        self.assertEqual(data['Lambda'], 1.540598)

        self.assertEqual(data['slitHeight'], 0.38)
        self.assertEqual(data['scanAxis'], 'Omega-2Theta')
        self.assertEqual(data['stepAxis'], 'Omega')
        self.assertEqual(data['time'], [3.])

        self.assertEqual(data['sample'], 'B11091')
        self.assertEqual(data['substrate'], 'SrTiO3')
        self.assertEqual(data['hkl'], {'h': 0, 'k': 1, 'l': 3})

        self.assertEqual(data['2Theta'].size, 5700)
        self.assertEqual(data['Omega'].size, 5700)
        self.assertEqual(data['data'].size, 5700)
        self.assertEqual(data['Phi'], [0.])
        self.assertEqual(data['Psi'], [-0.4])
        self.assertEqual(data['X'], [2.37])
        self.assertEqual(data['Y'], [-0.98])
        self.assertEqual(data['Z'], [9.695])
        self.assertEqual(data['yunit'], 'deg')
        self.assertEqual(data['xunit'], 'deg')
        self.assertEqual(data['xlabel'], 'Omega-2Theta')
        self.assertEqual(data['ylabel'], 'Omega')
        self.assertEqual(data['status'], 'Completed')
        self.assertEqual(data['measType'], 'Area measurement')

        keys = ['comment', 'kAlpha1', 'kAlpha2', 'kType',
                'sample', 'slitHeight', 'stepAxis',
                'X', 'Phi', 'Psi', 'yunit', 'filename', 'xunit',
                'xlabel', 'Omega', 'status', 'ylabel', '2Theta',
                'scannb', 'hkl', 'Y', 'Z', 'data', 'measType',
                'Lambda', 'scanAxis', 'substrate', 'kBeta',
                'time', 'kAlphaRatio']
        for key in keys:
            self.assertIn(key, data.keys())
