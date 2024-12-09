import socket
import sys
from threading import Thread
import signal
import psycopg2

from util import *
from action.admin.query_gambler import fetch_gambler_details
from action.admin.update_odds import manage_bet_odds
from action.gambler.make_or_update_bet import handle_bet_transaction
from action.gambler.query_bet_type import query_bet_type
from action.gambler.query_date import fetch_games_by_date
from action.gambler.query_game import query_game  
from action.gambler.update_profile import update_gambler_profile_transaction

from action.registration import registration 
from action.login import Login
from action.logout import logout
from action.Exit import Exit

BUFFER_SIZE = 4096
RECORD_NUM = 100

welcome_action = [
    query_game("Query game"), 
    fetch_games_by_date("Fetch games by date"),
    query_bet_type("query type"),
    Login("Login"),
    registration("Registration"),
    Exit("Exit")
]


Gambler_action = [
    query_game("Query game"), 
    fetch_games_by_date("Fetch games by date"),
    query_bet_type("query type"),
    handle_bet_transaction("Update bets"),
    update_gambler_profile_transaction("Update profile"),
    logout("Log out")
]

Admin_action = [
    fetch_gambler_details("Fetch gambler detail"), 
    manage_bet_odds("Update odds"), 
    logout("Log out")
]


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


def signal_handler(sig, frame, db, server):
    db.close()
    server.listen_fd.close()
    sys.exit(0)


def handle_connection(conn, client_addr, db, cur):
    try:
        
        while True: # Welcome Page
            conn.send("----------------------------------------\nWelcome to Oin! please enjoy yourself\n".encode('utf-8'))
            conn.send(f'[INPUT]Feel free to choise one of below choise:\n{list_option(welcome_action)})---> '.encode('utf-8'))
            action = get_selection(conn, welcome_action)
            
            user = action.exec(conn, db, cur)
                  
            if user == -2:
                break
            
            elif user:
                if user.get_role() == 1:
                    while True:
                        conn.send("----------------------------------------\nHi Admin! Welcome back to Oin!\n".encode('utf-8'))
                        conn.send(f'[INPUT]Please select your option:\n{list_option(Admin_action)}---> '.encode('utf-8'))
                        action = get_selection(conn, Admin_action)
                        
                        next_step = action.exec(conn, db, cur)
                        
                        if next_step == -1:
                            break
                    
                if user.get_role() == 2:
                    while True:
                        conn.send("----------------------------------------\nHi gambler! Welcome back to Oin!\n".encode('utf-8'))
                        conn.send(f'[INPUT]Please select your option:\n{list_option(Gambler_action)}---> '.encode('utf-8'))
                        action = get_selection(conn, Gambler_action)
                        
                        next_step = action.exec(conn, db, cur, user)
                        
                        if next_step == -1:
                            break
            

    except Exception:
        print(f"Connection with {client_addr} close.")
        conn.close()
        return
    
    finally:
        print(f"Connection with {client_addr} close.")
        conn.close()
        return  
        
def main():
    
    if len(sys.argv) != 2:
        print("usage: [port]")
        sys.exit(1)

    # init server
    port = int(sys.argv[1])
    server = Server(port)
    server.initialize()

    # init db
    db = connect_db()
    cur = db.cursor()
    
    # signal.signal(signal.SIGINT, signal_handler)
    try:
        while True:
            (conn, client_addr) = server.listen_fd.accept()

            thread = Thread(target=handle_connection, args=(conn, client_addr, db, cur, ))
            thread.start()
    finally:
        db.close()
        server.listen_fd.close()
                
if __name__ == "__main__":
    main()