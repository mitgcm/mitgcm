from __future__ import print_function
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri as tri

def contourf(*arguments, **kwargs):
    """
    Create a contourf plot of a 2-D llc array (with tricontour).

    Call signatures::

        contourf(X, Y, C, N, **kwargs)

        contourf(X, Y, C, V, **kwargs)

    Parameters
    ----------
    X : array-like
        x coordinates of the grid points

    Y : array-like
        y coordinates of the grid points

    C : array-like
        array of color values.

    N : int
        number of levels

    V : list of float
        list of levels

    kwargs
        passed to tricontour.

    """

    arglen = len(arguments)
    h = []
    if arglen >= 3:
        data = np.copy(arguments[2].flatten())
        x = arguments[0].flatten()
        y = arguments[1].flatten()

        # Create the Triangulation;
        # no triangles so Delaunay triangulation created.
        triang = tri.Triangulation(x, y)
        ntri = triang.triangles.shape[0]

        # Mask off unwanted triangles.
        mask = np.where(data[triang.triangles].prod(axis=1)==0., 1, 0)
        triang.set_mask(mask)

        if arglen == 3:
            h = plt.tricontourf(triang, data, **kwargs)
        elif arglen == 4:
            h = plt.tricontourf(triang, data, arguments[3], **kwargs)
        else:
            print("wrong number of arguments")
            print("need at least 3 or 4 arguments")
            sys.exit(__doc__)

        # show the triangles for debugging
        #plt.triplot(triang, color='0.7')

    else:
        print("wrong number of arguments")
        print("need at least x,y,fld")
        sys.exit(__doc__)

    return h

def contour(*arguments, **kwargs):
    """
    Create a contour plot of a 2-D llc array (with tricontour).

    Call signatures::

        contour(X, Y, C, N, **kwargs)

        contour(X, Y, C, V, **kwargs)

    Parameters
    ----------
    X : array-like
        x coordinates of the grid points

    Y : array-like
        y coordinates of the grid points

    C : array-like
        array of color values.

    N : int
        number of levels

    V : list of float
        list of levels

    kwargs
        passed to tricontour.

    """

    arglen = len(arguments)
    h = []
    if arglen >= 3:
        data = arguments[2].flatten()
        x = arguments[0].flatten()
        y = arguments[1].flatten()

        # Create the Triangulation;
        # no triangles so Delaunay triangulation created.
        triang = tri.Triangulation(x, y)
        ntri = triang.triangles.shape[0]

        # Mask off unwanted triangles.
        mask = np.where(data[triang.triangles].prod(axis=1)==0., 1, 0)
        triang.set_mask(mask)

        if arglen == 3:
            h = plt.tricontour(triang, data, **kwargs)
        elif arglen == 4:
            h = plt.tricontour(triang, data, arguments[3], **kwargs)
        else:
            print("wrong number of arguments")
            print("need at least 3 or 4 arguments")
            sys.exit(__doc__)

        # show the triangles for debugging
        #plt.triplot(triang, color='0.7')

    else:
        print("wrong number of arguments")
        print("need at least x,y,fld")
        sys.exit(__doc__)

    return h

def flat(fld, **kwargs):
    """convert mds data into global 2D field
    only fields with 2 to 5 dimensions are allowed"""

    ndims = len(fld.shape)
    if ndims == 2:
        gfld = _flat2D(fld, **kwargs)
    elif ndims == 3:
        gfld = [ _flat2D(fld[a,:,:], **kwargs)
                 for a in range(fld.shape[0]) ]
    elif ndims == 4:
        gfld = [ [ _flat2D(fld[a,b,:,:], **kwargs)
                   for b in range(fld.shape[1]) ]
                 for a in range(fld.shape[0]) ]
    elif ndims == 5:
        gfld = [ [ [ _flat2D(fld[a,b,c,:,:], **kwargs)
                     for c in range(fld.shape[2]) ]
                   for b in range(fld.shape[1]) ]
                 for a in range(fld.shape[0]) ]
    else:
        print("wrong number of dimensions")
        print("only 2 to 5 dimensions are allowed")
        sys.exit(__doc__)

    gfld = np.array(gfld)

    return gfld

