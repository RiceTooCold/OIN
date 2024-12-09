import socket
import sys
from threading import Thread
import signal
from util import *

# admin
from modules.admin.update_odds import manage_bet_odds
from modules.admin.query_bets import fetch_bets_by_date
from modules.admin.roi_rank import fetch_top_gamblers_by_roi 
from modules.admin.start_bet import open_new_bets_with_odds 
from modules.admin.settle_game_and_bet import settle_game

# gambler
from modules.gambler.make_or_update_bet import handle_bet_transaction
from modules.gambler.query_bet_type import query_bet_type
from modules.gambler.query_date import fetch_games_by_date
from modules.gambler.query_game import query_game  
from modules.gambler.update_profile import update_gambler_profile_transaction 
from modules.gambler.query_gambler import fetch_gambler_details
from modules.gambler.query_standings import query_standing  
from modules.gambler.deposit import Deposit

# login related 
from modules.registration import registration 
from modules.login import Login
from modules.logout import logout
from modules.Exit import Exit

BUFFER_SIZE = 4096

welcome_action = [
    query_standing("Query season standing"),
    fetch_games_by_date("Fetch games by date"),
    query_bet_type("query type"),
    Login("Login"),
    registration("Registration"),
    Exit("Exit")
]


Gambler_action = [
    query_standing("Query season standing"),
    fetch_gambler_details("Query Gambler"),
    query_game("Query game"), 
    fetch_games_by_date("Fetch games by date"),
    query_bet_type("query type"),
    handle_bet_transaction("Update bets"),
    update_gambler_profile_transaction("Update profile"),
    Deposit("Top up"),
    logout("Log out")
]

Admin_action = [
    fetch_top_gamblers_by_roi("Top5 Gamblers"),
    fetch_bets_by_date("Query bets by date"),
    open_new_bets_with_odds("Open bets"),
    settle_game("settle the game"),
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
        

def handle_connection(conn, client_addr, db, cur):
    try:
        conn.send("\n==============================================\n              Welcome to Oin!\n   The world largest sports betting system\n".encode('utf-8'))
        
        while True: # Welcome Page
            conn.send(f'==============================================\n[GET]Feel free to choise one of below choises:\n-----------\n{choises(welcome_action)}-----------\n===> '.encode('utf-8'))
            
            choise = make_the_choise(conn, welcome_action)
            user = choise.exec(conn, db, cur, None)
                  
            if user == -2:
                break
            
            elif user:
                if user.get_role() == 1:
                    conn.send("\n=============================================\n    Hi Admin! Welcome back to Oin!\n".encode('utf-8'))
                    
                    while True: 
                        conn.send(f'=============================================\n[GET]What actions you want to take?\n-----------\n{choises(Admin_action)}-----------\n===> '.encode('utf-8'))
                        
                        choise = make_the_choise(conn, Admin_action)
                        next_step = choise.exec(conn, db, cur, user)
                        
                        if next_step == -1:
                            break
                    
                if user.get_role() == 2:
                    conn.send("\n=============================================\n    Hi gambler! Welcome back to Oin!\n".encode('utf-8'))
                    
                    while True:    
                        conn.send(f'=============================================\n[GET]Wants to make fortune? just select the options below:\n-----------\n{choises(Gambler_action)}-----------\n===> '.encode('utf-8'))
                        
                        choise = make_the_choise(conn, Gambler_action)
                        next_step = choise.exec(conn, db, cur, user)
                        
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