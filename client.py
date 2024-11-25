import socket
import sys
import struct
import util

BUFFER_SIZE = 512
RECORD_NUM = 10

class Client:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.conn = None

    def connect(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.ip, self.port))


def main():

    if len(sys.argv) != 3:
        print("usage: [ip] [port]")
        sys.exit(1)

    ip = sys.argv[1]
    try:
        port = int(sys.argv[2])
        if not (0 < port <= 65535):
            raise ValueError
    except ValueError:
        print("Invalid port")
        sys.exit(1)

    client = Client(ip, port)
    client.connect()
    
    # send_welcome_mes()
    
    while True:
        print("Welcome to the Oin")
        print("1. login")
        print("2. logout")
        print("3. gamble")
        print("4. exit")
        command = input("Please enter your command: ").strip()
        # client.conn.send(command.encode())
        if command == "login":
            client.conn.send(command.encode())
            response = client.conn.recv(1024).decode()
            print(response)
            if response == "0":
                print("[Error] Maximum posting limit exceeded")
                continue

        elif command == "logout":
            client.conn.send(command.encode())
            response = client.conn.recv(1024).decode()

        elif command == "gamble":
            client.conn.send(command.encode())
        elif command == "exit":
            client.conn.send(command.encode())
            sys.exit(0)


if __name__ == "__main__":
    util.clear()
    main()
