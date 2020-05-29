"""
Utilities for panel data estimation
"""

__author__ = "Luc Anselin lanselin@gmail.com, \
              Pedro V. Amaral pedrovma@gmail.com"

import numpy as np

__all__ = ["check_panel"]


def check_panel(y, x, w, name_y, name_x):
    """
    Check the data structure and converts from wide to long if needed.

    Parameters
    ----------
    y          : array
                 n*tx1 or nxt array for dependent variable
    x          : array
                 Two dimensional array with n*t rows and k columns for
                 independent (exogenous) variable or n rows and k*t columns
                 (note, must not include a constant term)
    name_y     : string or list of strings
                 Name of dependent variable for use in output
    name_x     : list of strings
                 Names of independent variables for use in output
    """

    # Check if 'y' is a balanced panel with respect to 'W'
    if y.shape[0] / w.n != y.shape[0] // w.n:
        raise Exception("y must be ntx1 or nxt, and w must be an nxn PySAL W"
                        "object.")
    # Wide format
    if y.shape[1] > 1:
        message = ("Assuming time data is in wide format, i.e. y[:, 0] refers"
                   "to T0, y[:, 1] refers to T1, etc.\nSimilarly, assuming"
                   "x[:, 0:T] refers to T periods of k1, x[:, T+1:2T] refers"
                   "to k2, etc.")
        print("Warning: " + message)
        N, T = y.shape[0], y.shape[1]
        k = x.shape[1] // T
        bigy = y.reshape((y.size, 1), order="F")
        bigx = x[:, 0:T].reshape((N * T, 1), order="F")
        for i in range(1, k):
            bigx = np.hstack(
                (bigx, x[:, T * i:T * (i + 1)].reshape((N * T, 1), order="F")))
    # Long format
    else:
        message = ("Assuming time data is in long format, i.e. y[0:N] refers"
                   "to T0, y[N+1:2N] refers to T1, etc. \n Similar for x.")
        print("Warning: " + message)
        T = y.shape[0] // w.n
        N = w.n
        k = x.shape[1]
        bigy, bigx = y, x
    # Fix name_y and name_x
    if name_y:
        if not isinstance(name_y, str) and not isinstance(name_y, list):
            raise Exception("name_y must either be strings or a list of"
                            "strings.")
        if len(name_y) > 1 and isinstance(name_y, list):
            name_y = ''.join([i for i in name_y[0] if not i.isdigit()])
        if len(name_y) == 1 and isinstance(name_y, list):
            name_y = name_y[0]
    if name_x:
        if len(name_x) != k * T and len(name_x) != k:
            raise Exception("Names of columns in X must have exactly either"
                            "k or k*t elements.")
        if len(name_x) > k:
            name_bigx = []
            for i in range(k):
                namek = "".join([j for j in name_x[i * T] if not j.isdigit()])
                name_bigx.append(namek)
            name_x = name_bigx

    return bigy, bigx, name_y, name_x


def demean_panel(arr, n, t):
    """
    Returns demeaned variable.

    Parameters
    ----------
    arr         : array
                  n*tx1 array
    n           : integer
                  Number of observations
    t           : integer
                  Number of time periods

    Returns
    -------
    arr_dm      : array
                  Demeaned variable
    """
    if arr.ndim > 1:
        arr = arr.reshape(-1)
    arr_mean = arr.reshape((n, t)).mean(axis=1)
    arr_dm = arr - np.tile(arr_mean, t)
    return arr_dm
