import socket
import sys
from util import *

class Client:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.conn = None

    def connect(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.ip, self.port))

def handle_response(client):
    
    while True:

        response = recv_msg(client.conn)

        if not response:
            print("Connection closed.")
            break
        if response.find("[EXIT]") != -1:
            response = response.replace("[EXIT]", '')
            cbc_print(response)
            break
        if response.find("[GET]") != -1:
            print(response.replace("[GET]", ''), end = '')
            send_msg = input().strip()
            while len(send_msg) == 0:
                print("Input cannot be empty. Please enter again:", end=' ')
                send_msg = input().strip()

            if send_msg == "exit":
                break            
            client.conn.send(send_msg.encode('utf-8'))   

        elif response.find("[START]") != -1:
            response = response.replace("[START]", '')
            cbc_print(response)
        else:
            print(response, end='')


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
    
    # handling response recv from server
    handle_response(client)
    
    client.conn.close()
    
        
if __name__ == "__main__":
    clear()
    main()
