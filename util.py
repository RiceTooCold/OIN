import os
import platform
import time
import psycopg2

BUFFER_SIZE = 4096

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
        
        
def connect_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None
    

def choises(choises):
    msg = ''
    for idx, choise in enumerate(choises, 1):
        if hasattr(choise, 'get_name'): 
            msg += f'{idx}. {choise.get_name()}\n'
        else: 
            msg += f'.{idx}. {choise}\n'
    return msg


def make_the_choise(conn, choises):
        
    option_idx = [x for x in range(1, len(choises)+1)]
    
    recv_msg = conn.recv(BUFFER_SIZE).decode('utf-8')
    
    while int(recv_msg) not in option_idx:
        msg = "[GET]Wrong input, please select "
        for idx in option_idx:
            msg = msg + f'[{idx}] '
        msg += ': '
        conn.send(msg.encode('utf-8'))
        recv_msg = conn.recv(BUFFER_SIZE).decode("utf-8")
    
    return choises[int(recv_msg)-1]

def recv_msg(conn):
    msg = b""
    first_recv = conn.recv(BUFFER_SIZE)
    if "[TABLE]".encode('utf-8') not in first_recv:
        return first_recv.decode('utf-8')
        
    msg += first_recv
    while True:
        recv = conn.recv(BUFFER_SIZE)
        msg += recv
        if "[END]".encode('utf-8') in msg:
            break
    return msg.decode('utf-8').replace("[END]", '').replace("[TABLE]", '')
    
    
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

    
    
