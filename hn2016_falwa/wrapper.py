import numpy as np

def barotropic_eqlat_lwa(ylat,vort,area,dmu,n_points,planet_radius = 6.378e+6):
    """
    Compute equivalent latitude and wave activity on a barotropic sphere.

    Parameters
    ----------
    ylat : sequence or array_like
        1-d numpy array of latitude (in degree) with equal spacing in ascending order; dimension = nlat.
    vort : ndarray
        2-d numpy array of vorticity values; dimension = (nlat, nlon).
    area : ndarray
        2-d numpy array specifying differential areal element of each grid point; dimension = (nlat, nlon).
    dmu: sequence or array_like
        1-d numpy array of latitudinal differential length element (e.g. dmu = cos(lat) d(lat)). Size = nlat.
    n_points : int, default None
        Analysis resolution to calculate equivalent latitude. If input as None, it will be initialized as *nlat*.
    planet_radius : float, default 6.378e+6
        radius of spherical planet of interest consistent with input 'area'.

    Returns
    -------
    qref : ndarray
        1-d numpy array of value Q(y) where latitude y is given by ylat; dimension = (nlat).
    lwa_result : ndarray
        2-d numpy array of local wave activity values;
                    dimension = [nlat_s x nlon]
    """

    from hn2016_falwa import basis

    nlat = vort.shape[0]
    nlon = vort.shape[1]
    if n_points is None:
        n_points = nlat

    qref, dummy = basis.eqvlat(ylat, vort, area, n_points, planet_radius=planet_radius)
    lwa_result, dummy = basis.lwa(nlon, nlat, vort, qref, dmu)

    return qref, lwa_result


def barotropic_input_qref_to_compute_lwa(ylat,qref,vort,area,dmu,planet_radius = 6.378e+6): # used to be Eqlat_LWA
    """
    This function computes LWA based on a *prescribed* Qref instead of Qref obtained from the vorticity field on a barotropic sphere.

    Parameters
    ----------
    ylat : sequence or array_like
        1-d numpy array of latitude (in degree) with equal spacing in ascending order; dimension = nlat.
    qref : sequence or array_like
        1-d numpy array of prescribed reference value of vorticity at each latitude; dimension = nlat.
    vort : ndarray
        2-d numpy array of vorticity values; dimension = (nlat, nlon).
    area : ndarray
        2-d numpy array specifying differential areal element of each grid point; dimension = (nlat, nlon).
    dmu: sequence or array_like
        1-d numpy array of latitudinal differential length element (e.g. dmu = cos(lat) d(lat)). Size = nlat.
    planet_radius : float, default 6.378e+6
        radius of spherical planet of interest consistent with input 'area'.

    Returns
    -------
    lwa_result : ndarray
        2-d numpy array of local wave activity values; dimension = [nlat_s x nlon]
    """

    nlat = vort.shape[0]
    nlon = vort.shape[1]
    lwa_result = lwa(nlon,nlat,vort,qref,dmu)
    return lwa_result




def eqvlat_hemispheric(ylat, vort, area, nlat_s=None, n_points=None,
                       planet_radius=6.378e+6):

    """
    Compute equivalent latitude in a hemispheric domain.

    Parameters
    ----------
    ylat : sequence or array_like
        1-d numpy array of latitude (in degree) with equal spacing in ascending order; dimension = nlat.
    vort : ndarray
        2-d numpy array of vorticity values; dimension = (nlat, nlon).
    area : ndarray
        2-d numpy array specifying differential areal element of each grid point; dimension = (nlat, nlon).
    nlat_s : int, default None
        The index of grid point that defines the extent of hemispheric domain from the pole. If input as None, it will be initialize as int(nlat/2).
    n_points : int, default None
        Analysis resolution to calculate equivalent latitude. If input as None, it will be initialized as *nlat_s*.
    planet_radius : float, default 6.378e+6
        radius of spherical planet of interest consistent with input 'area'.

    Returns
    -------
    q_part : ndarray
        1-d numpy array of value Q(y) where latitude y is given by ylat; dimension = (nlat).

    """
    from hn2016_falwa import basis

    nlat = vort.shape[0]
    qref = np.zeros(nlat)
    brac = np.zeros(nlat)

    if nlat_s is None:
        nlat_s = int(nlat/2)

    if n_points is None:
        n_points = nlat_s

    # --- Southern Hemisphere ---
    qref1, dummy = basis.eqvlat(ylat[:nlat_s], vort[:nlat_s, :], area[:nlat_s, :],
                                n_points, planet_radius=planet_radius)
    qref[:nlat_s] = qref1

    # --- Northern Hemisphere ---
    vort2 = -vort[::-1, :]  # Added the minus sign, but gotta see if NL_North is affected
    qref2, dummy = basis.eqvlat(ylat[:nlat_s], vort2[:nlat_s, :], area[:nlat_s, :],
                                n_points, planet_radius=planet_radius)

    qref[-nlat_s:] = qref2[::-1]

    return qref


