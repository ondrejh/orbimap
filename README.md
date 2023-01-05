MPU6050 based gyroscope logger
==============================

The device should track gyroscope connected to orbitrack spinner and evaulate if its moving
forward or backward. According to the dirrection is should generate keyUp and keyDown events,
so the orbitrack spinner can be used as an input device for the panoramatic map walkthrough.

## Hardware

USB gyroscope device consist of Arduino BadUsb and MPU6050 breakout board.

## Firmware

Arduino sketch reading MPU6050 data and feeding it to virtual serial port.

## Software

Use matplotlib and tkinter to plot sensors data.
Handle start / stop serial connection to the sensor.
Save and load data to and from file.

## Next steps (ToDo)

- [x] interactive plot with matplotlib .. intplot.py
- [x] run interactive plot until it's closed .. testPlotClosed.py
- [x] embed plot to tkinter
- [x] more axis
- [x] connect gyro
- [x] start / stop ploting
- [x] connect / disconnect port
- [x] save / load data
- [x] window title, axes labels and so on
- [x] settings (port, range, ect.)
- [ ] save and restore settings
- [x] substract average acceleration
- [x] file replay
- [ ] calculate and display values: gravity (avg), rms, frequency

... and many others

## Future steps

- [ ] evaulate speed and steps - forward / backward
- [ ] make it wireless 
