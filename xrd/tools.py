"""
The MIT License (MIT)

Copyright (c) 2015 Benedikt Ziegler

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import numpy as np


def get_qmap(data, omega_offset=0):
    """Function to calculate kpar, kperp.

    Parameters
    ----------
    data : dict
        A xrdml data dictionary.
    omega_offset : float
        Offset for the omega angle.

    Returns
    -------
    kpar : ndarray
    kperp : ndarray
    """
    om = data['Omega'] + omega_offset
    lambd = data['Lambda']
    return angle2qvector(data['2Theta'], om, lambd)


# for backward compatibility
qmap = get_qmap


def angle2qvector(tt, om, lam=1.54):
    """Convert angles to q vector.

    Calculate the q-vector from the 2theta `tt` and omega `om` angle and
    the x-ray wavelength lambda `lam`.

    Parameters
    ----------
    tt : array-like
        Array containing the 2Theta values.
    om : array-like
        Array containing the Omega values.
    lam : float
        The wavelength lambda in Angstrom [Default: 1.54].

    Returns
    -------
    kpar : ndarray
    kperp : ndarray
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


# for backward compatibility
transfrom_angle2qvector = angle2qvector


def q2hkl_map(x, y, lattice_params=(3.905, 3.905, 3.905), hkl=None):
    """Compute the hk coordinates for a given q vector.

    Parameters
    ----------
    x : ndarray
    y : ndarray
    lattice_params : tuple
        A tuple of three floats for the lattice parameter.
    hkl : dict
        A dictionary containing the hkl values. Defaults to 001 if not given [Default: None].

    Returns
    -------
    x : ndarray
    y : ndarray
    """
    if hkl is None:
        hkl = {'h': 0, 'k': 0, 'l': 1}
    a, b, c = lattice_params

    x /= np.sqrt((hkl['h']/a)**2+(hkl['k']/b)**2)
    y *= c
    return x, y


# for backward compatibility
q2hklmap = q2hkl_map


def angles(hkl, lam=1.54, lattice_param=(3.905, 3.905, 3.905)):
    """Compute the angle for a given hkl position.

    Compute the 2Theta, Omega and Delta angle for a given hkl point, wavelength lambda and
    unit cell lattice parameters.

    Parameters
    ----------
    hkl : dict
        A dictionary containing the hkl values.
    lam : float
        The wavelength lambda in Angstrom. Defaults to 1.54.
    lattice_params : tuple
        A tuple of three floats for the lattice parameter.

    Returns
    -------
    tt : ndarray
    omega : ndarray
    delta : ndarray
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
