from scipy.spatial import Delaunay
def mesh_from_function(f, u, v):
    i, j = u[0], v[0]
    points = []
    while i <= u[1]:
        j = v[0]
        while j <= v[1]:
            points.append([i, j])
            if j < v[1] and j + v[2] > v[1]:
                points.append([i, v[1]])
                break
            j += v[2]
        if i < u[1] and i + u[2] > u[1]:
            i = u[1]
        else:
            i += u[2]
    tris = Delaunay(points)
    xval = []
    yval = []
    zval = []
    for tri in tris.simplices:
        for indices in tri:
            x, y, z = f(points[indices][0], points[indices][1])
            xval.append(x)
            yval.append(y)
            zval.append(z)
    return xval, yval, zval
