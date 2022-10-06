import numpy as np
import pandas as pd
import math
from pygnuplot import gnuplot

# quick simple 2d graph
def draw2DgraphFromFile(g, file, type):
    df = pd.read_csv(file, index_col=0, sep=" ")
    g.plot_data(df, ' using 1:2 with lines lc "web-blue" ', terminal=type)

def draw2Dgraph(xa, ya, type, file) -> gnuplot.Gnuplot:
    g = gnuplot.Gnuplot(
        output=file,
        terminal=type,
    )
    df = pd.DataFrame({"x": xa, "y": ya})
    g.set("grid")
    g.plot_data(df, 'using 2:3 with lines lc "web-blue"', output=file, terminal=type)
    return g


# quick simple 3d graph
def draw3Dgraph(g, xa, ya, za, type, file) -> gnuplot.Gnuplot:
    g.set("grid")
    df = pd.DataFrame({"x": xa, "y": ya, "z": za})
    g.splot_data(
        df,
        'using 2:3:4 with lines lc "web-blue"',
        output=file,
        terminal=type,
        parametric="",
    )
    return g


def add2Darrow(g, arrow, scale):
    buf = "arrow from %f, %f rto %f, %f" % (
        arrow[0][0],
        arrow[0][1],
        arrow[1][0] * scale,
        arrow[1][1] * scale,
    )
    g.set(buf)
    pass


def add3Darrow(g, arrow, scale):
    buf = "arrow from %f, %f, %f rto %f, %f, %f" % (
        arrow[0][0],
        arrow[0][1],
        arrow[0][2],
        arrow[1][0] * scale,
        arrow[1][1] * scale,
        arrow[1][2] * scale,
    )
    g.set(buf)
    pass


def test_draw():
    ## usage example.

    ##
    # generate graph data.
    ##
    i = 0
    data = np.zeros((50, 3))
    for t in np.arange(0, 5.0, 0.1):
        data[i][0] = math.cos(t)
        data[i][1] = math.sin(t)
        data[i][2] = t
        i += 1
    x = math.cos(math.pi / 2)
    y = math.sin(math.pi / 2)
    z = math.pi / 2
    tangent = np.array([[x, y, z], [-0.707107, 0, 0.707107]])
    normal = np.array([[x, y, z], [0, -1, 0]])
    binormal = np.array([[x, y, z], [0.707107, 0, 0.707107]])

    ##
    # plot data with gnuplot
    ##
    g = gnuplot.Gnuplot()
    draw2DgraphFromFile(g, "data.csv", "qt")
    g = gnuplot.Gnuplot()
    add3Darrow(g, tangent, 0.3)
    add3Darrow(g, normal, 0.3)
    add3Darrow(g, binormal, 0.3)
    g = draw3Dgraph(g, data[:, 0], data[:, 1], data[:, 2], "qt", "")
    input()
    ##

if __name__ == "__main__":
    test_draw()