def eqvlat_bracket_hemispheric(ylat, vort, area, nlat_s=None, n_points=None,
                               planet_radius=6.378e+6, vgrad=None):

    """
    Compute equivalent latitude and <...>_Q in Nakamura and Zhu (2010) in a hemispheric domain.

    Parameters
    ----------
    ylat : sequence or array_like
        1-d numpy array of latitude (in degree) with equal spacing in ascending order; dimension = nlat.
    vort : ndarray
        2-d numpy array of vorticity values; dimension = (nlat, nlon).
    area : ndarray
        2-d numpy array specifying differential areal element of each grid point; dimension = (nlat, nlon).
    nlat_s : int, default None
        The index of grid point that defines the extent of hemispheric domain from the pole. If input as None, it will be initialize as int(nlat/2).
    n_points : int, default None
        Analysis resolution to calculate equivalent latitude. If input as None, it will be initialized as *nlat_s*.
    planet_radius : float, default 6.378e+6
        radius of spherical planet of interest consistent with input 'area'.
    vgrad: ndarray, optional
        2-d numpy array of laplacian (or higher-order laplacian) values; dimension = (nlat, nlon)

    Returns
    -------
    q_part : ndarray
        1-d numpy array of value Q(y) where latitude y is given by ylat; dimension = (nlat).
    brac : ndarray or None
        1-d numpy array of averaged vgrad in the square bracket.
        If *vgrad* = None, *brac* = None.

    """
    from hn2016_falwa import basis

    nlat = vort.shape[0]
    qref = np.zeros(nlat)
    brac = np.zeros(nlat)

    if nlat_s is None:
        nlat_s = int(nlat/2)

    if n_points is None:
        n_points = nlat_s

    # --- Southern Hemisphere ---
    qref1, brac1 = basis.eqvlat(ylat[:nlat_s], vort[:nlat_s,:], area[:nlat_s,:],
                                n_points, planet_radius=planet_radius,vgrad=vgrad)
    qref[:nlat_s] = qref1

    # --- Northern Hemisphere ---
    vort2 = -vort[::-1, :]  # Added the minus sign, but gotta see if NL_North is affected
    qref2, brac2 = basis.eqvlat(ylat[:nlat_s], vort2[:nlat_s, :], area[:nlat_s, :],
                                n_points, planet_radius=planet_radius, vgrad=vgrad)

    qref[-nlat_s:] = qref2[::-1]

    brac[:nlat_s] = brac1
    brac[-nlat_s:] = brac2[::-1]

    return qref, brac


