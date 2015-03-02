import os
import string

from lxml.etree import parse, tostring, XML
import numpy as np


globprint = 0


def printif(variable, string='output: '):
    """ This function allows to print variables if globprint == 1 """
    if globprint == 1:
        print string, variable


def txtlist2arr(string):
    """split a list of numbers into an array"""
    if string is None:
        return np.asarray([])
    dat = np.fromstring(string, dtype=float, count=-1, sep=' ')
    return dat


def read_file(filename):
    """ procedure to open Panalytical XRDML files """

    # check file
    if filename == '':
        print('no input specified')
        return {}
    #        raise NameError('no input specified')

    if not os.path.exists(filename):
        raise ValueError('This is not a valid filename.')

    path, basename = os.path.split(filename)
    filebase, fileext = os.path.splitext(basename)

    if fileext == '':
        filename = filebase + '.xrdml'

    tree = parse(os.path.join(path, filename)).getroot()
    treestr = tostring(tree)
    treestr = string.replace(treestr, ' xmlns=', ' xmlnamespace=')
    xrdm = XML(treestr)

    data = {'filename': filename,
            'sample': xrdm.findtext('sample/id'),
            'status': xrdm.get('status'),
            'comment': {}}

    # get all sample infos
    #    data['sample'] = {}
    #    try: data['sample']['type'] = xrdm.find('sample').get('type')
    #    except: data['sample']['type'] = ''
    #    xpath = 'sample/id'
    #    try: data['sample']['id'] = xrdm.findtext(xpath)
    #    except: data['sample']['id'] = ''
    #    xpath = 'sample/name'
    #    try: data['sample']['name'] = xrdm.findtext(xpath)
    #    except: data['sample']['name'] = ''
    #    xpath = 'sample/preparedBy'
    #    try: data['sample']['preparedBy'] = xrdm.findtext(xpath)
    #    except: data['sample']['preparedBy'] = ''

    # get comment (reads ONLY the first comment, NEEDS improvement)
    xpath = 'comment/entry'
    try:
        data['comment']['1'] = xrdm.findtext(xpath)
    except:
        data['comment']['1'] = ''

    # get nb. of scans
    xpath_scans = 'xrdMeasurement/scan'
    uid_scans = xrdm.findall(xpath_scans)
    nb_scans = len(uid_scans)

    # get (h k l) and substrate
    if nb_scans > 1:
        xpath = 'xrdMeasurement/scan[1]/reflection'
        data['substrate'] = xrdm.findtext(xpath + '/material')
        data['hkl'] = {}
        if xrdm.findall(xpath) != []:
            xpath_h = xpath + '/hkl/h'
            data['hkl']['h'] = int(xrdm.findtext(xpath_h))
            xpath_k = xpath + '/hkl/k'
            data['hkl']['k'] = int(xrdm.findtext(xpath_k))
            xpath_l = xpath + '/hkl/l'
            data['hkl']['l'] = int(xrdm.findtext(xpath_l))
        else:
            data['hkl'] = 'not defined'

    xpath = 'xrdMeasurement'
    # get measurement type
    data['measType'] = xrdm.find(xpath).get('measurementType')

    # if not a simple scan and not the 'Repeated scan' than get
    # the step axis type
    if data['measType'] not in ['Scan', 'Repeated scan']:
        data['stepAxis'] = xrdm.find(xpath).get('measurementStepAxis')

    # get the scan axis type
    if nb_scans > 0:
        data['scanAxis'] = uid_scans[0].get('scanAxis')

    # get scans
    for key in ['scannb', 'data', 'time', '2Theta', 'Omega', 'Phi', 'Psi', 'X', 'Y', 'Z',
                'iscannb', 'idata', 'itime', 'i2Theta', 'iOmega', 'iPhi', 'iPsi', 'iX', 'iY', 'iZ']:
        data[key] = []

    for k in range(nb_scans):
        scan = getScan(uid_scans, k)
        if scan:
            if data['measType'] == 'Scan' or scan['status'] == 'Completed':
                data['scannb'].append(k)
                for key in ['data', 'time', '2Theta', 'Omega', 'Phi', 'Psi', 'X', 'Y', 'Z']:
                    data = append2arr(data, scan, key)
            else:  # (TODO: check if this code actually works?!)
                data['iscannb'].append(k)
                data['idata'].append(scan['data'])
                data['itime'].append(scan['time'])
                data['i2Theta'].append(scan['2Theta'])
                data['iOmega'].append(scan['Omega'])
                if 'Phi' in scan.keys():
                    data['iPhi'].append(scan['Phi'])
                if 'Psi' in scan.keys():
                    data['iPsi'].append(scan['Psi'])
                if 'X' in scan.keys():
                    data['iX'].append(scan['X'])
                if 'Y' in scan.keys():
                    data['iY'].append(scan['Y'])
                if 'Z' in scan.keys():
                    data['iZ'].append(scan['Z'])

    # if we have only one incomplete scan, the scan is considered to be
    # completed and is moved to completed scans list
    if not data['scannb'] and len(data['iscannb']) == 1:
        print '''one and only incomplete scan found in the data,
        the scan considered as completed'''
        for key, ikey in zip(['scannb', 'data', 'time', '2Theta', 'Omega', 'Phi', 'Psi', 'X', 'Y', 'Z'],
                             ['iscannb', 'idata', 'itime', 'i2Theta', 'iOmega', 'iPhi', 'iPsi', 'iX', 'iY', 'iZ']):
            if ikey in data.keys() and data[ikey]:
                data[key] = data[ikey]
                data[ikey] = []

                #        data['scannb'] = data['iscannb']
                #        data['iscannb'] = []
                #        data['data'] = data['idata']
                #        data['idata'] = []
                #        data['time'] = data['itime']
                #        data['itime'] = []
                #        data['2Theta'] = data['i2Theta']
                #        data['i2Theta'] = []
                #        data['Omega'] = data['iOmega']
                #        data['iOmega'] = []
                #        if 'iPhi' in data.keys() and data['iPhi']:
                #            data['Phi'] = data['iPhi']
                #            data['iPhi'] = []
                #        if 'iPsi' in data.keys() and data['iPsi']:
                #            data['Psi'] = data['iPsi']
                #            data['iPsi'] = []
                #        if 'iX' in data.keys() and data['iX']:
                #            data['X'] = data['iX']
                #            data['iX'] = []
                #        if 'iY' in data.keys() and data['iY']:
                #            data['Y'] = data['iY']
                #            data['iY'] = []
                #        if 'iZ' in data.keys() and data['iZ']:
                #            data['Z'] = data['iZ']
                #            data['iZ'] = []

    # remove redundant information
    for key in ['Phi', 'Psi', 'X', 'Y', 'Z']:
        if data[key] == []:
            data.pop(key)
    if not data['iscannb']:
        for key in ['iscannb', 'idata', 'itime', 'i2Theta', 'iOmega',
                    'iPhi', 'iPsi', 'iX', 'iY', 'iZ']:
            data.pop(key)

    if np.all(data['time'] == data['time'][0]):
        data['time'] = data['time'][0]

    if data['measType'] != 'Area measurement':
        if np.all(data['2Theta'] == data['2Theta'][0]):
            data['2Theta'] = data['2Theta'][0]
        if np.all(data['Omega'] == data['Omega'][0]):
            data['Omega'] = data['Omega'][0]

    if nb_scans > 1:
        if 'Phi' in data.keys() and np.all(data['Phi'] == data['Phi'][0]):
            data['Phi'] = data['Phi'][0]
        if 'Psi' in data.keys() and np.all(data['Psi'] == data['Psi'][0]):
            data['Psi'] = data['Psi'][0]
        if 'X' in data.keys() and np.all(data['X'] == data['X'][0]):
            data['X'] = data['X'][0]
        if 'Y' in data.keys() and np.all(data['Y'] == data['Y'][0]):
            data['Y'] = data['Y'][0]
        if 'Z' in data.keys() and np.all(data['Z'] == data['Z'][0]):
            data['Z'] = data['Z'][0]

    # in case of 'Repeated scan' sum all completed scans together and
    # remove redundant data
    if data['measType'] == 'Repeated scan':
        # average completed scans (intensity is in cps)
        for k in np.arange(1, len(data['scannb'])):
            data['data'][0] += data['data'][k]
        data['data'] = data['data'][0] / len(data['scannb'])
        # reduce all possible axis
        for key in ['2Theta', 'Omega', 'Phi', 'Psi', 'X', 'Y', 'Z']:
            if key in data.keys() and np.all(data[key][:] == data[key][0]):
                data[key] = data[key][0]
        # set true time
        data['time'] *= len(data['scannb'])
        # remove redundant infromation about scan number
        data.pop('scannb')

    # get wavelength
    xpath = 'xrdMeasurement/usedWavelength'
    uid = xrdm.find(xpath)
    data['kType'] = uid.get('intended')
    data['kAlpha1'] = np.double(xrdm.findtext(xpath + '/kAlpha1'))
    data['kAlpha2'] = np.double(xrdm.findtext(xpath + '/kAlpha2'))
    data['kBeta'] = np.double(xrdm.findtext(xpath + '/kBeta'))
    data['kAlphaRatio'] = np.double(xrdm.findtext(xpath + '/ratioKAlpha2KAlpha1'))
    if data['kType'] == 'K-Alpha 1':
        data['Lambda'] = data['kAlpha1']
    elif data['kType'] == 'K-Alpha':
        data['Lambda'] = data['kAlpha1'] + data['kAlphaRatio'] * data['kAlpha2']
        data['Lambda'] /= 1.5
    else:
        print('usedWavelength type is not supported (using K-Alpha 1')
        data['Lambda'] = data['kAlpha1']

    # get some usefull information (x/y-label, x/y-units)
    if nb_scans > 0:
        if 'scanAxis' in data.keys():
            if data['scanAxis'] == 'Gonio':
                axisType = '2Theta'
                data['xlabel'] = '2Theta-Theta'
                if data['measType'] in ['Scan', 'Repeated scan']:
                    data['x'] = data['2Theta']
            elif data['scanAxis'] in ['2Theta', '2Theta-Omega']:
                axisType = '2Theta'
                data['xlabel'] = data['scanAxis']
                if data['measType'] in ['Scan', 'Repeated scan']:
                    data['x'] = data['2Theta']
            elif data['scanAxis'] in ['Omega', 'Omega-2Theta']:
                axisType = 'Omega'
                data['xlabel'] = data['scanAxis']
                if data['measType'] in ['Scan', 'Repeated scan']:
                    data['x'] = data['Omega']
            elif data['scanAxis'] == 'Reciprocal Space':
                axisType = 'Omega'
                data['xlabel'] = 'Omega'
                if data['measType'] in ['Scan', 'Repeated scan']:
                    data['x'] = data['Omega']
            elif data['scanAxis'] in ['Phi', 'Psi', 'X', 'Y', 'Z']:
                axisTpye = data['scanAxis']
                data['xlable'] = data['scanAxis']
                if data['measType'] == 'Scan':
                    data['x'] = data[data['scanAxis']]
            else:
                print('scanAxis type is not supported')
                axisType = 'unknown'
                data['xlabel'] = 'unknown'

            # (TODO: maybe optimization possible, load units before)
            xpath = 'xrdMeasurement/scan[1]/dataPoints/positions'
            uid = xrdm.find(xpath)
            for pos in uid:
                if pos.get('axis') == axisType:
                    data['xunit'] = pos.get('unit')
                    break
            if 'xunit' not in data.keys():
                #print('xunit value not assigned')
                data['xunit'] = 'nd'

        if 'stepAxis' in data.keys():
            if data['stepAxis'] == 'Gonio':
                axisType = '2Theta'
                data['ylabel'] = '2Theta-Theta'
            elif data['stepAxis'] in ['2Theta', '2Theta-Omega']:
                axisType = '2Theta'
                data['ylabel'] = data['stepAxis']
            elif data['stepAxis'] in ['Omega', 'Omega-2Theta']:
                axisType = 'Omega'
                data['ylabel'] = data['stepAxis']
            elif data['stepAxis'] in ['Phi', 'Psi', 'X', 'Y', 'Z']:
                axisType = data['stepAxis']
                data['ylabel'] = data['stepAxis']
            else:
                print('scanAxis type not supported')
                axisType = 'unknown'
                data['ylabel'] = 'unknown'

            # (TODO: maybe optimization possible, load units before)
            xpath = 'xrdMeasurement/scan[1]/dataPoints/positions'
            uid = xrdm.find(xpath)
            for pos in uid:
                if pos.get('axis') == axisType:
                    data['yunit'] = pos.get('unit')
                    break
            if 'yunit' not in data.keys():
                print('yunit value is not assigned')
                data['yunit'] = 'nd'

    if data['measType'] == 'Area measurement':
        # TODO: check if omega is same dimensions as 2theta, otherwise correct it
        dim2T = data['2Theta'].shape
        dimO = data['Omega'].shape
        if dim2T[1] != dimO[1] and data['scanAxis'] == '2Theta' and data['stepAxis'] == 'Omega':
            tmp = np.empty_like(data['2Theta'])
            for k in range(dim2T[1]):
                tmp[:, k] = data['Omega'].T
            data['Omega'] = tmp
            print('Omega array was corrected to match 2Theta and data arrays')

    # Mask Width [OPTIONAL]
    xpath = 'xrdMeasurement/incidentBeamPath/mask/width'
    uid = xrdm.find(xpath)
    if uid is not None:
        unit = uid.get('unit')
        if unit != 'mm':
            print('Mask Width units are not \'mm\'')
        data['maskWidth'] = np.double(xrdm.findtext(xpath))

    # Divergence slit Height [OPTIONAL]
    xpath = 'xrdMeasurement/incidentBeamPath/divergenceSlit/height'
    uid = xrdm.find(xpath)
    if uid is not None:
        unit = uid.get('unit')
        if unit != 'mm':
            print('Divergence slit Height units are not \'mm\'')
        data['slitHeight'] = np.double(xrdm.findtext(xpath))

    return data


