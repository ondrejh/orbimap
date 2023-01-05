#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import tkinter as tk
from tkinter.ttk import Button, Frame, Entry, Label

import threading
import serial
from time import sleep
from math import sqrt

LEN = 250
TMAX = LEN * 0.02 #s
ALIM = [-12, 12]
RLIM = [-10, 10]

PORT = '/dev/ttyACM0'

class myFig(object):

    def __init__(self, fig, tmax=TMAX, ylim=ALIM, zlim=RLIM, dlen=LEN, after=None):
        self.fig = fig
        self.ax = self.fig.add_subplot(211)
        self.bx = self.fig.add_subplot(212)
        self.after = after

        self.dlen = dlen
        self.tmax = tmax
        self.ylim = ylim
        self.zlim = zlim
        self.grav = [0.0, 0.0, 0.0]
        self.rms = [0.0, 0.0, 0.0]

        # zero crossing
        self.th = 1.0
        self.ycz = False
        self.yczt = 0
        self.zcz = False
        self.zczt = 0
        self.yczn = False
        self.ycznt = 0
        self.zczn = False
        self.zcznt = 0

        self.x = np.linspace(0, self.tmax, self.dlen)
        self.y1 = [0] * self.dlen
        self.y2 = [0] * self.dlen
        self.y3 = [0] * self.dlen
        self.z1 = [0] * self.dlen
        self.z2 = [0] * self.dlen
        self.z3 = [0] * self.dlen
        self.ya1 = [0] * self.dlen
        self.ya2 = [0] * self.dlen
        self.ya3 = [0] * self.dlen

        self.ln1, self.ln2, self.ln3, = self.ax.plot(self.x, self.ya1, 'r-',
                self.x, self.ya2, 'g-',
                self.x, self.ya3, 'b-')
        self.ax.set_ylim(self.ylim)
        self.ax.set_xlim([0, self.tmax])
        self.ax.set_ylabel('Accel [m/s^2]')
        self.ax.legend(['Acc X', 'Acc Y', 'Acc Z'], loc='upper right')
        self.ax.grid()

        self.rln1, self.rln2, self.rln3, = self.bx.plot(self.x, self.z1, 'r-',
                self.x, self.z2, 'g-',
                self.x, self.z3, 'b-')
        self.bx.set_ylim(self.zlim)
        self.bx.set_xlim([0, self.tmax])
        self.bx.set_ylabel('Rot [rad/s]')
        self.bx.set_xlabel('Time [s]')
        self.bx.legend(['Rot X', 'Rot Y', 'Rot Z'], loc='upper right')
        self.bx.grid()

        self.newdata = False
        self.pause = False

    def reset(self, tmax=TMAX, ylim=ALIM, zlim=RLIM, dlen=LEN):
        self.ax.clear()
        self.bx.clear()

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
        self.ya1 = [0] * self.dlen
        self.ya2 = [0] * self.dlen
        self.ya3 = [0] * self.dlen

        self.ln1, self.ln2, self.ln3, = self.ax.plot(self.x, self.ya1, 'r-',
                self.x, self.ya2, 'g-',
                self.x, self.ya3, 'b-')
        self.ax.set_ylim(self.ylim)
        self.ax.set_xlim([0, self.tmax])
        self.ax.set_ylabel('Accel [m/s^2]')
        self.ax.legend(['Acc X', 'Acc Y', 'Acc Z'], loc='upper right')
        self.ax.grid()

        self.rln1, self.rln2, self.rln3, = self.bx.plot(self.x, self.z1, 'r-',
                self.x, self.z2, 'g-',
                self.x, self.z3, 'b-')
        self.bx.set_ylim(self.zlim)
        self.bx.set_xlim([0, self.tmax])
        self.bx.set_ylabel('Rot [rad/s]')
        self.bx.set_xlabel('Time [s]')
        self.bx.legend(['Rot X', 'Rot Y', 'Rot Z'], loc='upper right')
        self.bx.grid()

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def insert(self, data):
        if self.pause:
            return
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
        self.recalc()
        self.newdata = True

    def recalc(self):
        sy1 = sy2 = sy3 = 0.0
        for i in range(self.dlen):
            sy1 += self.y1[i]
            sy2 += self.y2[i]
            sy3 += self.y3[i]
        sy1 /= self.dlen
        sy2 /= self.dlen
        sy3 /= self.dlen
        self.ya1 = [(y - sy1) for y in self.y1]
        self.ya2 = [(y - sy2) for y in self.y2]
        self.ya3 = [(y - sy3) for y in self.y3]
        self.grav = [sy1, sy2, sy3]

        ry1 = ry2 = ry3 = 0.0
        for i in range(self.dlen):
            ry1 += self.ya1[i] * self.ya1[i] 
            ry2 += self.ya2[i] * self.ya2[i]
            ry3 += self.ya3[i] * self.ya3[i]
        ry1 = sqrt( ry1 / self.dlen )
        ry2 = sqrt( ry2 / self.dlen )
        ry3 = sqrt( ry3 / self.dlen )
        self.rms = [ry1, ry2, ry3]

        # step detection
        self.th = (ry1 + ry2 + ry3) / 3
        if self.th < 1.0:
            self.th = 1.0
        if self.ya2[0] > self.th:
            self.ycz = True
        elif self.ycz and (self.ya2[0] < -self.th):
            if self.yczt > self.zczt:
                dt = self.yczt - self.zczt
                dtt = self.yczt / 3
                if dt < dtt:
                    print('Backward')
                elif dt > 2 * dtt:
                    print('Forward')
            self.ycz = False
            self.yczt = 0
            print('Y zero crossing')
        if self.ya3[0] > self.th:
            self.zcz = True
        elif self.zcz and (self.ya3[0] < -self.th):
            self.zcz = False
            self.zczt = 0
            print('Z zero crossing')
        if self.ya2[0] < -self.th:
            self.yczn = True
        elif self.yczn and (self.ya2[0] > self.th):
            if self.ycznt > self.zcznt:
                dt = self.ycznt - self.zcznt
                dtt = self.ycznt / 3
                if dt < dtt:
                    print('Backward')
                elif dt > 2 * dtt:
                    print('Forward')
            self.yczn = False
            self.ycznt = 0
            print('Y zero crossing negative')
        if self.ya3[0] < -self.th:
            self.zczn = True
        elif self.zczn and (self.ya3[0] > self.th):
            self.zczn = False
            self.zcznt = 0
            print('Z zero crossing negative')
        self.yczt += 1
        self.zczt += 1
        self.ycznt += 1
        self.zcznt += 1

    def update(self):
        if self.newdata:
            self.ln1.set_ydata(self.ya1)
            self.ln2.set_ydata(self.ya2)
            self.ln3.set_ydata(self.ya3)
            self.rln1.set_ydata(self.z1)
            self.rln2.set_ydata(self.z2)
            self.rln3.set_ydata(self.z3)
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
            self.newdata = False
        if self.after is not None:
            self.after()
        root.after(20, self.update)


