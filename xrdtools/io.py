from __future__ import unicode_literals, print_function, division, absolute_import

import os
import io
import logging

from lxml import etree
import numpy as np

logger = logging.getLogger(__name__)

package_path = os.path.dirname(__file__)


def validate_xrdml_schema(filename):
    """
    Validate the xml schema of a given file.

    Parameters
    ----------
    filename : str
        The Filename of the `.xrdml` file to test.

    Returns
    -------
    float or None
        Returns the version number as float or None if
        the file was not matching any provided xml schema.

    """
    schemas = [(1.5, 'data/schemas/XRDMeasurement15.xsd'),
               (1.4, 'data/schemas/XRDMeasurement14.xsd'),
               (1.3, 'data/schemas/XRDMeasurement13.xsd'),
               (1.2, 'data/schemas/XRDMeasurement12.xsd'),
               (1.1, 'data/schemas/XRDMeasurement11.xsd'),
               (1.0, 'data/schemas/XRDMeasurement10.xsd'),
               ]
    schemas = [(v, os.path.join(package_path, schema)) for v, schema in schemas]

    with open(filename, 'r') as f:
        data_xml = etree.parse(f)

    for version, schema in schemas:
        with io.open(schema, 'r', encoding='utf8') as f:
            xmlschema_doc = etree.parse(f)
            xmlschema = etree.XMLSchema(xmlschema_doc)

        valid = xmlschema.validate(data_xml)
        if valid:
            return version
    return None


def _txt_list2arr(txt):
    """
    Split a list of numbers `txt` into a numpy ndarray.

    Parameters
    ----------
    txt : str
        String containing floats separated by spaces.

    Returns
    -------
    ndarray
        Numpy ndarray of dtype float.
    """
    if txt is None:
        return np.asarray([])
    return np.fromstring(txt, dtype=float, count=-1, sep=' ')


def _get_array_for_single_value(data, key):
    """
    Create an array for a given `key` of the length of the data array.

    Parameters
    ----------
    data : dict
        Dictionary containing the measurement data and settings.
    key : str
        Key of the parameter which needs to be transformed to the same length
        as the data array.

    Returns
    -------
    dict
        Same data dictionary as input dictionary `data`.
    """
    if key not in data:
        return data
    if data[key].size == 1:
        data[key] = np.ones_like(data['data']) * data[key]
    elif len(data[key]) > 1 and np.all(data[key] == data[key][0]):
        data[key] = data[key][0]
    return data


def _sort_data(k, uid_scans, data):
    """
    Retrieve settings of scan `k` and append to data.

    Parameters
    ----------
    k : int
        Scan number
    uid_scans : list
        A list containing `lxml.etree._Element` elements pointing to the scans in a xml tree.
    data : dict
        Data dictionary containing the measurement data and settings.

    Returns
    -------
    dict
        Same data dictionary as input dictionary `data`.
    """
    # get a scan
    scan = _get_scan_data(uid_scans, k)
    if scan:
        # append data to the completed data keys
        if data['measType'] == 'Scan' or scan['status'] == 'Completed':
            data['scannb'].append(k)
            for key in ['data', 'time', '2Theta', 'Omega', 'Phi', 'Psi', 'X', 'Y', 'Z']:
                if key in scan:
                    data = _append2arr(data, scan, key)
        # append data to the incomplete data keys
        # TODO: check if the following code actually works?!
        else:
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


def _append2arr(data, scan, key):
    """
    Append the data with key `key` from scan `scan` to the data dictionary.

    Parameters
    ----------
    data : dict
        Data dictionary containing the measurement data and settings.
    scan : dict
        Scan dictionary containing the measurement data and settings of one particular scan.
    key : str
        Parameter key of `scan` dictionary.

    Returns
    -------
    dict
        Same data dictionary as input dictionary `data`.
    """
    if data[key] == []:  # keep as is, otherwise it fails the test
        data[key] = scan[key]
    else:
        data[key] = np.vstack((data[key], scan[key]))
    return data


