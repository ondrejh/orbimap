#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import tkinter as tk
from tkinter.ttk import Button, Frame

import threading
import serial
from time import sleep

LEN = 250
TMAX = LEN * 0.02 #s
ALIM = [-12, 12]
RLIM = [-10, 10]

PORT = 'COM9'

class myFig(object):

    def __init__(self, fig, tmax=TMAX, ylim=ALIM, zlim=RLIM, dlen=LEN):
        self.fig = fig
        self.ax = self.fig.add_subplot(211)
        self.bx = self.fig.add_subplot(212)

        self.phase = 0
        self.step = 0.1

        self.dlen = dlen
        self.tmax = tmax
        self.ylim = ylim
        self.zlim = zlim

        self.x = np.linspace(0, self.tmax, self.dlen)
        self.y1 = [0] * self.dlen
        self.y2 = [0] * self.dlen
        self.y3 = [0] * self.dlen
        self.z1 = [0] * self.dlen
        self.z2 = [0] * self.dlen
        self.z3 = [0] * self.dlen

        self.ln1, self.ln2, self.ln3, = self.ax.plot(self.x, self.y1, 'r-', self.x, self.y2, 'g-', self.x, self.y3, 'b-')
        self.ax.set_ylim(self.ylim)
        self.ax.set_xlim([0, self.tmax])
        self.ax.grid()

        self.rln1, self.rln2, self.rln3, = self.bx.plot(self.x, self.z1, 'r-', self.x, self.z2, 'g-', self.x, self.z3, 'b-')
        self.bx.set_ylim(self.zlim)
        self.bx.set_xlim([0, self.tmax])
        self.bx.grid()

        self.newdata = False

    def reset(self, tmax=TMAX, ylim=ALIM, zlim=RLIM, dlen=LEN):
        print('reset')
        self.ax.clear()

        self.dlen = dlen
        self.tmax = tmax
        self.ylim = ylim
        self.zlim = zlim

        self.x = np.linspace(0, self.tmax, self.dlen)
        self.y1 = [0] * self.dlen
        self.y2 = [0] * self.dlen
        self.y3 = [0] * self.dlen
        self.z1 = [0] * self.dlen
        self.z2 = [0] * self.dlen
        self.z3 = [0] * self.dlen

        self.ln1, self.ln2, self.ln3, = self.ax.plot(self.x, self.y1, 'r-', self.x, self.y2, 'g-', self.x, self.y3, 'b-')
        self.ax.set_ylim(self.ylim)
        self.ax.set_xlim([0, self.tmax])
        self.ax.grid()

        self.rln1, self.rln2, self.rln3, = self.bx.plot(self.x, self.z1, 'r-', self.x, self.z2, 'g-', self.x, self.z3, 'b-')
        self.bx.set_ylim(self.zlim)
        self.bx.set_xlim([0, self.tmax])
        self.bx.grid()

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def insert(self, data):
        for i in range(self.dlen -1):
            n = self.dlen - 1 - i
            self.y1[n] = self.y1[n - 1]
            self.y2[n] = self.y2[n - 1]
            self.y3[n] = self.y3[n - 1]
            self.z1[n] = self.z1[n - 1]
            self.z2[n] = self.z2[n - 1]
            self.z3[n] = self.z3[n - 1]
        self.y1[0] = data[0]
        self.y2[0] = data[1]
        self.y3[0] = data[2]
        self.z1[0] = data[3]
        self.z2[0] = data[4]
        self.z3[0] = data[5]
        self.newdata = True

    def update(self):
        if self.newdata:
            #print('update')
            self.ln1.set_ydata(self.y1)
            self.ln2.set_ydata(self.y2)
            self.ln3.set_ydata(self.y3)
            self.rln1.set_ydata(self.z1)
            self.rln2.set_ydata(self.z2)
            self.rln3.set_ydata(self.z3)
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
            self.newdata = False
        root.after(20, self.update)


class GetGyro(threading.Thread):
    def __init__(self, port, update):
        threading.Thread.__init__(self)
        self.portname = port
        self.updatefcn = update
        self.stop = False
    def run(self):
        with serial.Serial(self.portname, timeout=0) as p:
            buf = ""
            while not self.stop:
                cont = p.read()
                for b in cont:
                    if b != ord('\n'):
                        buf += chr(b)
                    else:
                        splt = buf.split(' ')
                        if len(splt) == 6:
                            val = [float(s) for s in splt]
                            #print(val)
                            try:
                                self.updatefcn(val)
                            except:
                                print('finito')
                                self.stop = True
                        buf = ""


# frames
root = tk.Tk()
fg_frame = Frame(root)
fg_frame.pack(fill="both", expand=True)
bot_frame = Frame(root)
bot_frame.pack(fill="x", expand=True)

# figure
fg = Figure()
cnv = FigureCanvasTkAgg(fg, fg_frame)
cnv.get_tk_widget().pack(fill="both", expand=True)
Figma = myFig(fg)

# controls
btnU = tk.Button(bot_frame, text='Update', command=Figma.update)
btnU.pack(side='left')
btnR = tk.Button(bot_frame, text='Reset', command=Figma.reset)
btnR.pack(side='left')

gyroThr = GetGyro(PORT, Figma.insert)
gyroThr.start()

root.after(100, Figma.update)
root.mainloop()

gyroThr.stop = True
sleep(0.3)
