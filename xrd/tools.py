import numpy as np


def get_qmap(data, omega_offset=0):
    """ Function to calculate kpar, kperp.

    :param dict data: xrdml data
    :param flaot omega_offset: omega angle offset

    :returns (ndarray, ndarray) kpar, kperp:
    """
    om = data['Omega'] + omega_offset
    lambd = data['Lambda']
    return angle2qvector(data['2Theta'], om, lambd)


def angle2qvector(tt, om, lam):
    """
    Calculate the q-vector from the 2theta and omega angle and the x-ray wavelength lam.

    :param ndarray tt:
    :param ndarray om:
    :param float lam:

    :return (ndarray, ndarray) kpar, kperp:
    """
    # convert degrees to radians
    tt_rad = np.radians(tt)
    t_rad = tt_rad / 2.
    om_rad = np.radians(om)

    # calculate kpar, kperp
    delta = t_rad - om_rad
    delta_k = 2./lam * np.sin(t_rad)

    kperp = delta_k * np.cos(delta)
    kpar = delta_k * np.sin(delta)

    return kpar, kperp


def q2hk_l_map(x, y, lattice_params=(3.905, 3.905, 3.905), hkl=None):
    """
    Compute the hk coordinates for a given q vector.

    :param ndarray x:
    :param ndarray y:
    :param (float, float, float) lattice_params:
    :param dict | None hkl:
    :return (ndarray, ndarray) x, y:
    """
    if hkl is None:
        hkl = {'h': 0, 'k': 0, 'l': 1}
    a, b, c = lattice_params

    x /= np.sqrt((hkl['h']/a)**2+(hkl['k']/b)**2)
    y *= c
    return x, y


def angles(hkl, lam=1.54, lattice_param=(3.905, 3.905, 3.905)):
    """
    Compute the 2Theta, Omega and Delta angle for a given hkl point, wavelength lambda and
    unit cell lattice parameters.

    :param dict hkl:
    :param float lam:
    :param (float, float, float) lattice_param:
    :return (ndarray, ndarray, ndarray) tt, omega, delta:
    """
    # lattice parameters, 90 degree angles
    a0, a1, a2 = lattice_param

    h = hkl['h']
    k = hkl['k']
    l = hkl['l']

    # calculation
    d_hkl = 1/np.sqrt((h/a0)**2 + (k/a1)**2 + (l/a2)**2)

    theta = np.degrees(np.arcsin(lam/(2*d_hkl)))
    offset_oop = np.degrees(np.arctan(1/np.sqrt((l/a2)**2)/(1/np.sqrt((h/a0)**2 + (k/a1)**2))))

    tt = 2*theta
    omega = theta - offset_oop
    delta = offset_oop

    return tt, omega, delta



# for backward compatibility
qmap = get_qmap
transfrom_angle2qvector = angle2qvector
q2hklmap = q2hk_l_map