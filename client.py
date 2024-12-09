import socket
import sys
import util

BUFFER_SIZE = 4096

class Client:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.conn = None

    def connect(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.ip, self.port))


def receive_message(conn):
    # Keep reading until the delimiter is found
    try:
        message = b""
        first_chunk = conn.recv(BUFFER_SIZE)
        if "[TABLE]".encode('utf-8') not in first_chunk:
            return first_chunk.decode('utf-8')
        
        message += first_chunk

        while True:
            chunk = conn.recv(BUFFER_SIZE)
            if not chunk:
                raise ConnectionError("Connection lost while receiving data")
            message += chunk
            if "[END]".encode('utf-8') in message:
                break
        return message.decode('utf-8').replace("[END]", '').replace("[TABLE]", '')
    except Exception as e:
        print("Receive message error.")
        print(str(e))
        return


def handle_response(client):
    while True:
        response = receive_message(client.conn)

        if not response:
            print("Connection closed by the server.")
            break
        if response.find("[EXIT]") != -1:
            print(response.replace("[EXIT]", ''), end='')
            break
        if response.find("[GET]") != -1:
            print(response.replace("[GET]", ''), end='')

            send_msg = input().strip()
            while len(send_msg) == 0:
                print("Input cannot be empty. Please enter again:", end=' ')
                send_msg = input().strip()

            if send_msg == "exit":
                break            
            client.conn.send(send_msg.encode('utf-8'))   

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
    util.clear()
    main()
