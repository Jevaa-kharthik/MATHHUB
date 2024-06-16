from subprocess import PIPE, Popen, STDOUT
from threading import Thread
import socket
import logging
from collections import defaultdict
import time

HOST = '172.168.67.188'
PORT = 3099

THRESHOLD = 50  
WINDOW_SIZE = 60  
BLOCK_DURATION = 300  
connection_counts = defaultdict(int)
blocked_ips = set()

logging.basicConfig(filename='dos.log', level=logging.INFO,
                    format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

class OutputThread(Thread):
    def __init__(self, proc, conn):
        Thread.__init__(self)
        self.proc = proc
        self.conn = conn

    def run(self):
        while not self.proc.stdout.closed and not self.conn._closed:
            try:
                line = self.proc.stdout.readline()
                if not line:
                    break
                self.conn.sendall(line.encode())
            except:
                pass

class MathServerThread(Thread):
    def __init__(self, conn, addr):
        Thread.__init__(self)
        self.conn = conn
        self.addr = addr

    def run(self):
        print("{} connected with the back port {}".format(self.addr[0], self.addr[1]))
        self.conn.sendall("Welcome to the MATHHUB SERVER \n Give any Mathematical Equation and Don't try to DOS or DDoS this Server \n\n Because this has firewall".encode())

        p = Popen(['bc'], stderr=STDOUT, stdout=PIPE, stdin=PIPE, text=True)
        output = OutputThread(p, self.conn)
        output.start()

        while not p.stdout.closed and not self.conn._closed:
            try:
                data = self.conn.recv(1024)
                if not data:
                    break
                else:
                    try:
                        query = data.decode().strip()
                        if query.lower() == "quit" or query.lower() == "exit":
                            p.communicate(query, timeout=1)
                            if p.poll() is not None:
                                break
                        query += "\n"
                        p.stdin.write(query)
                        p.stdin.flush()
                        p.stdin.timeout(10)
                    except Exception as e:
                        print(f"Error processing data: {e}")
            except Exception as e:
                print(f"Error receiving data: {e}")

def firewall_check(addr):
    ip = addr[0]
    if ip in blocked_ips:
        return False
    connection_counts[ip] += 1
    if connection_counts[ip] > THRESHOLD:
        logging.info(f'DoS attack detected from {ip}')
        # Block the IP address
        block_ip(ip)
        return False

    return True

def block_ip(ip):
    blocked_ips.add(ip)


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()

    while True:
        conn, addr = s.accept()

        if firewall_check(addr):
            MathServerThread(conn, addr).start()
        else:
            print("Access denied: Your IP address is not allowed by the firewall")

    s.close()

if __name__ == "__main__":
    main()
