import socket
from time import sleep

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

FILENAME = 'data/dopredu1.csv'

def load_file(fname = FILENAME):
    data = []
    with open(fname, 'r') as fd:
        for line in fd:
            splt = line.strip().split(';')
            val = []
            if len(splt) >= 7:
                for i in range(6):
                    val.append(float(splt[i + 1]))
                if len(val) == 6:
                    data.append(val)
    return data

data = load_file()
#for d in data:
#    print(d)
#print(data)

ptr = 0

print('Awaiting the connection from clinet')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    s.setblocking(False)
    with conn:
        print(f"Connected by {addr}")
        try:
            while True:
                d = data[ptr]
                #print(d)
                msg = '{:0.02f}'.format(d[0])
                for f in d[1:]:
                    msg += ' {:0.02f}'.format(f)
                print(msg)
                msg += '\n'
                conn.sendall(msg.encode('ascii'))
                ptr += 1
                if ptr >= len(data):
                    ptr = 0
                sleep(0.02)
        except ConnectionAbortedError:
            print('Connection closed by client')