def _get_scan_data(uid_scans, scannb, namespace=None):
    """
    Get the data of scan with number `scannb`.

    Parameters
    ----------
    uid_scans : list
        A list containing `lxml.etree._Element` elements
        pointing to the scans in a xml tree.
    scannb : int
        ID of the scan.
    namespace : dict or None, optional
        A dictionary defining the namespace `ns`. If None,
        it is determined from the uid_scan.nsmap[None].

    Returns
    -------
    dict
        A dictionary containing the data and settings for
        the specified scan `scannb`.
    """
    if namespace is None:
        namespace = {'ns': uid_scans[0].nsmap[None]}

    # create output dictionary
    scan_data = {}

    # get correct scan
    uid_scan = uid_scans[scannb]

    # get the scan status
    scan_data['status'] = uid_scan.get('status')

    # get the scan axis type
    scan_data['scanAxis'] = uid_scan.get('scanAxis')

    # get dataPoint handler
    data_points = uid_scan.find('ns:dataPoints', namespaces=namespace)

    # get intensities
    intensities = data_points.findtext('ns:intensities', namespaces=namespace)

    scan_data['data'] = _txt_list2arr(intensities)
    units_intensities = data_points.find('ns:intensities', namespaces=namespace).get('unit')

    # get counting time
    scan_mode = uid_scan.get('mode')
    if scan_mode == 'Pre-set counts':
        time = data_points.findtext('ns:countingTimes', namespaces=namespace)
    else:
        time = data_points.findtext('ns:commonCountingTime', namespaces=namespace)
    scan_data['time'] = _txt_list2arr(time)

    # normalize intensity units to cps
    if units_intensities == 'counts':
        scan_data['data'] /= scan_data['time']

    # get the position of all axes
    uid_pos = data_points.findall('ns:positions', namespaces=namespace)
    n = len(scan_data['data'])  # nb of data points
    for pos in uid_pos:
        info = _read_axis_info(pos, n)
        if info['axis'] in ['2Theta', 'Omega', 'Phi', 'Psi', 'X', 'Y', 'Z']:
            scan_data[info['axis']] = info['data']
        else:
            print('axis type not supported')
    return scan_data


def _read_axis_info(uid_pos, n):
    """
    Get the settings for a given axis.

    Parameters
    ----------
    uid_pos : lxml.etree._Element
        A `lxml.etree._Element` element pointing to axis information in the xml tree.
    n : int
        Number of data points.

    Returns
    -------
    dict
        Axis settings stored in a dictionary.
    """
    info = {'axis': uid_pos.get('axis'), 'unit': uid_pos.get('unit'), 'data': np.array([0, 0])}
    is_array = True

    for child in list(uid_pos):
        if child.tag.find('listPositions') != -1:
            info['data'] = _txt_list2arr(child.text)
        elif child.tag.find('startPosition') != -1:
            info['data'][0] = np.double(child.text)
            is_array = False
        elif child.tag.find('endPosition') != -1:
            info['data'][1] = np.double(child.text)
            is_array = False
        elif child.tag.find('commonPosition') != -1:
            info['data'] = np.asarray(np.double(child.text))
        else:
            logger.debug('unsupported tag')
            info['data'] = np.array([])

    if not is_array:
        info['data'] = np.linspace(info['data'][0], info['data'][1], n)
    return info