def sortdata(k, uid_scans, data):
    scan = getScan(uid_scans, k)
    if scan:
        if data['measType'] == 'Scan' or scan['status'] == 'Completed':
            data['scannb'].append(k)
            for key in ['data', 'time', '2Theta', 'Omega', 'Phi', 'Psi', 'X', 'Y', 'Z']:
                data = append2arr(data, scan, key)
        else:  # (TODO: check if this code actually works?!)
            data['iscannb'].append(k)
            data['idata'].append(scan['data'])
            data['itime'].append(scan['time'])
            data['i2Theta'].append(scan['2Theta'])
            data['iOmega'].append(scan['Omega'])
            if 'Phi' in scan.keys():
                data['iPhi'].append(scan['Phi'])
            if 'Psi' in scan.keys():
                data['iPsi'].append(scan['Psi'])
            if 'X' in scan.keys():
                data['iX'].append(scan['X'])
            if 'Y' in scan.keys():
                data['iY'].append(scan['Y'])
            if 'Z' in scan.keys():
                data['iZ'].append(scan['Z'])
    return data


def append2arr(data, scan, key):
    if data[key] == []:
        data[key] = scan[key]
    else:
        data[key] = np.vstack((data[key], scan[key]))
    return data


def getScan(uid_scans, scannb):
    """ Extract scan data
    """
    scan_data = {}
    # here should be some input checks

    #    # find the scan in the tree
    #    xpath_scan = 'xrdMeasurement/scan'+'['+str(scannb)+']'
    #    uid_scan = tree.find(xpath_scan)
    #    if not uid_scan:
    #        print 'Can not find a specified scan.'
    #        return []

    # get correct scan
    uid_scan = uid_scans[scannb]

    # get the scan status
    scan_data['status'] = uid_scan.get('status')

    # get the scan axis type
    scan_data['scanAxis'] = uid_scan.get('scanAxis')

    # get intensities
    scan_data['data'] = txtlist2arr(uid_scan.findtext('dataPoints/intensities'))
    units_intensities = uid_scan.find('dataPoints/intensities').get('unit')

    # get counting time
    scan_mode = uid_scan.get('mode')
    if scan_mode == 'Pre-set counts':
        time = uid_scan.findtext('dataPoints/countingTimes')
    else:
        time = uid_scan.findtext('dataPoints/commonCountingTime')
    scan_data['time'] = txtlist2arr(time)

    # normalize intensity units to cps
    if units_intensities == 'counts':
        scan_data['data'] /= scan_data['time']

    # get the position of all axes
    xpath = 'dataPoints/positions'
    uid_pos = uid_scan.findall(xpath)
    n = len(scan_data['data'])  # nb of data points
    for pos in uid_pos:
        info = readAxisInfo(pos, n)
        if info['axis'] == '2Theta':
            scan_data['2Theta'] = info['data']
        elif info['axis'] == 'Omega':
            scan_data['Omega'] = info['data']
        elif info['axis'] == 'Phi':
            scan_data['Phi'] = info['data']
        elif info['axis'] == 'Psi':
            scan_data['Psi'] = info['data']
        elif info['axis'] == 'X':
            scan_data['X'] = info['data']
        elif info['axis'] == 'Y':
            scan_data['Y'] = info['data']
        elif info['axis'] == 'Z':
            scan_data['Z'] = info['data']
        else:
            print 'axis type not supported'
    return scan_data