def qgpv_eqlat_lwa(ylat, vort, area, dmu, nlat_s=None, n_points=None,
                   planet_radius=6.378e+6):

    """
    Compute equivalent latitutde *qref* and local wave activity *lwa_result* based
    on Quasi-geostrophic potential vorticity field *vort* at a pressure level as
    outlined in Huang and Nakamura (2017).

    Parameters
    ----------
    ylat : sequence or array_like
        1-d numpy array of latitude (in degree) with equal spacing in ascending order; dimension = nlat.
    vort : ndarray
        2-d numpy array of Quasi-geostrophic potential vorticity field; dimension = (nlat, nlon).
    area : ndarray
        2-d numpy array specifying differential areal element of each grid point; dimension = (nlat, nlon).
    dmu: sequence or array_like
        1-d numpy array of latitudinal differential length element (e.g. dmu = cos(lat) d(lat)). Size = nlat.
    nlat_s : int, default None
        The index of grid point that defines the extent of hemispheric domain from the pole. If input as None, it will be initialize as int(nlat/2).
    n_points : int, default None
        Analysis resolution to calculate equivalent latitude. If input as None, it will be initialized as *nlat_s*.
    planet_radius : float, default 6.378e+6
        radius of spherical planet of interest consistent with input 'area'.

    Returns
    -------
    qref : ndarray
        1-d numpy array of value Q(y) where latitude y is given by ylat; dimension = (nlat).
    lwa_result : ndarray
        2-d numpy array of local wave activity values;
                    dimension = [nlat_s x nlon]

    """

    from hn2016_falwa import basis

    nlat = vort.shape[0]
    nlon = vort.shape[1]

    if nlat_s is None:
        nlat_s = int(nlat/2)

    if n_points is None:
        n_points = nlat_s

    qref = np.zeros(nlat)
    lwa_result = np.zeros((nlat, nlon))

    # --- Southern Hemisphere ---
    qref1, dummy = basis.eqvlat(ylat[:nlat_s], vort[:nlat_s, :], area[:nlat_s, :],
                         n_points, planet_radius=planet_radius)
    qref[:nlat_s] = qref1
    lwa_result[:nlat_s, :], dummy = basis.lwa(nlon, nlat_s,
                                              vort[:nlat_s, :],
                                              qref1, dmu[:nlat_s])

    # --- Northern Hemisphere ---
    vort2 = -vort[::-1, :]  # Added the minus sign, but gotta see if NL_North is affected
    qref2, dummy = basis.eqvlat(ylat[:nlat_s], vort2[:nlat_s, :], area[:nlat_s, :],
                         n_points, planet_radius=planet_radius)
    qref[-nlat_s:] = -qref2[::-1]
    lwa_result[-nlat_s:, :], dummy = basis.lwa(nlon, nlat_s,
                                               vort[-nlat_s:, :],
                                               qref[-nlat_s:],
                                               dmu[-nlat_s:])
    return qref, lwa_result


def qgpv_eqlat_lwa_ncforce(ylat, vort, ncforce, area, dmu, nlat_s=None,
                           n_points=None, planet_radius=6.378e+6):

    """
    Compute equivalent latitutde *qref*, local wave activity *lwa_result* and
    non-conservative force on wave activity *bigsigma_result* based on Quasi-
    geostrophic potential vorticity field *vort* at a pressure level as
    outlined in Huang and Nakamura (2017).

    Parameters
    ----------
    ylat : sequence or array_like
        1-d numpy array of latitude (in degree) with equal spacing in ascending order; dimension = nlat.
    vort : ndarray
        2-d numpy array of Quasi-geostrophic potential vorticity field; dimension = (nlat, nlon).
    ncforce: ndarray
        2-d numpy array of non-conservative force field (i.e. theta in NZ10(a) in equation (23a) and (23b));
        dimension = (nlat, nlon).
    area : ndarray
        2-d numpy array specifying differential areal element of each grid point; dimension = (nlat, nlon).
    dmu: sequence or array_like
        1-d numpy array of latitudinal differential length element (e.g. dmu = cos(lat) d(lat)). Size = nlat.
    nlat_s : int, default None
        The index of grid point that defines the extent of hemispheric domain from the pole. If input as None, it will be initialize as int(nlat/2).
    n_points : int, default None
        Analysis resolution to calculate equivalent latitude. If input as None, it will be initialized as *nlat_s*.
    planet_radius : float, default 6.378e+6
        radius of spherical planet of interest consistent with input 'area'.

    Returns
    -------
    qref : ndarray
        1-d numpy array of value Q(y) where latitude y is given by ylat; dimension = (nlat).
    lwa_result : ndarray
        2-d numpy array of local wave activity values; dimension = (nlat, nlon).
    bigsigma_result: ndarray
        2-d numpy array of non-conservative force contribution value; dimension = (nlat, nlon).

    """

    from hn2016_falwa import basis

    nlat = vort.shape[0]
    nlon = vort.shape[1]

    if nlat_s is None:
        nlat_s = int(nlat/2)

    if n_points is None:
        n_points = nlat_s

    qref = np.zeros(nlat)
    lwa_result = np.zeros((nlat, nlon))
    bigsigma_result = np.zeros((nlat, nlon))

    # --- Southern Hemisphere ---
    qref1, dummy = basis.eqvlat(ylat[:nlat_s], vort[:nlat_s, :], area[:nlat_s, :],
                                n_points, planet_radius=planet_radius)
    qref[:nlat_s] = qref1
    lwa_result[:nlat_s, :], bigsigma_result[:nlat_s, :] = basis.lwa(nlon, nlat_s,
                                                                    vort[:nlat_s, :],
                                                                    qref1, dmu[:nlat_s],
                                                                    ncforce=ncforce[:nlat_s, :])

    # --- Northern Hemisphere ---
    vort2 = -vort[::-1, :]  # Added the minus sign, but gotta see if NL_North is affected
    qref2, dummy = basis.eqvlat(ylat[:nlat_s], vort2[:nlat_s, :], area[:nlat_s, :],
                                n_points, planet_radius=planet_radius)
    qref[-nlat_s:] = -qref2[::-1]
    lwa_result[-nlat_s:, :], bigsigma_result[-nlat_s:, :] = basis.lwa(nlon, nlat_s,
                                                                      vort[-nlat_s:, :],
                                                                      qref[-nlat_s:],
                                                                      dmu[-nlat_s:],
                                                                      ncforce=ncforce[-nlat_s:, :])
    return qref, lwa_result, bigsigma_result


