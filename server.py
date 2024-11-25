import socket
import select
import os
import struct

BUFFER_SIZE = 512
RECORD_NUM = 100

class Server:
    def __init__(self, port):
        self.hostname = socket.gethostname()
        self.port = port
        self.listen_fd = None

    def initialize(self):
        self.listen_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(self.listen_fd)
        self.listen_fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_fd.bind(('', self.port))
        self.listen_fd.listen(1024)

class Request:
    def __init__(self):
        self.conn_fd = None
        self.buf = bytearray(BUFFER_SIZE)
        self.buf_len = 0
        self.id = 0

    def reset(self):
        self.conn_fd = None
        self.buf = bytearray(BUFFER_SIZE)
        self.buf_len = 0
        self.id = 0


def main():
    import sys
    if len(sys.argv) != 2:
        print("usage: [port]")
        sys.exit(1)

    port = int(sys.argv[1])
    server = Server(port)
    server.initialize()

    request_table = {}
    check_fds = [server.listen_fd]
    print(server.listen_fd)
    
    while True:
      
        read_fds, _, _ = select.select(check_fds, [], [], None)
        
        for fd in read_fds:
            print(server.listen_fd.fileno())
            if fd.fileno() == server.listen_fd.fileno(): 
                conn_fd, cliaddr = server.listen_fd.accept()
                print(conn_fd)
                print(f"New connection from {cliaddr}")
                conn_fd.setblocking(0)
                check_fds.append(conn_fd)
                request_table[conn_fd.fileno] = Request()
                request_table[conn_fd.fileno].conn_fd = conn_fd

            else:  
                print(fd)
                request = fd.recv(1024).decode()
                print(request)
                if request == "login" :
                    response = "hihi"
                    fd.send(response.encode())
                elif request == "logout":
                    response = "hihi"
                    fd.send(response.encode())
                elif request == "gamble":
                    response = "hihi"
                    fd.send(response.encode())
                elif request == "exit":
                    del request_table[fd.fileno]
                    check_fds.remove(fd)
                  
                
if __name__ == "__main__":
    main()
