from .Action import Action
from .util import *
from .user.user import User

class Login(Action):

    # Function to check if a admmin exists in the database by name
    def check_Admin_name(self, name, conn, cur):
        query = "SELECT admin_id FROM ADMIN WHERE admin_name = %s;"
        try:
            cur.execute(query, (name,))
            result = cur.fetchone()
            return result is not None 
        except Exception as e:
            conn.send(f"Error checking admin existence: {e}\n".encode('utf-8'))
            return False
          
    # Function to validate admin's password and return balance if valid
    def validate_Admin_password(self, name, password, conn, cur):
        query = "SELECT * FROM ADMIN WHERE admin_name = %s AND password = %s;"
        try:
            cur.execute(query, (name, password))
            result = cur.fetchone()
            if result:
                return result  # Return balance if password matches
            else:
                return None
        except Exception as e:
            conn.send(f"Error validating password: {e}\n".encode('utf-8'))
            return None
          
    # Function to check if a gambler exists in the database by name
    def check_gambler_name(self, name, conn, cur):
        query = "SELECT gambler_id FROM GAMBLER WHERE gam_name = %s;"
        try:
            cur.execute(query, (name,))
            result = cur.fetchone()
            return result is not None  # True if found, False otherwise
        except Exception as e:
            conn.send(f"Error checking gambler existence: {e}\n".encode('utf-8'))
            return False
          
    # Function to validate gambler's password and return balance if valid
    def validate_gambler_password(self, name, password, conn, cur):
        query = "SELECT * FROM GAMBLER WHERE gam_name = %s AND password = %s;"
        try:
            cur.execute(query, (name, password))
            result = cur.fetchone()
            if result:
                return result  # Return balance if password matches
            else:
                return None
        except Exception as e:
            conn.send(f"Error validating password: {e}\n".encode('utf-8'))
            return None
          
          
    def exec(self, conn, db, cur, user):
        while True:
            conn.send("\n[GET]Enter your name: ".encode('utf-8'))
            name = conn.recv(1024).decode('utf-8').strip()

            user_flag = -1
            if self.check_Admin_name(name, conn, cur): 
                user_flag = 1
            elif self.check_gambler_name(name, conn, cur):
                user_flag = 2
              # User exists, validate password
            if user_flag > 0:
                while True:
                    conn.send("[GET]Enter your password: ".encode('utf-8'))
                    password = conn.recv(1024).decode('utf-8').strip()
                    if user_flag == 1:
                        result = self.validate_Admin_password(name, password, conn, cur)
        
                        if result is not None:
                            admin_id, admin_name, password = result
                            role = User(admin_id, admin_name, "", password, 1)
                            conn.sendall(f"Login successful. Welcome back Admin, {name}!\n".encode('utf-8'))
                            return role
                        else:
                            conn.send("Incorrect password. Please try again.\n".encode('utf-8'))
                    
                    elif user_flag == 2:
                        result = self.validate_gambler_password(name, password, conn, cur)
                        print(result)
                        if result is not None:
                            gambler_id, gam_name, email, password, date, balance = result
                            role = User(gambler_id, gam_name, email, password, 2)
                            
                            conn.sendall(f"\nLogin successful. Welcome back Gambler, {name}!\n".encode('utf-8'))
                            conn.sendall(f"Your balance is: {balance}\n".encode('utf-8'))
                            return role
                        else:
                            conn.send("Incorrect password. Please try again.\n".encode('utf-8'))
                    
            else:
                conn.send((f"{name} does not exist. Please try again\n").encode('utf-8'))