def qgpv_eqlat_lwa_options(ylat, vort, area, dmu, nlat_s=None,
                           n_points=None, vgrad=None, ncforce=None,
                           planet_radius=6.378e+6):

    """
    Compute equivalent latitutde *qref*, local wave activity *lwa_result* and
    non-conservative force on wave activity *bigsigma_result* based on Quasi-
    geostrophic potential vorticity field *vort* at a pressure level as
    outlined in Huang and Nakamura (2017).

    Parameters
    ----------
    ylat : sequence or array_like
        1-d numpy array of latitude (in degree) with equal spacing in ascending order; dimension = nlat.
    vort : ndarray
        2-d numpy array of Quasi-geostrophic potential vorticity field; dimension = (nlat, nlon).
    ncforce: ndarray
        2-d numpy array of non-conservative force field (i.e. theta in NZ10(a) in equation (23a) and (23b));
        dimension = (nlat, nlon).
    area : ndarray
        2-d numpy array specifying differential areal element of each grid point; dimension = (nlat, nlon).
    dmu: sequence or array_like
        1-d numpy array of latitudinal differential length element (e.g. dmu = cos(lat) d(lat)). Size = nlat.
    nlat_s : int, default None
        The index of grid point that defines the extent of hemispheric domain from the pole. If input as None, it will be initialize as int(nlat/2).
    n_points : int, default None
        Analysis resolution to calculate equivalent latitude. If input as None, it will be initialized as *nlat_s*.
    planet_radius : float, default 6.378e+6
        radius of spherical planet of interest consistent with input 'area'.

    Returns
    -------
    return_dict : dictionary
        A dictionary that consist of the 4 computed outputs listed below.
    (1) qref : ndarray
        1-d numpy array of value Q(y) where latitude y is given by ylat; dimension = (nlat).
    (2) brac_result: ndarray
        1-d numpy array of <...>_Q(y) in NZ10 where latitude y is given by ylat; dimension = (nlat).
    (3) lwa_result : ndarray
        2-d numpy array of local wave activity values; dimension = (nlat, nlon).
    (4) bigsigma_result: ndarray
        2-d numpy array of non-conservative force contribution value; dimension = (nlat, nlon).

    """

    from hn2016_falwa import basis

    nlat = vort.shape[0]
    nlon = vort.shape[1]

    if nlat_s is None:
        nlat_s = int(nlat/2)

    if n_points is None:
        n_points = nlat_s

    qref = np.zeros(nlat)
    lwa_result = np.zeros((nlat, nlon))
    if ncforce is not None:
        bigsigma_result = np.zeros((nlat, nlon))
    if vgrad is not None:
        brac_result = np.zeros(nlat)

    # --- Southern Hemisphere ---
    if vgrad is None:
        qref1, brac = basis.eqvlat(ylat[:nlat_s], vort[:nlat_s, :], area[:nlat_s, :],
                                   n_points, planet_radius=planet_radius)
    else:
        qref1, brac = basis.eqvlat(ylat[:nlat_s], vort[:nlat_s, :], area[:nlat_s, :],
                                   n_points, planet_radius=planet_radius,
                                   vgrad=vgrad[:nlat_s, :])

    qref[:nlat_s] = qref1
    if vgrad is not None:
        brac_result[:nlat_s] = brac

    if ncforce is not None:
        lwa_result[:nlat_s, :], bigsigma_result[:nlat_s, :] = basis.lwa(nlon, nlat_s,
                                                                    vort[:nlat_s, :],
                                                                    qref1, dmu[:nlat_s],
                                                                    ncforce=ncforce[:nlat_s, :])
    else:
        lwa_result[:nlat_s, :], dummy = basis.lwa(nlon, nlat_s, vort[:nlat_s, :], qref1, dmu[:nlat_s])

    # --- Northern Hemisphere ---
    vort2 = -vort[::-1, :]  # Added the minus sign, but gotta see if NL_North is affected

    if vgrad is None:
        qref2, brac = basis.eqvlat(ylat[:nlat_s], vort2[:nlat_s, :], area[:nlat_s, :],
                                    n_points, planet_radius=planet_radius)
    else:
        vgrad2 = -vgrad[::-1, :] # Is this correct?
        qref2, brac = basis.eqvlat(ylat[:nlat_s], vort2[:nlat_s, :], area[:nlat_s, :],
                                    n_points, planet_radius=planet_radius,
                                    vgrad=vgrad2[:nlat_s, :])

    qref[-nlat_s:] = -qref2[::-1]
    if vgrad is not None:
        brac_result[-nlat_s:] = -brac[::-1]

    if ncforce is not None:
        lwa_result[-nlat_s:, :], bigsigma_result[-nlat_s:, :] = basis.lwa(nlon, nlat_s,
                                                                      vort[-nlat_s:, :],
                                                                      qref[-nlat_s:],
                                                                      dmu[-nlat_s:],
                                                                      ncforce=ncforce[-nlat_s:, :])
    else:
        lwa_result[-nlat_s:, :], dummy = basis.lwa(nlon, nlat_s, vort[-nlat_s:, :], qref[-nlat_s:], dmu[-nlat_s:])

    # Return things as dictionary
    return_dict = dict()
    return_dict['qref'] = qref
    return_dict['lwa_result'] = lwa_result

    if vgrad is not None:
        return_dict['brac_result'] = brac_result
    if ncforce is not None:
        return_dict['bigsigma_result'] = bigsigma_result

    return return_dict


