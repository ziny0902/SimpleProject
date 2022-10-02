from sympy import *
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook

import numpy as np
import pandas as pd
fname = cbook.get_sample_data('/home/ziny/mnt/share-data/OpenSourceProject/C++/SimpleProject/Calculus/build/data.csv', asfileobj=False)
with cbook.get_sample_data('/home/ziny/mnt/share-data/OpenSourceProject/C++/SimpleProject/Calculus/build/data.csv') as file:
    array = np.loadtxt(file)
fig, ax = plt.subplots()

# original data.
org=np.zeros( (40, 2))
x = Symbol('x')
f=integrate(exp(-x**2/2))

i=0;
for t in np.arange(0.0, 4.0, 0.1):
    org[i][0] = t
    org[i][1] = f.subs(x, t).evalf()
    i += 1
ax.plot(array[:, 0], array[:, 1])
ax.plot(org[:, 0], org[:, 1])
plt.show()
