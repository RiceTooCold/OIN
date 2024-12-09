from datetime import datetime
from .Action import Action
from .util import *
from .role.user import User

class registration(Action):
    
    # Function to check if a admmin exists in the database by name
    def check_name_exist(self, name, conn, cur):

        query1 = """
        SELECT 
           *
        FROM Gambler g
        WHERE g.gam_name = %s 
        """
        query2 = """
        SELECT 
           *
        FROM Admin a
        WHERE a.admin_name = %s;
        """
        try:
            cur.execute(query1, (name,))
            result1 = cur.fetchone()
            cur.execute(query2, (name,))
            result2 = cur.fetchone()

            exist = False
            if result1 or result2: 
                exist = True
            return exist
        
        except Exception as e:
            conn.send(f"Error checking admin existence: {e}\n".encode('utf-8'))
            return False
        
    def check_password_exist(self, pwd, conn, cur):
        query1 = """
        SELECT 
           *
        FROM Gambler g
        WHERE g.password = %s 
        """
        query2 = """
        SELECT 
           *
        FROM Admin a
        WHERE a.password = %s;
        """

        try:
            cur.execute(query1, (pwd,))
            result1 = cur.fetchone()
            cur.execute(query2, (pwd,))
            result2 = cur.fetchone()
            exist = False
            if result1 or result2: 
                exist = True
            return exist 
        except Exception as e:
            conn.send(f"Error checking admin existence: {e}\n".encode('utf-8'))
            return False
        
    def check_email_exist(self, email, conn, cur):
        query = """
        SELECT 
           *
        FROM Gambler g
        WHERE g.email = %s ;
        """
        try:
            cur.execute(query, (email,))
            result = cur.fetchone()
            return result is not None 
        except Exception as e:
            conn.send(f"Error checking admin existence: {e}\n".encode('utf-8'))
            return False
        
    # Function to get the next gambler_id
    def get_next_gambler_id(self, conn, cur):
        query = "SELECT COALESCE(MAX(gambler_id), 'G000000000') FROM GAMBLER;"
        try:
            cur.execute(query)
            max_id = cur.fetchone()[0]
            next_id = f"G{int(max_id[1:]) + 1:09d}"
            return next_id
        except Exception as e:
            conn.send(f"Error generating next gambler ID: {e}\n".encode('utf-8'))
            raise

    # Function to register a new gambler
    def register_gambler(self, name, password, email, conn, db, cur):
        try:
            # Begin transaction
            # db.autocommit = True # weird
            conn.send("Transaction started for registration.\n".encode('utf-8'))

            # Generate the next gambler_id
            gambler_id = self.get_next_gambler_id(conn, cur)
            join_date = datetime.now().strftime('%Y-%m-%d')
            balance = 0.0

            # Insert new gambler
            query = """
            INSERT INTO GAMBLER (gambler_id, gam_name, email, password, join_date, balance)
            VALUES (%s, %s, %s, %s, %s, %s);
            """
            cur.execute(query, (gambler_id, name, email, password, join_date, balance))
            print(f'{gambler_id} {name} {email} {password} {join_date} {balance}')
            # Commit the transaction
            db.commit()
            conn.sendall(f"Registration successful. Welcome, {name}!\n".encode('utf-8'))
            conn.sendall(f"Your balance is: {balance}\n".encode('utf-8'))
            return gambler_id
        except Exception as e:
            # Rollback the transaction in case of error
            db.rollback()
            conn.send(f"Registration failed: {e}\n".encode('utf-8'))


    def exec(self, conn, db, cur):
        conn.send("Let's create your own account!\n".encode('utf-8'))
        while True:
            conn.send("[INPUT]Enter your name: ".encode('utf-8'))
            name = conn.recv(1024).decode('utf-8').strip()
            print("wtf")
            if self.check_name_exist(name, conn, cur) == False:
                break
            else: 
                conn.send(f"Name {name} has already existed. please try again\n".encode('utf-8'))
            
        while True:
            conn.send("[INPUT]Enter your password: ".encode('utf-8'))
            password = conn.recv(1024).decode('utf-8').strip()
            if self.check_password_exist(password, conn, cur) == False:
                break
            else: 
                conn.send(f"Password {password} has already existed. please try again\n".encode('utf-8'))
        
        while True:
            conn.send("[INPUT]Enter your email: ".encode('utf-8'))
            email = conn.recv(1024).decode('utf-8').strip()
            if self.check_email_exist(email, conn, cur) == False:
                break
            else: 
                conn.send(f"Email {email} has already existed. please try again\n".encode('utf-8'))
                
        gambler_id = self.register_gambler(name, password, email, conn, db, cur)
        role = User(gambler_id, name, email, password, 2)
        return role
        

# # Example usage
# if __name__ == "__main__":
#     manage_login_or_registration()