def qgpv_input_qref_to_compute_lwa(ylat, qref, vort, area, dmu, nlat_s=None,
                                   planet_radius=6.378e+6):
    """
    Compute equivalent latitutde *qref* and local wave activity *lwa_result* based
    on Quasi-geostrophic potential vorticity field *vort* at a pressure level as
    outlined in Huang and Nakamura (2017). This function computes lwa based on a
    prescribed *qref* instead of *qref* obtained from the QGPV field.

    Parameters
    ----------
    ylat : sequence or array_like
        1-d numpy array of latitude (in degree) with equal spacing in ascending order; dimension = nlat.
    qref : ndarray
        1-d numpy array of value Q(y) where latitude y is given by ylat; dimension = (nlat).
    vort : ndarray
        2-d numpy array of Quasi-geostrophic potential vorticity field; dimension = (nlat, nlon).
    area : ndarray
        2-d numpy array specifying differential areal element of each grid point; dimension = (nlat, nlon).
    dmu: sequence or array_like
        1-d numpy array of latitudinal differential length element (e.g. dmu = cos(lat) d(lat)). Size = nlat.
    nlat_s : int, default None
        The index of grid point that defines the extent of hemispheric domain from the pole. If input as None, it will be initialize as int(nlat/2).
    planet_radius : float, default 6.378e+6
        radius of spherical planet of interest consistent with input 'area'.

    Returns
    -------
    lwa_result : ndarray
        2-d numpy array of local wave activity values; dimension = (nlat, nlon).
    """
    from hn2016_falwa import basis

    nlat = vort.shape[0]
    nlon = vort.shape[1]
    if nlat_s is None:
        nlat_s = nlat/2

    lwa_result = np.zeros((nlat, nlon))

    # --- Southern Hemisphere ---
    lwa_result[:nlat_s, :], dummy = basis.lwa(nlon, nlat_s, vort[:nlat_s, :],
                                              qref[:nlat_s], dmu[:nlat_s])

    # --- Northern Hemisphere ---
    lwa_result[-nlat_s:, :], dummy = basis.lwa(nlon, nlat_s, vort[-nlat_s:, :],
                                               qref[-nlat_s:], dmu[-nlat_s:])

    return lwa_result



