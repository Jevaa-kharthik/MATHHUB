from subprocess import PIPE, Popen, STDOUT
from threading import Thread
import socket
import mysql.connector

HOST = ''
PORT = 3079

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

def login_check(username, password, addr):
    try:
        mydb = mysql.connector.connect(
            host="mysql.selfmade.ninja",
            user="Jevaa_kharthik_n",
            password="jicry9-saxvyb-jytWib",
            database="Jevaa_kharthik_n_Mathserver"
        )

        mycursor = mydb.cursor()
        sqlcheck = "SELECT username, password, ip_address FROM LoginCredentials WHERE username=%s AND password=%s AND ip_address=%s"
        val = (username, password, addr)
        mycursor.execute(sqlcheck, val)
        result = mycursor.fetchone()
        if result:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error checking login credentials: {e}")
        return False

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen()

while True:
    conn, addr = s.accept()
    file = open("ip.txt", 'r')
    if addr[0] in file.read():
        file.close()
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        if login_check(username, password, addr[0]):
            MathServerThread(conn, addr).start()
    else:
        file.close()
        with open("ip.txt", 'a') as f:
            f.write(addr[0] + "\n")

        username = input("Enter your username: ")
        password = input("Enter your password: ")

        mydb = mysql.connector.connect(
            host="mysql.selfmade.ninja",
            user="Jevaa_kharthik_n",
            password="jicry9-saxvyb-jytWib",
            database="Jevaa_kharthik_n_Mathserver"
        )

        mycursor = mydb.cursor()
        sqlquery = "INSERT INTO LoginCredentials (username, password, ip_address) VALUES (%s, %s, %s)"
        val = (username, password, addr[0])
        mycursor.execute(sqlquery, val)
        mydb.commit()

        if login_check(username, password, addr[0]):
            MathServerThread(conn, addr).start()
        else:
            print("Invalid credentials")

s.close()
