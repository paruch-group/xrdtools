import numpy as np


def qmap(data, omoff=0, ttoff=0):
    """ This function calculates kpar, kperp

    Parameters
    ----------
    data : dictonary
        loaded by readxrdml.read_file
    omoff : float
        omega angle offset
    ttoff : float
        2theta angle offset (honestly I think it shouldn't be anything but 0)

    Returns
    -------
    kpar : array-like
    kperp : array-like
    """

    tt = data['2Theta'] + ttoff
    om = data['Omega'] + omoff
    lambd = data['Lambda']
    return transform_angle2qvector(tt, om, lambd)


def transform_angle2qvector(tt, om, lambd):
    """
    Calculate the q-vector from the 2theta and omega angle and the x-ray wavelength lambd.

    Parameters
    ----------
    tt : array-like
    om : array-like
    lambd : float

    Returns
    -------
    kpar : array-like
    kperp : array-like
    """
    # convert degrees to radians
    ttrad = np.radians(tt)
    trad = ttrad / 2.
    omrad = np.radians(om)

    # calculate kpar, kperp
    delta = trad - omrad
    deltak = 2./lambd * np.sin(trad)

    kperp = deltak * np.cos(delta)
    kpar = deltak * np.sin(delta)

    return kpar, kperp


def q2hklmap(x, y, latt_params, hkl, lambd):
    h = hkl['h']
    k = hkl['k']
    l = hkl['l']

    a = latt_params[0]
    b = latt_params[1]
    c = latt_params[2]

    x /= np.sqrt((h/a)**2+(k/b)**2)
    y *= c
    return x, y


def angles(hkl_dic, lambd=1.54, latt_param=[3.905, 3.905, 3.905]):

    # lattice parameters, 90 degree angles
    a0 = latt_param[0]
    a1 = latt_param[1]
    a2 = latt_param[2]

    h_dat = hkl_dic['h']
    k_dat = hkl_dic['k']
    l_dat = hkl_dic['l']
#     if hkl['h'] != 0:
#         h_dat = hkl_dic[0]
#     if hkl['k'] != 0:
#         k_dat = hkl_dic[0]
#     if hkl['l'] != 0:
#         l_dat = hkl_dic[1]


    # calculation
    d_hkl = 1/np.sqrt((h_dat/a0)**2 + (k_dat/a1)**2 + (l_dat/a2)**2)

    theta = np.degrees(np.arcsin(lambd/(2*d_hkl)))

    offset_oop = np.degrees(np.arctan(1/np.sqrt((l_dat/a2)**2)/(1/np.sqrt((h_dat/a0)**2 + (k_dat/a1)**2))))

    #offset_ip = np.degrees(np.arctan(1/np.sqrt(((k_dat/a1)**2)/(1/np.sqrt((h_dat/a0)**2))))) #not needed here
    #phi = offset_ip

    tt = 2*theta

    om1 = theta - offset_oop

    delta = offset_oop

    return tt, om1, delta