"""
Based on code from : chaosmagpy, Clemens Kloss (DTU Space) and pyIGRF, Ciaran Beggan (British Geological Survey)
"""

import os
import pandas as pd
import numpy as np
from math import pi
from datetime import datetime
from logging import getLogger

from src.magnetopy.magnetopy_utils.magnetopy_logging import MagnetopyLogging


r2d = np.rad2deg
d2r = np.deg2rad

class IGRF:
    def __init__(self, time, coeffs, parameters):
        self.__magnetopy_logging: getLogger = MagnetopyLogging().create_magnetopy_logging(logger='IGRF')
        self.time = time
        self.coeffs = coeffs
        self.parameters = parameters

class MagnetoPyIGRFHelper:
    def load_igrf_coefficients(self):
        """
        This function loads the shc-file with the IGRF-13 coefficients and return a IGRF object.

        :return: IGRF object
        """
        magnetopy_logging: getLogger = MagnetopyLogging().create_magnetopy_logging(logger='MagnetoPyIGRFHelper: load_igrf_coefficients')
        magnetopy_logging.info('Loading the IGRF coefficients')
        resources_path = os.path.abspath('resources')
        igrf13_full_path = os.path.join(resources_path, 'igrf13')
        igrf13_file = os.path.join(igrf13_full_path, 'IGRF13.shc')

        if not os.path.exists(igrf13_file):
            raise FileNotFoundError(f"IGRF coefficients file not found: {igrf13_file}")

        with open(igrf13_file, 'r') as f:

            data = np.array([])
            for line in f.readlines():
                if line.startswith('#'):
                    continue

                read_line = np.fromstring(line, sep=' ')
                if read_line.size == 7:
                    name = os.path.split(igrf13_file)[1]
                    values = [name] + read_line.astype(int).tolist()
                else:
                    data = np.append(data, read_line)

        keys = ['SHC', 'nmin', 'nmax', 'N', 'order', 'step', 'start_year', 'end_year']
        parameters = dict(zip(keys, values))

        time = data[:parameters['N']]
        coeffs = data[parameters['N']:].reshape((-1, parameters['N']+2))
        coeffs = np.squeeze(coeffs[:, 2:])

        magnetopy_logging.info(f'IGRF coefficients from file: {igrf13_file} loaded successfully.')

        return IGRF(time, coeffs, parameters)


    def gg_to_geo(self, h, gdcolat):
        """
        Compute geocentric colatitude and radius from geodetic colatitude and
        height.

        Parameters
        ----------
        h : ndarray, shape (...)
            Altitude in kilometers.
        gdcolat : ndarray, shape (...)
            Geodetic colatitude

        Returns
        -------
        radius : ndarray, shape (...)
            Geocentric radius in kilometers.
        theta : ndarray, shape (...)
            Geocentric colatitude in degrees.
        
        sd : ndarray shape (...) 
            rotate B_X to gd_lat 
        cd :  ndarray shape (...) 
            rotate B_Z to gd_lat 

        References
        ----------
        Equations (51)-(53) from "The main field" (chapter 4) by Langel, R. A. in:
        "Geomagnetism", Volume 1, Jacobs, J. A., Academic Press, 1987.
        
        Malin, S.R.C. and Barraclough, D.R., 1981. An algorithm for synthesizing 
        the geomagnetic field. Computers & Geosciences, 7(4), pp.401-405.

        """
        # Use WGS-84 ellipsoid parameters
        eqrad = 6378.137 # equatorial radius
        flat  = 1/298.257223563
        plrad = eqrad*(1-flat) # polar radius
        ctgd  = np.cos(np.deg2rad(gdcolat))
        stgd  = np.sin(np.deg2rad(gdcolat))
        a2    = eqrad*eqrad
        a4    = a2*a2
        b2    = plrad*plrad
        b4    = b2*b2
        c2    = ctgd*ctgd
        s2    = 1-c2
        rho   = np.sqrt(a2*s2 + b2*c2)
        
        rad   = np.sqrt(h*(h+2*rho) + (a4*s2+b4*c2)/rho**2)

        cd    = (h+rho)/rad
        sd    = (a2-b2)*ctgd*stgd/(rho*rad)
        
        cthc  = ctgd*cd - stgd*sd           # Also: sthc = stgd*cd + ctgd*sd
        thc   = np.rad2deg(np.arccos(cthc)) # arccos returns values in [0, pi]
        
        return rad, thc, sd, cd
    

    def geo_to_gg(self, radius, theta):
        """
        Compute geodetic colatitude and vertical height above the ellipsoid from
        geocentric radius and colatitude.

        Parameters
        ----------
        radius : ndarray, shape (...)
            Geocentric radius in kilometers.
        theta : ndarray, shape (...)
            Geocentric colatitude in degrees.

        Returns
        -------
        height : ndarray, shape (...)
            Altitude in kilometers.
        beta : ndarray, shape (...)
            Geodetic colatitude

        Notes
        -----
        Round-off errors might lead to a failure of the algorithm especially but
        not exclusively for points close to the geographic poles. Corresponding
        geodetic coordinates are returned as NaN.

        References
        ----------
        Function uses Heikkinen's algorithm taken from:

        Zhu, J., "Conversion of Earth-centered Earth-fixed coordinates to geodetic
        coordinates", IEEE Transactions on Aerospace and Electronic Systems}, 1994,
        vol. 30, num. 3, pp. 957-961

        """
        
        # Use WGS-84 ellipsoid parameters
        a =  6378.137  # equatorial radius
        b =  6356.752  # polar radius
        
        a2 = a**2
        b2 = b**2

        e2 = (a2 - b2) / a2  # squared eccentricity
        e4 = e2*e2
        ep2 = (a2 - b2) / b2  # squared primed eccentricity

        r = radius * np.sin(np.radians(theta))
        z = radius * np.cos(np.radians(theta))

        r2 = r**2
        z2 = z**2

        F = 54*b2*z2

        G = r2 + (1. - e2)*z2 - e2*(a2 - b2)

        c = e4*F*r2 / G**3

        s = (1. + c + np.sqrt(c**2 + 2*c))**(1./3)

        P = F / (3*(s + 1./s + 1.)**2 * G**2)

        Q = np.sqrt(1. + 2*e4*P)

        r0 = -P*e2*r / (1. + Q) + np.sqrt(0.5*a2*(1. + 1./Q) - P*(1. - e2)*z2 / (Q*(1. + Q)) - 0.5*P*r2)

        U = np.sqrt((r - e2*r0)**2 + z2)

        V = np.sqrt((r - e2*r0)**2 + (1. - e2)*z2)

        z0 = b2*z/(a*V)

        height = U*(1. - b2 / (a*V))

        beta = 90. - np.degrees(np.arctan2(z + ep2*z0, r))

        return height, beta
    
    def synth_values(self, coeffs, radius, theta, phi, nmax=None, nmin=None, grid=None):
        """
        Based on code from : chaosmagpy, Clemens Kloss (DTU Space) and pyIGRF, Ciaran Beggan (British Geological Survey)
        Computes radial, colatitude and azimuthal field components from the
        magnetic potential field in terms of spherical harmonic coefficients.
        
        :param coeffs: numpy.ndarray, shape (..., N)
            Coefficients of the spherical harmonic expansion. The last dimension is
            equal to the number of coefficients, `N` at the grid points.
        :param radius: float or numpy.ndarray, shape (...,)
            Array containing the radius in kilometers.
        :param theta: float or numpy.ndarray, shape (...,)
            Array containing the colatitude in degrees. :math: `[0^\\circ, 180^\\circ]`.
        :param phi: float or numpy.ndarray, shape (...,)
            Array containing the longitude in degrees.
        :param nmax: int, positive, optional
            Maximum degree up to which expansion is to be used (default is
            given by the ``coeffs``, but can also be smaller if specified).
            :math: `N` :math: `\\geq` ``nmax`` (``nmax`` + 2)
        :param nmin: int, positive, optional
            Minimum degree from which expansion is to be used (default is 1).
            Note that it will just skip the degrees smaller than ``nmin``, the
            whole sequence of coefficients 1 through ``nmax`` must still be given
            in ``coeffs``. Magnetic field source (default is an internal source).
        :param grid: bool, optional
            If True, field components are computed on a regular grid, Arrays
            ``theta`` and ``phi`` must have one dimension less than the output grid
            since the grid will be created as their outer product (defaults to
            False).

        :return: numpy.ndarray, shape (...)
            B_radius, B_theta, B_phi field components.
            Radial, colatitude and azimuthal field components.
        """
        magnetopy_logging: getLogger = MagnetopyLogging().create_magnetopy_logging(logger='MagnetoPyIGRFHelper: synth_values')

        coeffs = np.array(coeffs, dtype=float)
        radius = np.array(radius, dtype=float) / 6371.2
        theta = np.array(theta, dtype=float)
        phi = np.array(phi, dtype=float)

        if np.amin(theta) <= 0.0 or np.amax(theta) >= 180.0:
            if np.amin(theta) == 0.0 or np.amax(theta) == 180.0:
                magnetopy_logging.warning('The geographic poles are included.')
            else:
                raise ValueError('Colatitude outside bounds [0, 180].')
            
        if nmin is None:
            nmin = 1
        else:
            assert nmin > 0, 'Only positive nmin allowed.'

        nmax_coeffs = int(np.sqrt(coeffs.shape[-1] + 1) - 1)
        if nmax is None:
            nmax = nmax_coeffs
        else:
            assert nmax > 0, 'Only positive nmax allowed.'

        if nmax > nmax_coeffs:
            raise ValueError(f'Supplied nmax = {nmax} and nmin = {nmin} is incompatible with number of model coefficients. \nUsing nmax = {nmax_coeffs} instead.')
            nmax = nmax_coeffs

        if nmax < nmin:
            raise ValueError(f'Nothing to compute: nmax < nmin ({nmax} < {nmin}.)')
        
        grid = False if grid is None else grid

        if grid:
            theta = theta[..., None]
            phi = phi[None, ...]

        try:
            b = np.broadcast(radius, theta, phi, np.broadcast_to(0, coeffs.shape[:-1]))
        except ValueError:
            magnetopy_logging.error('Cannot broadcast grid shapes (excl. last dimension of coeffs):')
            magnetopy_logging.error(f'radius: {radius.shape}\n theta: {theta.shape}\n phi: {phi.shape}\n coeffs: {coeffs.shape[:-1]}')
            raise

        grid_shape = b.shape

        r_n = radius**(-(nmin+2))

        Pnm = self.legendre_poly(nmax, theta)

        sinth = Pnm[1, 1]

        phi = np.radians(phi)
        cmp = np.cos(np.multiply.outer(np.arange(nmax+1), phi))
        smp = np.sin(np.multiply.outer(np.arange(nmax+1), phi))

        B_radius = np.zeros(grid_shape)
        B_theta = np.zeros(grid_shape)
        B_phi = np.zeros(grid_shape)

        num = nmin**2 - 1
        for n in range(nmin, nmax+1):
            B_radius += (n+1) * Pnm[n, 0] * r_n * coeffs[..., num]
            B_theta += -Pnm[0, n+1] * r_n * coeffs[..., num]
            num += 1

            for m in range(1, n+1):
                B_radius += ((n+1) * Pnm[n, m] * r_n * (coeffs[..., num] * cmp[m] + coeffs[..., num+1] * smp[m]))
                
                B_theta += (-Pnm[m, n+1] * r_n * (coeffs[..., num] * cmp[m] + coeffs[..., num+1] * smp[m]))

                with np.errstate(divide='ignore', invalid='ignore'):
                    # handle poles using L'Hopital's rule
                    div_Pnm = np.where(theta == 0., Pnm[m, n+1], Pnm[n, m] / sinth)
                    div_Pnm = np.where(theta == np.degrees(pi), -Pnm[m, n+1], div_Pnm)

                B_phi += (m * div_Pnm * r_n * (coeffs[..., num] * smp[m] - coeffs[..., num+1] * cmp[m]))

                num += 2

            r_n = r_n / radius

        return B_radius, B_theta, B_phi

    def legendre_poly(self, nmax, theta):
        """
        Returns associated Legendre polynomials `P(n,m)` (Schmidt quasi-normalized)
        and the derivative :math:`dP(n,m)/d\\theta` evaluated at :math:`\\theta`.

        Parameters
        ----------
        nmax : int, positive
            Maximum degree of the spherical expansion.
        theta : ndarray, shape (...)
            Colatitude in degrees :math:`[0^\\circ, 180^\\circ]`
            of arbitrary shape.

        Returns
        -------
        Pnm : ndarray, shape (n, m, ...)
            Evaluated values and derivatives, grid shape is appended as trailing
            dimensions. `P(n,m)` := ``Pnm[n, m, ...]`` and `dP(n,m)` :=
            ``Pnm[m, n+1, ...]``
        """

        costh = np.cos(np.radians(theta))
        sinth = np.sqrt(1-costh**2)

        Pnm = np.zeros((nmax+1, nmax+2) + costh.shape)
        Pnm[0, 0] = 1  
        Pnm[1, 1] = sinth  

        rootn = np.sqrt(np.arange(2 * nmax**2 + 1))

        # Recursion relations after Langel "The Main Field" (1987),
        # eq. (27) and Table 2 (p. 256)
        for m in range(nmax):
            Pnm_tmp = rootn[m+m+1] * Pnm[m, m]
            Pnm[m+1, m] = costh * Pnm_tmp

            if m > 0:
                Pnm[m+1, m+1] = sinth*Pnm_tmp / rootn[m+m+2]

            for n in np.arange(m+2, nmax+1):
                d = n * n - m * m
                e = n + n - 1
                Pnm[n, m] = ((e * costh * Pnm[n-1, m] - rootn[d-e] * Pnm[n-2, m])
                            / rootn[d])

        # dP(n,m) = Pnm(m,n+1) is the derivative of P(n,m) vrt. theta
        Pnm[0, 2] = -Pnm[1, 1]
        Pnm[1, 2] = Pnm[1, 0]
        for n in range(2, nmax+1):
            Pnm[0, n+1] = -np.sqrt((n*n + n) / 2) * Pnm[n, 1]
            Pnm[1, n+1] = ((np.sqrt(2 * (n*n + n)) * Pnm[n, 0]
                        - np.sqrt((n*n + n - 2)) * Pnm[n, 2]) / 2)

            for m in np.arange(2, n):
                Pnm[m, n+1] = (0.5*(np.sqrt((n + m) * (n - m + 1)) * Pnm[n, m-1]
                            - np.sqrt((n + m + 1) * (n - m)) * Pnm[n, m+1]))

            Pnm[n, n+1] = np.sqrt(2 * n) * Pnm[n, n-1] / 2

        return Pnm

    def xyz2dhif(self, x, y, z):
        """Calculate D, H, I and F from (X, Y, Z)
        
        Based on code from D. Kerridge, 2019
        
        Parameters
        ---------------
        X: north component (nT) : float
        Y: east component (nT) : float
        Z: vertical component (nT) : float
        
        Returns
        ------
        A tuple: (D, H, I, F) : float
        D: declination (degrees) : float
        H: horizontal intensity (nT) : float
        I: inclination (degrees) : float
        F: total intensity (nT) : float
        """
        hsq = x*x + y*y
        hoz  = np.sqrt(hsq)
        eff = np.sqrt(hsq + z*z)
        dec = np.arctan2(y,x)
        inc = np.arctan2(z,hoz)
        
        return r2d(dec), hoz, r2d(inc), eff


    def xyz2dhif_sv(self, x, y, z, xdot, ydot, zdot):
        """Calculate secular variation in D, H, I and F from (X, Y, Z) and
        (Xdot, Ydot, Zdot)
        
        Based on code from D. Kerridge, 2019
        
        Parameters
        ---------------
        X: north component (nT) : float  
        Y: east component (nT) : float
        Z: vertical component (nT) : float
        Xdot=dX/dt : rate of change of X : float
        Ydot=dY/dt : rate of change of Y : float
        Zdot=dZ/dt : rate of change of Z : float
        
        Returns
        ------
        A tuple: (Ddot, Hdot, Idot, Fdot)
        Ddot: rate of change of declination (degrees/year)
        Hdot: rate of change of horizontal intensity (nT/year)
        Idot: rate of change of inclination (degrees/year)
        Fdot: rate of change of total intensity (nT/year)
        


        """
        h2  = x*x + y*y
        h   = np.sqrt(h2)
        f2  = h2 + z*z
        hdot = (x*xdot + y*ydot)/h
        fdot = (x*xdot + y*ydot + z*zdot)/np.sqrt(f2)
        ddot = r2d((xdot*y - ydot*x)/h2)*60
        idot = r2d((hdot*z - h*zdot)/f2)*60
        
        return ddot, hdot, idot, fdot