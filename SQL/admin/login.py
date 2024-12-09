import psycopg2

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

# Function to authenticate admin
def admin_login():
    conn = connect_db()
    if not conn:
        return False

    try:
        with conn.cursor() as cur:
            # Input admin credentials
            admin_id = input("Enter Admin ID: ").strip()
            password = input("Enter Password: ").strip()

            # Query to validate admin credentials
            login_query = """
            SELECT admin_name
            FROM ADMIN
            WHERE admin_id = %s AND password = %s;
            """
            cur.execute(login_query, (admin_id, password))
            admin = cur.fetchone()

            if admin:
                print(f"Welcome, {admin[0]}! Login successful.")
                return True
            else:
                print("Invalid credentials. Login failed.")
                return False

    except Exception as e:
        print(f"Error during login: {e}")
        return False
    finally:
        conn.close()

# Example usage
if __name__ == "__main__":
    if admin_login():
        print("Admin logged in. You can now access admin features.")
    else:
        print("Login failed. Exiting program.")
