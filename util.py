import os
import platform
import time

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