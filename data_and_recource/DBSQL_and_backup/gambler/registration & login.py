import psycopg2
from psycopg2 import sql
from datetime import datetime

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "dbname": "OIN",
    "user": "postgres",
    "password": "705046",
}

# Function to connect to the database
def connect_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# Function to check if a gambler exists in the database by name
def check_gambler_name(name):
    query = "SELECT gambler_id FROM GAMBLER WHERE gam_name = %s;"
    conn = connect_db()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(query, (name,))
                result = cur.fetchone()
                return result is not None  # True if found, False otherwise
        except Exception as e:
            print(f"Error checking gambler existence: {e}")
            return False
        finally:
            conn.close()
    return False

# Function to validate gambler's password and return balance if valid
def validate_gambler_password(name, password):
    query = "SELECT balance FROM GAMBLER WHERE gam_name = %s AND password = %s;"
    conn = connect_db()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(query, (name, password))
                result = cur.fetchone()
                if result:
                    return result[0]  # Return balance if password matches
                else:
                    return None
        except Exception as e:
            print(f"Error validating password: {e}")
            return None
        finally:
            conn.close()
    return None

# Function to get the next gambler_id
def get_next_gambler_id(conn):
    query = "SELECT COALESCE(MAX(gambler_id), 'G000000000') FROM GAMBLER;"
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            max_id = cur.fetchone()[0]
            next_id = f"G{int(max_id[1:]) + 1:09d}"
            return next_id
    except Exception as e:
        print(f"Error generating next gambler ID: {e}")
        raise

# Function to register a new gambler
def register_gambler(name, password, email):
    conn = connect_db()
    if not conn:
        print("Database connection failed.")
        return
    
    try:
        # Begin transaction
        conn.autocommit = False
        print("Transaction started for registration.")

        # Generate the next gambler_id
        gambler_id = get_next_gambler_id(conn)
        join_date = datetime.now().strftime('%Y-%m-%d')
        balance = 0.0

        # Insert new gambler
        query = """
        INSERT INTO GAMBLER (gambler_id, gam_name, email, password, join_date, balance)
        VALUES (%s, %s, %s, %s, %s, %s);
        """
        with conn.cursor() as cur:
            cur.execute(query, (gambler_id, name, email, password, join_date, balance))
        
        # Commit the transaction
        conn.commit()
        print(f"Registration successful. Welcome, {name}!")
        print(f"Your balance is: {balance}")
    except Exception as e:
        # Rollback the transaction in case of error
        conn.rollback()
        print(f"Registration failed: {e}")
    finally:
        # Ensure the connection is closed
        conn.close()

# Function to manage login or registration with balance display
def manage_login_or_registration():
    name = input("Enter your name: ")

    if check_gambler_name(name):
        # User exists, validate password
        while True:
            password = input("Enter your password: ")
            balance = validate_gambler_password(name, password)
            if balance is not None:
                print(f"Login successful. Welcome back, {name}!")
                print(f"Your balance is: {balance}")
                break
            else:
                print("Incorrect password. Please try again.")
    else:
        # User does not exist, proceed to registration
        print("User not found. Proceeding to registration...")
        password = input("Enter your password: ")
        email = input("Enter your email: ")
        register_gambler(name, password, email)

# Example usage
if __name__ == "__main__":
    manage_login_or_registration()