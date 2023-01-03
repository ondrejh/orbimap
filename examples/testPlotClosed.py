#!/usr/bin/python3

""" 
Interactive plot example by:
    https://stackoverflow.com/questions/4098131/how-to-update-a-plot-in-matplotlib

Test figure closed by:
    https://stackoverflow.com/questions/7557098/matplotlib-interactive-mode-determine-if-figure-window-is-still-displayed
"""

import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 6*np.pi, 100)
y = np.sin(x)

# You probably won't need this if you're embedding things in a tkinter plot...
plt.ion()

fig = plt.figure()
ax = fig.add_subplot(111)
line1, = ax.plot(x, y, 'r-') # Returns a tuple of line objects, thus the comma

phase = 0
step = 10 * np.pi / 500

while True:

    phase += step
    if phase > 2*np.pi:
        phase -= 2*np.pi

    print(phase)

    if plt.fignum_exists(fig.number):
        line1.set_ydata(np.sin(x + phase))
        fig.canvas.draw()
        fig.canvas.flush_events()
    else:
        print('Plot closed!')
        break