class GetGyro(threading.Thread):
    def __init__(self, port, update):
        threading.Thread.__init__(self)
        self.portname = port
        self.updatefcn = update
        self.stop = False
        self.connect = False
        self.connected = False
        self.replay = False
    def run(self):
        while not self.stop:
            if self.connect:
                with serial.Serial(self.portname, timeout=0) as p:
                    buf = ""
                    self.connected = True
                    #print('connected')
                    while self.connect and not self.stop:
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
                                    #if True:
                                        self.updatefcn(val)
                                    except:
                                        print('finito')
                                        self.stop = True
                                buf = ""
                    #print('disconnecting')
            elif self.replay:
                for i in range(Figma.dlen):
                    val = [Figma.y1[-1], Figma.y2[-1], Figma.y3[-1], Figma.z1[-1], Figma.z2[-1], Figma.z3[-1]]
                    self.updatefcn(val)
                    sleep(0.02)
                self.replay = False
            else:
                #print('disconected')
                self.connected = False
                while not self.connect and not self.stop and not self.replay:
                    sleep(0.1)
                #print('connecting')


def pause():
    Figma.pause = not Figma.pause
    btnP['text'] = 'Run' if Figma.pause else 'Pause'

def connect():
    gyroThr.portname = portVar.get()
    gyroThr.connect = not gyroThr.connect
    if gyroThr.connect:
        btnC['text'] = 'Disconnect'
        portEntry['state'] = 'disabled'
        btnP['state'] = 'disabled'
        if Figma.pause:
            pause()
    else:
        btnC['text'] = 'Connect'
        portEntry['state'] = 'normal'
        btnP['state'] = 'normal'