def readAxisInfo(uid_pos, n):
    info = {'axis': uid_pos.get('axis'), 'unit': uid_pos.get('unit')}
    unspaced = True
    isarray = True
    uid_child = list(uid_pos)
    for child in uid_child:
        #        node = uid_pos.find(child.tag)
        #        print node
        if child.tag == 'listPositions':
            info['data'] = txtlist2arr(uid_pos.findtext('listPositions'))
            unspaced = False
        elif child.tag in ['startPosition', 'endPosition', 'commonPosition']:
            if 'data' not in info.keys():
                info['data'] = np.zeros(2)
            if child.tag == 'startPosition':
                info['data'][0] = np.double(uid_pos.findtext('startPosition'))
            elif child.tag == 'endPosition':
                info['data'][1] = np.double(uid_pos.findtext('endPosition'))
            elif child.tag == 'commonPosition':
                info['data'] = np.asarray(np.double(uid_pos.findtext('commonPosition')))
                isarray = False
        else:
            print 'unsupported tag'
            info['data'] = np.array([])

    if unspaced and ('n' in locals()) and n and isarray:
        info['data'] = np.linspace(info['data'][0], info['data'][1], n)

    if not unspaced and ('n' in locals()) and n and len(info['data']) != n:
        print 'different numbers of axis positions and data points'
    return info


if __name__ == '__main__':
    file = read_file('test.xrdml')





