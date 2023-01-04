import serial
import click

DEFAULT_PORT = 'COM9'

@click.command()
@click.option('--port', default=DEFAULT_PORT, help='Serial port name')
def read(port):

    with serial.Serial(port, timeout=0) as p:

        buf = ''
        while True:
            cont = p.read()
            for b in cont:
                if b != ord('\n'):
                    buf += chr(b)
                else:
                    print(buf)
                    buf = ''

if __name__ == '__main__':

    read()