def _flat2D(fld, center='Atlantic'):
    """convert mds 2D data into global 2D field"""

    nx = fld.shape[1]
    ny = fld.shape[0]
    n = ny//nx//4

    # eastern and western hemispheres
    eastern=np.concatenate((fld[:n*nx,:],fld[n*nx:2*(n*nx)]),axis=1)
    tmp    = fld[2*(n*nx)+nx:,        ::-1]
    western=np.concatenate((tmp[2::n,:].transpose(),
                            tmp[1::n,:].transpose(),
                            tmp[0::n,:].transpose()))
    # Arctic face is special
    arctic  = fld[2*(n*nx):2*(n*nx)+nx,:]
    arctice = np.concatenate((np.triu(arctic[::-1,:nx//2].transpose()),
                              np.zeros((nx//2,nx))),axis=1)
    # arcticw = np.concatenate((arctic[:,nx:nx//2-1:-1].transpose(),
    #                           np.zeros((nx//2,nx//2)),
    #                           arctic[nx:nx//2-1:-1,nx//2-1::-1]),axis=1)
    mskr = np.tri(nx//2)[::-1,:]
    arcticw = np.concatenate((arctic[0:nx//2,nx:nx//2-1:-1].transpose(),
                              arctic[nx//2:nx,nx:nx//2-1:-1].transpose()*mskr,
                              np.triu(arctic[nx:nx//2-1:-1,nx:nx//2-1:-1]),
                              arctic[nx:nx//2-1:-1,nx//2-1::-1]*mskr),axis=1)
    #
    if center == 'Pacific':
        gfld = np.concatenate( ( np.concatenate((eastern,arctice)),
                                 np.concatenate((western,arcticw)) ), axis=1)
    else:
        gfld = np.concatenate( ( np.concatenate((western,arcticw)),
                                 np.concatenate((eastern,arctice)) ), axis=1)

    return gfld

def _mds2D(fld,center='Atlantic'):
    """convert global 2D 'flat field' to mds 2D data"""

    ni = fld.shape[-1]
    nj = fld.shape[-2]
    nx = ni//4
    ny = nx*(3*4+1)
    n = ny//nx//4

    # arctic face
    arcticw = fld[n*nx:,:nx]
    arctice = fld[n*nx:,2*nx:3*nx]
    arctic = np.concatenate((arctice,arcticw[::-1,::-1]),axis=0)

    # eastern and western hemispheres
    eastern=fld[:n*nx,2*nx:]
    # this is tricky
    western=fld[:n*nx,:2*nx]

    mdsfld = np.concatenate((eastern[:,:nx],
                             eastern[:,nx:],
                             arctic[:,::-1].transpose(),
                             western[::-1,:].transpose().reshape((2*n*nx,nx))),
                             axis=0)
    return mdsfld

def mds(fld,center='Atlantic'):
    """convert global 'flat' field into mds data;
    only fields with 2 to 5 dimensions are allowed"""

    ndims = len(fld.shape)
    if ndims == 2:
        mdsfld = _mds2D(fld, **kwargs)
    elif ndims == 3:
        mdsfld = [ _mds2D(fld[a,:,:], **kwargs)
                 for a in range(fld.shape[0]) ]
    elif ndims == 4:
        mdsfld = [ [ _mds2D(fld[a,b,:,:], **kwargs)
                   for b in range(fld.shape[1]) ]
                 for a in range(fld.shape[0]) ]
    elif ndims == 5:
        mdsfld = [ [ [ _mds2D(fld[a,b,c,:,:], **kwargs)
                     for c in range(fld.shape[2]) ]
                   for b in range(fld.shape[1]) ]
                 for a in range(fld.shape[0]) ]
    else:
        print("wrong number of dimensions")
        print("only 2 to 5 dimensions are allowed")
        sys.exit(__doc__)

    mdsfld = np.array(mdsfld)

    return mdsfld

def faces(fld):
    """convert mds multidimensional data into a list with 6 faces"""

    ndim = len(fld.shape)
    if ndim == 2:
        f = _faces2D(fld)
    else:
        # use list for dynamical memory allocation, because it is fast
        if ndim == 3:
            ff = []
            nk = fld.shape[0]
            for k in range(nk):
                fld2D = fld[k,:,:]
                f2D = _faces2D(fld2D)
                ff.append(f2D)
        elif ndim == 4:
            ff = []
            nk = fld.shape[1]
            nl = fld.shape[0]
            for l in range(nl):
                for k in range(nk):
                    fld2D = fld[l,k,:,:]
                    f2D = _faces2D(fld2D)
                    ff.append(f2D)
        elif ndim == 5:
            ff = []
            nk = fld.shape[2]
            nl = fld.shape[1]
            nm = fld.shape[0]
            for m in range(nm):
                for l in range(nl):
                    for k in range(nk):
                        fld2D = fld[m,l,k,:,:]
                        f2D = _faces2D(fld2D)
                        ff.append(f2D)
        # permute list indices so that face index is the first
        ff = np.transpose(ff)
        f  = []
        for listIndex in range(len(ff)):
            # for each face turn list into array, glue together and reshape
            nx = ff[listIndex][0].shape[-1]
            ny = ff[listIndex][0].shape[-2]
            if   ndim == 3: rshp =       (nk,ny,nx)
            elif ndim == 4: rshp =    (nl,nk,ny,nx)
            elif ndim == 5: rshp = (nm,nl,nk,ny,nx)
            f.append(np.concatenate(np.array(ff[listIndex])).reshape(rshp))

    return f

def faces2mds(ff):
    """convert 6 faces to mds 2D data,
    inverse opertation of llc.faces"""

    ndims = len(ff[0].shape)
    shp = list(ff[0].shape)
    shp[-2]=2*ff[0].shape[-2]
    wd = np.concatenate( (ff[3],ff[4]),axis=-2 ).reshape(shp)
    f  = np.concatenate( (ff[0],ff[1],ff[2],wd),axis=-2)

    return f

def _faces2D(fld):
    """convert mds 2D data into a list with 6 faces"""

    nx = fld.shape[-1]
    ny = fld.shape[-2]
    n = ny//nx//4

    # divide into faces
    f = []
    f.append(fld[:n*nx,:])
    f.append(fld[n*nx:2*(n*nx),:])
    # arctic face
    f.append(fld[2*(n*nx):2*(n*nx)+nx,:])
    # western hemisphere
    wd = fld[2*(n*nx)+nx:,:].reshape(2*nx,n*nx)
    f.append(wd[:nx,:])
    f.append(wd[nx:,:])
    # pseudo-sixth face
    f.append(np.zeros((nx,nx)))

    return f


def _sqCoord(a):
    b = np.squeeze(a)
    return b

def _sqData(a):
    b = np.copy(np.squeeze(a))
    b = np.ma.masked_where(b==0., b)
    b = np.ma.masked_where(np.isnan(b), b)
    return b

def pcol(*arguments, **kwargs):
    """
    Create a pseudo-color plot of a 2-D llc array (with plt.pcolormesh).

    Call signatures::

        pcol(X, Y, C, **kwargs)

        pcol(X, Y, C, m, **kwargs)

    Parameters
    ----------
    X : array-like
        x coordinates of the grid point corners (G-points)

    Y : array-like
        y coordinates of the grid point corners (G-points)

    C : array-like
        array of color values.

    m : Basemap instance, optional
        map projection to use.
        NOTE: currently not all projections work

    kwargs
        passed to plt.pcolormesh.

    """

    arglen = len(arguments)
    h = []
    mapit = False
    if arglen < 3:
        print("wrong number of arguments")
        print("need at least x,y,fld")
        sys.exit(__doc__)
    elif arglen > 3:
        mapit = True
        m = arguments[3]

    if mapit:
        # not all projections work, catch few of these here
        if ( (m.projection == 'hammer') |
             (m.projection == 'robin')  |
             (m.projection == 'moll')   |
             (m.projection == 'cea') ):
            sys.exit("selected projection '"+m.projection
                     +"' is not supported")

        # these projections use simple code for the Arctic face;
        # all others require more complicted methods
        stereographicProjection = (m.projection == 'npaeqd')  | \
                                  (m.projection == 'spaeqd')  | \
                                  (m.projection == 'nplaea')  | \
                                  (m.projection == 'splaea')  | \
                                  (m.projection == 'npstere') | \
                                  (m.projection == 'spstere') | \
                                  (m.projection == 'stere')
    else:
        stereographicProjection = False


    xg = arguments[0]
    yg = arguments[1]
    data = arguments[2]

    nx = data.shape[-1]
    ny = data.shape[-2]
    n = ny//nx//4

    # color range
    cax = [data.min(),data.max()]
    # overwrite if necessary
    if 'vmin' in kwargs: cax[0] = kwargs.pop('vmin','')
    if 'vmax' in kwargs: cax[1] = kwargs.pop('vmax','')
    # divide into faces
    f0 = []
    f0.append(faces(xg))
    f0.append(faces(yg))
    f0.append(faces(data))
    # fill holes in coordinate arrays
#    for t in [0,1,3,4]:
#        inan = f0[2][t]==0 # _sqCoord(f0[2][t])==np.NaN]
#        f0[0][t][inan]=np.NaN
#        f0[1][t][inan]=np.NaN

#    for t in [0,1]:
#        for i in range(nx):
#            for j in range(n*nx):
#                if f0[0][t][j,i]==0:f0[0][t][100,i]
#                if f0[1][t][j,i]==0:f0[1][t][100,i]
#
#    for t in [3,4]:
#        for i in range(n*nx):
#            for j in range(nx):
#                if f0[0][t][j,i]==0:f0[0][t][j,239]
#                if f0[1][t][j,i]==0:f0[1][t][j,239]

    # find the missing corners by interpolation
    fo = []
    fo.append( (f0[0][0][-1,0]+f0[0][2][-1,0]+f0[0][4][-1,0])/3. )
    fo.append( (f0[1][2][-1,0]+f0[1][2][-1,0]+f0[1][4][-1,0])/3. )
    fo.append( np.NaN )
    fe = []
    fe.append( (f0[0][1][0,-1]+f0[0][3][0,-1])/2. )
    fe.append( (f0[1][1][0,-1]+f0[1][3][0,-1])/2. )
    fe.append( np.NaN )
    f  = np.copy(f0)
    # fill some gaps at the face boundaries
    for t in [0,2,4]:
        tp = 2*(t//2)
        tpp = tp
        if tp==4: tpp = tp-6
        for k in [0,1,2]:
            tp = min(tp,3)
            f[k][t] = np.concatenate((f0[k][t],f0[k][1+tp][:,:1]),axis=1)
            if k==2: tmp = np.atleast_2d(np.append(f0[k][2+tpp][::-1,:1],fo[k]))
            else:    tmp = np.atleast_2d(np.append(fo[k],f0[k][2+tpp][::-1,:1]))
            f[k][t] = np.concatenate((f[k][t],tmp),axis=0)

    for t in [1,3]:
        tp = 2*(t//2)
        for k in [0,1,2]:
            f[k][t] = np.concatenate((f0[k][t],f0[k][2+tp][:1,:]),axis=0)
            if k==2: tmp = np.atleast_2d(np.append(f0[k][3+tp][:1,::-1],fe[k]))
            else:    tmp = np.atleast_2d(np.append(fe[k],f0[k][3+tp][:1,::-1]))
            f[k][t] = np.concatenate((f[k][t],tmp.transpose()),axis=1)

    # we do not really have a sixth face so we overwrite the southernmost row
    # of face 4 and 5 by a hack:
    for t in [3,4]:
        f[0][t][:,-1] = f[0][t][:,-2]
        f[1][t][:,-1] = -90. # degree = south pole

    # make sure that only longitudes of one sign are on individual lateral faces
    i0 = f[0][3]<0.
    f[0][3][i0] = f[0][3][i0]+360.
    # plot the lateral faces
    ph = []
    for t in [0,1,3,4]:
        if mapit: x, y = m(_sqCoord(f[0][t]), _sqCoord(f[1][t]))
        else:     x, y =   _sqCoord(f[0][t]), _sqCoord(f[1][t])
        ph.append(plt.pcolormesh(x,y,_sqData(f[2][t]), **kwargs))
    # plot more lateral faces to be able to select the longitude range later
    for t in [1,3,4]:
        f[0][t] = f[0][t]+ (-1)**t*360.
        if mapit: x, y = m(_sqCoord(f[0][t]), _sqCoord(f[1][t]))
        else:     x, y =   _sqCoord(f[0][t]), _sqCoord(f[1][t])
        ph.append(plt.pcolormesh(x,y,_sqData(f[2][t]), **kwargs))

    # Arctic face is special, because of the rotation of the grid by
    # rangle = 7deg (seems to be the default)
    t = 2

    if mapit & stereographicProjection:
        x, y = m(_sqCoord(f[0][t]),_sqCoord(f[1][t]))
        ph.append(plt.pcolormesh(x,y,_sqData(f[2][t]), **kwargs))
    else:
        rangle = 7.
        # first half of Arctic tile
        nn = nx//2+1
        xx = np.copy(f[0][t][:nn,:])
        yy = np.copy(f[1][t][:nn,:])
        zz = np.copy(f[2][t][:nn,:])
        xx = np.where(xx<rangle,xx+360,xx)
        if mapit: x, y = m(_sqCoord(xx),_sqCoord(yy))
        else:     x, y =   _sqCoord(xx),_sqCoord(yy)
        ph.append(plt.pcolormesh(x,y,_sqData(zz), **kwargs))
        # repeat for xx-360
        xx = xx-360.
        if mapit: x, y = m(_sqCoord(xx),_sqCoord(yy))
        else:     x, y =   _sqCoord(xx),_sqCoord(yy)
        ph.append(plt.pcolormesh(x,y,_sqData(zz), **kwargs))
        # second half of Arctic tile
        nn = nx//2
        xx = np.copy(f[0][t][nn:,:])
        yy = np.copy(f[1][t][nn:,:])
        zz = np.copy(f[2][t][nn:,:])
        #
        if mapit: x, y = m(_sqCoord(xx),_sqCoord(yy))
        else:     x, y =   _sqCoord(xx),_sqCoord(yy)
        ph.append(plt.pcolormesh(x,y,_sqData(zz), **kwargs))
        # repeat for xx+360
        xx = xx + 360.
        if mapit: x, y = m(_sqCoord(xx),_sqCoord(yy))
        else:     x, y =   _sqCoord(xx),_sqCoord(yy)
        ph.append(plt.pcolormesh(x,y,_sqData(zz), **kwargs))

    if not mapit:
        plt.xlim([-170,190])
        plt.ylim([-90,90])

    for im in ph:
        im.set_clim(cax[0],cax[1])

    return ph

def _getDims(u,v):
    lenu = len(np.shape(u))
    nt = 1
    nk = 1
    if lenu == 2:
        nju, niu = np.shape(u)
        njv, niv = np.shape(v)
    elif lenu == 3:
        nk, nju, niu = np.shape(u)
        nk, njv, niv = np.shape(v)
    elif lenu == 4:
        nt, nk, nju, niu = np.shape(u)
        nt, nk, njv, niv = np.shape(v)
    else:
        raise ValueError('Can only handle 2 to 4 dimensions')

    if nju!=13*niu:
        raise ValueError('nju=%i not equal 13*niu, niu=%i\n'%(nju,niu) +
                         'This is not and NOT an llc grid.')

    return nt, nk, nju, niu, njv, niv

def div(*arguments):
    """
    Compute divergence of vector field on llc grid

    Call signatures::

       divergence = div(U,V,HFW,HFS,DXG,DYG,RAC)
       divergence = div(U,V)
       divergence = div(U,V,DXG,DYG)
       divergence = div(U,V,DXG,DYG,RAC)

    Parameters
    ----------
    U   : array-like (timelevel,depthlevel,jpoint,jpoint)
          x-component of vector field at u-point

    V   : array-like
          y-component of vector field at v-point

    HFW : array-like (depthlevel,jpoint,jpoint)
          hFac at u-point

    HFS : array-like (jpoint,jpoint)
          hFac at v-point

    DXG : array-like (jpoint,jpoint)
          grid spacing in x across v-point

    DYG : array-like (depthlevel,jpoint,jpoint)
          grid spacing in y across u-point

    RAC : array-like (jpoint,jpoint)
          grid cell area

    """

    arglen = len(arguments)
    if arglen > 7:
        raise ValueError('too many arguments, maximum of 7 allowed')
    elif arglen == 7:
        u,v,hfw,hfs,dxg,dyg,rac = arguments[:]
        nt, nk, nju, niu, njv, niv =  _getDims(u,v)
    elif arglen == 2:
        u,v = arguments[:]
        nt, nk, nju, niu, njv, niv =  _getDims(u,v)
        hfw = np.ones((nk,nju,niu))
        hfs = np.ones((nk,njv,niv))
        dxg = np.ones((nju,niu))
        dyg = np.ones((njv,niv))
        rac = dxg*dyg
    elif arglen == 4:
        u,v,dxg,dyg = arguments[:]
        nt, nk, nju, niu, njv, niv =  _getDims(u,v)
        hfw = np.ones((nk,nju,niu))
        hfs = np.ones((nk,njv,niv))
        rac = dxg*dyg
    elif arglen == 5:
        u,v,dxg,dyg,rac = arguments[:]
        nt, nk, nju, niu, njv, niv =  _getDims(u,v)
        hfw = np.ones((nk,nju,niu))
        hfs = np.ones((nk,njv,niv))
    elif arglen == 6:
        u,v,hfw,hfs,dxg,dyg = arguments[:]
        nt, nk, nju, niu, njv, niv =  _getDims(u,v)
        rac = dxg*dyg
    else:
        raise ValueError('wrong number of arguments')

    u   = u.reshape(nt,nk,nju,niu)
    v   = v.reshape(nt,nk,njv,niv)
    hfw = hfw.reshape(nk,nju,niu)
    hfs = hfs.reshape(nk,njv,niv)

    dxgf = faces(dxg)
    dygf = faces(dyg)
    racf = faces(rac)

    divergence = np.zeros(u.shape)
    for t in range(0,nt):
        for k in range(0,nk):
            uf   = faces(u[t,k,:,:])
            vf   = faces(v[t,k,:,:])
            hfwf = faces(hfw[k,:,:])
            hfsf = faces(hfs[k,:,:])
            uflx = faces(np.zeros((nju,niv)))
            vflx = faces(np.zeros((nju,niv)))
            for iface in range(len(uf)-1):
                uflx[iface] = uf[iface]*dygf[iface]*hfwf[iface]
                vflx[iface] = vf[iface]*dxgf[iface]*hfsf[iface]

            divf = faces(np.zeros((nju,niu)))
            for iface in range(len(uf)-1):
                du   = np.roll(uflx[iface],-1,axis=-1)-uflx[iface]
                dv   = np.roll(vflx[iface],-1,axis=-2)-vflx[iface]
                # now take care of the connectivity
                if iface==0:
                    du[:,-1] = uflx[1][:,   0] - uflx[iface][:,-1]
                    dv[-1,:] = uflx[2][::-1,0] - vflx[iface][-1,:]
                if iface==1:
                    du[:,-1] = vflx[3][0,::-1] - uflx[iface][:,-1]
                    dv[-1,:] = vflx[2][0,:]    - vflx[iface][-1,:]
                if iface==2:
                    du[:,-1] = uflx[3][:,   0] - uflx[iface][:,-1]
                    dv[-1,:] = uflx[4][::-1,0] - vflx[iface][-1,:]
                if iface==3:
                    du[:,-1] = 0. # hack
                    dv[-1,:] = vflx[4][0,:]    - vflx[iface][-1,:]
                if iface==4:
                    du[:,-1] = 0. # hack
                    dv[-1,:] = uflx[0][::-1,0] - vflx[iface][-1,:]
                # putting it all together
                divf[iface] = (du + dv)/racf[iface]

            divergence[t,k,:,:] = faces2mds(divf)

    return np.squeeze(divergence)


def uv2c(*arguments):
    """
    Average vector component (u,v) to center points on llc grid

    Call signatures::

       uc,vc = uv2c(U,V)

    Parameters
    ----------
    U   : array-like (timelevel,depthlevel,jpoint,jpoint)
          x-component of vector field at u-point

    V   : array-like
          y-component of vector field at v-point

    """

    arglen = len(arguments)
    if arglen == 2:
        u,v = arguments[:]
        nt, nk, nju, niu, njv, niv =  _getDims(u,v)
    else:
        raise ValueError('wrong number of arguments, only 2 allowed')

    u   = u.reshape(nt,nk,nju,niu)
    v   = v.reshape(nt,nk,njv,niv)

    uc = np.zeros(u.shape)
    vc = np.zeros(v.shape)
    for t in range(0,nt):
        for k in range(0,nk):
            uf  = faces(u[t,k,:,:])
            vf  = faces(v[t,k,:,:])
            ucf = faces(np.zeros((nju,niu)))
            vcf = faces(np.zeros((njv,niv)))
            for iface in range(len(uf)-1):
                uk = np.roll(uf[iface],-1,axis=-1)+uf[iface]
                vk = np.roll(vf[iface],-1,axis=-2)+vf[iface]
                # now take care of the connectivity
                if iface==0:
                    uk[:,-1] = uf[1][:,   0] + uf[iface][:,-1]
                    vk[-1,:] = uf[2][::-1,0] + vf[iface][-1,:]
                if iface==1:
                    uk[:,-1] = vf[3][0,::-1] + uf[iface][:,-1]
                    vk[-1,:] = vf[2][0,:]    + vf[iface][-1,:]
                if iface==2:
                    uk[:,-1] = uf[3][:,   0] + uf[iface][:,-1]
                    vk[-1,:] = uf[4][::-1,0] + vf[iface][-1,:]
                if iface==3:
                    uk[:,-1] = 0. # hack
                    vk[-1,:] = vf[4][0,:]    + vf[iface][-1,:]
                if iface==4:
                    uk[:,-1] = 0. # hack
                    vk[-1,:] = uf[0][::-1,0] + vf[iface][-1,:]
                # putting it all together
                ucf[iface] = 0.5*uk
                vcf[iface] = 0.5*vk

            uc[t,k,:,:] = faces2mds(ucf)
            vc[t,k,:,:] = faces2mds(vcf)

    return np.squeeze(uc), np.squeeze(vc)