def read_xrdml(filename):
    """
    Load a Panalytical XRDML file.

    Parameters
    ----------
    filename : str
        The filename of the xrdml file to be loaded.

    Returns
    -------
    dict
        A dictionary with all relevant data of the measurement.
    """
    if not os.path.exists(filename):
        logger.error('File "{}" does not exist.'.format(filename))
        raise ValueError('This is not a valid filename.')

    filename = os.path.abspath(filename)

    path, basename = os.path.split(filename)
    file_base, file_ext = os.path.splitext(basename)

    if file_ext == '':
        filename = file_base + '.xrdml'

    # check if file is conform with xml schema
    valid = validate_xrdml_schema(filename)
    if valid is None:
        raise ValueError('The file is not conform with hte xrdml schema.')

    tree = etree.parse(os.path.join(path, filename)).getroot()
    # define the namespace
    namespace = {'ns': tree.nsmap[None]}

    xrd_measurement = tree.find('ns:xrdMeasurement', namespaces=namespace)

    data = {'filename': filename,
            'sample': tree.findtext('ns:sample/ns:id', namespaces=namespace),
            'status': tree.get('status'),
            'comment': {}}

    # get comment (reads only the first comment, needs maybe improvement)
    lookup = tree.findtext('ns:comment/ns:entry', namespaces=namespace)
    data['comment']['1'] = lookup if lookup else ''

    # get nb. of scans
    uid_scans = xrd_measurement.findall('ns:scan', namespaces=namespace)
    nb_scans = len(uid_scans)

    # get (h k l) and substrate
    if nb_scans > 1:
        reflection_uid = xrd_measurement.find('ns:scan[1]/ns:reflection', namespaces=namespace)
        data['hkl'] = {'h': None, 'k': None, 'l': None}
        if reflection_uid is not None:
            data['substrate'] = reflection_uid.findtext('ns:material', namespaces=namespace)
            for hkl in 'hkl':
                data['hkl'][hkl] = int(reflection_uid.findtext('ns:hkl/ns:{}'.format(hkl), namespaces=namespace))
        else:
            data['substrate'] = ''

    # get measurement type
    data['measType'] = xrd_measurement.get('measurementType')

    # if not a simple scan and not the 'Repeated scan' than get
    # the step axis type
    if data['measType'] not in ['Scan', 'Repeated scan']:
        data['stepAxis'] = xrd_measurement.get('measurementStepAxis')

    # get the scan axis type
    if nb_scans > 0:
        data['scanAxis'] = uid_scans[0].get('scanAxis')

    # get scans
    for key in ['scannb', 'data', 'time', '2Theta', 'Omega', 'Phi', 'Psi', 'X', 'Y', 'Z',
                'iscannb', 'idata', 'itime', 'i2Theta', 'iOmega', 'iPhi', 'iPsi', 'iX', 'iY', 'iZ']:
        data[key] = []

    for k in range(nb_scans):
        scan = _get_scan_data(uid_scans, k, namespace=namespace)
        if scan:
            if data['measType'] == 'Scan' or scan['status'] == 'Completed':
                data['scannb'].append(k)
                for key in ['data', 'time', '2Theta', 'Omega', 'Phi', 'Psi', 'X', 'Y', 'Z']:
                    if key in scan:
                        data = _append2arr(data, scan, key)
            # TODO: check if this code actually works?!
            else:
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
    if data['scannb'] == [] and len(data['iscannb']) == 1:
        logger.debug('One and only incomplete scan found in the data. This scan is considered complete.')

        for key, ikey in zip(['scannb', 'data', 'time', '2Theta', 'Omega', 'Phi', 'Psi', 'X', 'Y', 'Z'],
                             ['iscannb', 'idata', 'itime', 'i2Theta', 'iOmega', 'iPhi', 'iPsi', 'iX', 'iY', 'iZ']):
            if ikey in data.keys() and data[ikey]:
                data[key] = data[ikey]
                data[ikey] = []

    # remove redundant information
    [data.pop(key) for key in ['Phi', 'Psi', 'X', 'Y', 'Z'] if data[key] == []]
    if len(data['iscannb']) == 0:
        for key in ['iscannb', 'idata', 'itime', 'i2Theta', 'iOmega', 'iPhi', 'iPsi', 'iX', 'iY', 'iZ']:
            data.pop(key)

    data = _get_array_for_single_value(data, 'time')

    if data['measType'] != 'Area measurement':
        data = _get_array_for_single_value(data, '2Theta')
        data = _get_array_for_single_value(data, 'Omega')

    if nb_scans > 1:
        for key in ['Phi', 'Psi', 'X', 'Y', 'Z']:
            data = _get_array_for_single_value(data, key)

    # in case of 'Repeated scan' sum all completed scans together and
    # remove redundant data
    if data['measType'] == 'Repeated scan':
        # average completed scans (intensity is in cps)
        for k in np.arange(1, len(data['scannb'])):
            data['data'][0] += data['data'][k]
        data['data'] = data['data'][0] / len(data['scannb'])
        # reduce all possible axis
        for key in ['2Theta', 'Omega', 'Phi', 'Psi', 'X', 'Y', 'Z']:
            data = _get_array_for_single_value(data, key)
        # set true time
        data['time'] *= len(data['scannb'])
        # remove redundant information about scan number
        data.pop('scannb')

    # get wavelength
    uid = xrd_measurement.find('ns:usedWavelength', namespaces=namespace)
    data['kType'] = uid.get('intended')
    data['kAlpha1'] = np.double(uid.findtext('ns:kAlpha1', namespaces=namespace))
    data['kAlpha2'] = np.double(uid.findtext('ns:kAlpha2', namespaces=namespace))
    data['kBeta'] = np.double(uid.findtext('ns:kBeta', namespaces=namespace))
    data['kAlphaRatio'] = np.double(uid.findtext('ns:ratioKAlpha2KAlpha1', namespaces=namespace))
    if data['kType'] == 'K-Alpha 1':
        data['Lambda'] = data['kAlpha1']
    elif data['kType'] == 'K-Alpha':
        data['Lambda'] = data['kAlpha1'] + data['kAlphaRatio'] * data['kAlpha2']
        data['Lambda'] /= 1.5
    else:
        print('usedWavelength type is not supported (using K-Alpha 1')
        data['Lambda'] = data['kAlpha1']

    # get some useful information (x/y-label, x/y-units)
    if nb_scans > 0:
        if 'scanAxis' in data.keys():
            if data['scanAxis'] == 'Gonio':
                data['xlabel'] = '2Theta-Theta'
                if data['measType'] in ['Scan', 'Repeated scan']:
                    data['x'] = data['2Theta']
            elif data['scanAxis'] in ['2Theta', '2Theta-Omega']:
                data['xlabel'] = data['scanAxis']
                if data['measType'] in ['Scan', 'Repeated scan']:
                    data['x'] = data['2Theta']
            elif data['scanAxis'] in ['Omega', 'Omega-2Theta']:
                data['xlabel'] = data['scanAxis']
                if data['measType'] in ['Scan', 'Repeated scan']:
                    data['x'] = data['Omega']
            elif data['scanAxis'] == 'Reciprocal Space':
                data['xlabel'] = 'Omega'
                if data['measType'] in ['Scan', 'Repeated scan']:
                    data['x'] = data['Omega']
            elif data['scanAxis'] in ['Phi', 'Psi', 'X', 'Y', 'Z']:
                data['xlable'] = data['scanAxis']
                if data['measType'] == 'Scan':
                    data['x'] = data[data['scanAxis']]
            else:
                logger.debug('The scanAxis type is not supported')
                data['xlabel'] = 'unknown'

            uid = xrd_measurement.find('ns:scan[1]/ns:dataPoints/ns:positions', namespaces=namespace)
            data['xunit'] = uid.get('unit', 'nd')

        if 'stepAxis' in data.keys():
            if data['stepAxis'] in ['2Theta', '2Theta-Omega', 'Omega', 'Omega-2Theta', 'Phi', 'Psi', 'X', 'Y', 'Z']:
                data['ylabel'] = data['stepAxis']
            elif data['stepAxis'] == 'Gonio':
                data['ylabel'] = '2Theta-Theta'
            else:
                print('scanAxis type not supported')
                data['ylabel'] = 'unknown'

            # TODO: maybe optimization possible, load units before
            uid = xrd_measurement.find('ns:scan[1]/ns:dataPoints/ns:positions', namespaces=namespace)
            data['yunit'] = uid.get('unit', 'nd')

    if data['measType'] == 'Area measurement':
        dim_2t = data['2Theta'].shape
        dim_o = data['Omega'].shape
        if dim_2t[1] != dim_o[1] and data['scanAxis'] == '2Theta' and data['stepAxis'] == 'Omega':
            tmp = np.empty_like(data['2Theta'])
            for k in range(dim_2t[1]):
                tmp[:, k] = data['Omega'].T
            data['Omega'] = tmp
            logger.debug('Omega array was corrected to match "2Theta" and "data" arrays')

    # Mask Width [OPTIONAL]
    xpath = 'ns:incidentBeamPath/ns:mask/ns:width'
    uid = xrd_measurement.find(xpath, namespaces=namespace)
    if uid is not None:
        unit = uid.get('unit')
        if unit != 'mm':
            logger.debug("Mask width units are not 'mm'")
        data['maskWidth'] = np.double(tree.findtext(xpath, namespaces=namespace))

    # Divergence slit Height [OPTIONAL]
    xpath = 'ns:incidentBeamPath/ns:divergenceSlit/ns:height'
    uid = xrd_measurement.find(xpath, namespaces=namespace)
    if uid is not None:
        unit = uid.get('unit')
        if unit != 'mm':
            logger.debug("Divergence slit height units are not 'mm'")
        data['slitHeight'] = np.double(xrd_measurement.findtext(xpath, namespaces=namespace))

    return data


if __name__ == '__main__':
    data = read_xrdml('test_area.xrdml')
