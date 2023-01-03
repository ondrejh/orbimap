#!/usr/bin/python3

import numpy as np
from matplotlib.widgets import Slider
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import tkinter as tk
from tkinter.ttk import Button, Frame

TMAX = 3.0 #s

def update():
    print('Update')
    global phase
    phase += step
    if phase > 2 * np.pi:
        phase -= 2 * np.pi
    line1.set_ydata(np.sin(x + phase))
    line2.set_ydata(np.cos(x + phase))
    fg.canvas.draw()
    fg.canvas.flush_events()

# frames
root = tk.Tk()
fg_frame = Frame(root)
fg_frame.pack(fill="both", expand=True)
bot_frame = Frame(root)
bot_frame.pack(fill="x", expand=True)

# figure
fg = Figure()
phase = 0.0
step = 10*np.pi / 500
x = np.linspace(0, TMAX, 100)
y1 = np.sin(x)
y2 = np.cos(x + phase)
cnv = FigureCanvasTkAgg(fg, fg_frame)
cnv.get_tk_widget().pack(fill="both", expand=True)
axp = fg.add_subplot(111)
line1, line2, = axp.plot(x, y1, 'r-', x, y2, 'g-')

# controls
btn = tk.Button(bot_frame, text='Update', command=update)
btn.pack()

root.mainloop()