def theta_lwa(ylat,theta,area,dmu,nlat_s=None,n_points=None,planet_radius=6.378e+6):
    """
    Compute the surface wave activity *B* based on surface potential temperature.
    See Nakamura and Solomon (2010a) for details.

    Parameters
    ----------
    ylat : sequence or array_like
        1-d numpy array of latitude (in degree) with equal spacing in ascending order; dimension = nlat.
    theta : ndarray
        2-d numpy array of surface potential temperature field; dimension = (nlat, nlon).
    area : ndarray
        2-d numpy array specifying differential areal element of each grid point; dimension = (nlat, nlon).
    dmu: sequence or array_like
        1-d numpy array of latitudinal differential length element (e.g. dmu = cos(lat) d(lat)). Size = nlat.
    nlat_s : int, default None
        The index of grid point that defines the extent of hemispheric domain from the pole. If input as None, it will be initialize as int(nlat/2).
    planet_radius : float, default 6.378e+6
        radius of spherical planet of interest consistent with input 'area'.

    Returns
    -------
    qref : sequence or array_like
        1-d numpy array of value reference potential temperature *Theta(y)* approximated by box counting method, where latitude y is given by ylat; dimension = (nlat).
    lwa_result : ndarray
        2-d numpy array of local surface wave activity values; dimension = (nlat, nlon).

    """
    from hn2016_falwa import basis

    nlat = theta.shape[0]
    nlon = theta.shape[1]
    if nlat_s == None:
        nlat_s = nlat/2
    if n_points == None:
        n_points = nlat_s

    qref = np.zeros(nlat)
    lwa_result = np.zeros((nlat,nlon))

    # --- southern Hemisphere ---
    qref[:nlat_s], brac = basis.eqvlat(ylat[:nlat_s], theta[:nlat_s, :],
                                       area[:nlat_s, :], n_points,
                                       planet_radius=planet_radius)
    #qref1 = eqvlat(ylat[:nlat_s],theta[:nlat_s,:],area[:nlat_s,:],nlat_s,planet_radius=6.378e+6)
    # qref[:nlat_s] = qref1
    # lwa_south = lwa(nlon,nlat_s,theta[:nlat_s,:],qref1,dmu[:nlat_s])
    lwa_result[:nlat_s, :], dummy = basis.lwa(nlon, nlat_s, theta[:nlat_s, :],
                                              qref[:nlat_s], dmu[:nlat_s])
    # lwa_result[:nlat_s,:] = lwa_south

    # --- northern Hemisphere ---
    theta2 = theta[::-1,:] # Added the minus sign, but gotta see if NL_north is affected
    # qref2 = eqvlat(ylat[:nlat_s],theta2[:nlat_s,:],area[:nlat_s,:],nlat_s,planet_radius=6.378e+6)
    qref2, brac = basis.eqvlat(ylat[:nlat_s], theta2[:nlat_s, :], area[:nlat_s, :],
                               n_points, planet_radius=planet_radius)
    qref[-nlat_s:] = qref2[::-1]
    # lwa_north = lwa(nlon,nlat_s,theta2[:nlat_s,:],qref2,dmu[:nlat_s])
    lwa_result[-nlat_s:, :], dummy = basis.lwa(nlon, nlat_s, theta[-nlat_s:, :], qref[-nlat_s:], dmu[-nlat_s:])
    # lwa_result[-nlat_s:,:] = lwa_north[::-1,:]

    return qref, lwa_result
