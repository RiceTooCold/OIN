import os
import platform
import time
import sys
import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "dbname": "OIN",
    "user": "postgres",
    "password": "5432",
    # 705046
}


def clear():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')


def cbc_print(string: str, interval: float = 0.05):
    '''
    Print the string char by char.
    '''
    for c in string:
        print(c, end='', flush=True)
        time.sleep(interval)

def twinkle_print(string: str, interval: float = 0.2, times: int = 3):
    for _ in range(times):
        print(string, end='\r')
        time.sleep(0.2)
        print(' '*len(string), end='\r')
        time.sleep(0.2)
    print(string)
    time.sleep(0.2)
    
# def signal_handler(sig, frame, db, server):
#     db.close()
#     server.listen_fd.close()
#     sys.exit(0)


def list_option(options):
    msg = ''
    if isinstance(options, dict):
        for idx, option in options.items():
            msg = msg + f'[{idx}] {option.get_name()}\n'
    elif isinstance(options, list):
        for idx, option in enumerate(options, 1):
            if hasattr(option, 'get_name'): # Action class
                msg += f'[{idx}] {option.get_name()}\n'
            else: # User info item
                msg += f'[{idx}] {option}\n'
            

    return msg


def connect_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None


def get_selection(conn, options):
        
    if isinstance(options, dict):
        option_idx = options.keys()
    else:
        option_idx = [x for x in range(1, len(options)+1)]
    recv_msg = conn.recv(100).decode("utf-8")
    while int(recv_msg) not in option_idx:
        msg = "[INPUT]Wrong input, please select "
        for idx in option_idx:
            msg = msg + f'[{idx}] '
        msg += ': '
        conn.send(msg.encode('utf-8'))
        
        recv_msg = conn.recv(100).decode("utf-8")
    print("Select option:", recv_msg)
    
    if isinstance(options, dict):
        return options[recv_msg]
    else:
        return options[int(recv_msg)-1]

    
    