def save():
    if not Figma.pause:
        pause()
    f = tk.filedialog.asksaveasfile(title="Select file to save plot", filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
    if f is None:
        return
    f.write('len;{}\n\n'.format(Figma.dlen))
    for i in range(Figma.dlen):
        f.write('{};{};{};{};{};{};{}\n'.format(Figma.x[i],
            Figma.y1[i], Figma.y2[i], Figma.y3[i],
            Figma.z1[i], Figma.z2[i], Figma.z3[i]))
    f.close()

def load():
    if not Figma.pause:
        pause()
    f = tk.filedialog.askopenfile(title="Select file to load", filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
    if f is None:
        return
    i = 0
    for line in f.readlines():
        sp = line.strip().split(';')
        if len(sp) > 1 and sp[0] == 'len':
            dlen = int(sp[1])
            if Figma.dlen != dlen:
                Figma.reset(dlen=dlen)
        elif len(sp) == 7:
            Figma.x[i] = float(sp[0])
            Figma.y1[i] = float(sp[1])
            Figma.y2[i] = float(sp[2])
            Figma.y3[i] = float(sp[3])
            Figma.z1[i] = float(sp[4])
            Figma.z2[i] = float(sp[5])
            Figma.z3[i] = float(sp[6])
            i += 1
    Figma.recalc()
    Figma.newdata = True

def replay():
    if not gyroThr.connect and not gyroThr.connected:
        if Figma.pause:
            pause()
        gyroThr.replay = True

def reset():
    try:
        ar = float(accRangVar.get())
        rr = float(rolRangVar.get())
        dl = int(dlenVar.get())
    except TypeError:
        return

    Figma.reset(dlen=dl, ylim=[-ar, ar], zlim=[-rr, rr], tmax=0.02*dl)

def after():
    labGxVal['text'] = '{:0.1f}'.format(Figma.grav[0])
    labGyVal['text'] = '{:0.1f}'.format(Figma.grav[1])
    labGzVal['text'] = '{:0.1f}'.format(Figma.grav[2])
    labRxV['text'] = '{:0.1f}'.format(Figma.rms[0])
    labRyV['text'] = '{:0.1f}'.format(Figma.rms[1])
    labRzV['text'] = '{:0.1f}'.format(Figma.rms[2])
    labThV['text'] = '{:0.1f}'.format(Figma.th)
    labZcyV['text'] = str(Figma.yczt)
    labZczV['text'] = str(Figma.zczt)

# frames
root = tk.Tk()
root.title("MPU6050 gyro logger v0.1")
fgsid_frame = Frame(root)
fgsid_frame.pack(fill="both", expand=True)
fg_frame = Frame(fgsid_frame)
fg_frame.pack(side="left", fill="both", expand=True)
bot_frame = Frame(root)
bot_frame.pack(fill="x", expand=False)
sid_frame = Frame(fgsid_frame)
sid_frame.pack(side="left", fill="y", expand=False)

# figure
fg = Figure()
cnv = FigureCanvasTkAgg(fg, fg_frame)
cnv.get_tk_widget().pack(fill="both", expand=True)
Figma = myFig(fg, after=after)

# controls
btnC = Button(bot_frame, text='Connect', command=connect)
btnC.pack(side='left')
portVar = tk.StringVar()
portVar.set(PORT)
portEntry = Entry(bot_frame, textvariable=portVar, width=15, justify='center')
portEntry.pack(side='left')
btnP = Button(bot_frame, text='Pause', command=pause)
btnP.pack(side='left')

accRangVar = tk.StringVar()
accRangVar.set(ALIM[-1])
accRangEntry = Entry(bot_frame, textvariable=accRangVar, width=6, justify='center')
accRangEntry.pack(side='left')
rolRangVar = tk.StringVar()
rolRangVar.set(RLIM[-1])
rolRangEntry = Entry(bot_frame, textvariable=rolRangVar, width=6, justify='center')
rolRangEntry.pack(side='left')
dlenVar = tk.StringVar()
dlenVar.set(LEN)
dlenEntry = Entry(bot_frame, textvariable=dlenVar, width=6, justify='center')
dlenEntry.pack(side='left')

btnR = Button(bot_frame, text='Reset', command=reset)
btnR.pack(side='left')
btnS = Button(bot_frame, text='Save', command=save)
btnS.pack(side='left')
btnL = Button(bot_frame, text='Load', command=load)
btnL.pack(side='left')
btnRp = Button(bot_frame, text='Replay', command=replay)
btnRp.pack(side='left')

# gravity (avg)
labGx = Label(sid_frame, text='Avg X:')
labGx.grid(row=0, column=0)
labGy = Label(sid_frame, text='Avg Y:')
labGy.grid(row=1, column=0)
labGz = Label(sid_frame, text='Avg Z:')
labGz.grid(row=2, column=0)
labGxVal = Label(sid_frame, text='0.0', width=6, justify='center')
labGxVal.grid(row=0, column=1)
labGyVal = Label(sid_frame, text='0.0', width=6, justify='center')
labGyVal.grid(row=1, column=1)
labGzVal = Label(sid_frame, text='0.0', width=6, justify='center')
labGzVal.grid(row=2, column=1)
# rms
labRx = Label(sid_frame, text='Rms X:')
labRx.grid(row=3, column=0)
labRy = Label(sid_frame, text='Rms Y:')
labRy.grid(row=4, column=0)
labRz = Label(sid_frame, text='Rms Z:')
labRz.grid(row=5, column=0)
labRxV = Label(sid_frame, text='0.0', width=6, justify='center')
labRxV.grid(row=3, column=1)
labRyV = Label(sid_frame, text='0.0', width=6, justify='center')
labRyV.grid(row=4, column=1)
labRzV = Label(sid_frame, text='0.0', width=6, justify='center')
labRzV.grid(row=5, column=1)
# treshold
labTh = Label(sid_frame, text='Th:')
labTh.grid(row=6, column=0)
labThV = Label(sid_frame, text='1.0', width=6, justify='center')
labThV.grid(row=6, column=1)
labZcy = Label(sid_frame, text='Y tim:')
labZcy.grid(row=7, column=0)
labZcyV = Label(sid_frame, text='0', width=6, justify='center')
labZcyV.grid(row=7, column=1)
labZcz = Label(sid_frame, text='Z tim:')
labZcz.grid(row=8, column=0)
labZczV = Label(sid_frame, text='0', width=6, justify='center')
labZczV.grid(row=8, column=1)

gyroThr = GetGyro(PORT, Figma.insert)
gyroThr.start()

root.after(100, Figma.update)
root.mainloop()

gyroThr.stop = True
sleep(0.3)
