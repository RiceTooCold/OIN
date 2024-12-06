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

# Function to update gambler's profile and print the updated record
def update_gambler_profile_transaction(gambler_id, new_name=None, new_email=None, new_password=None):
    fields_to_update = []
    values = []

    if new_name:
        fields_to_update.append("gam_name = %s")
        values.append(new_name)
    if new_email:
        fields_to_update.append("email = %s")
        values.append(new_email)
    if new_password:
        fields_to_update.append("password = %s")
        values.append(new_password)

    if not fields_to_update:
        print("No updates provided. Nothing to change.")
        return

    # Build dynamic SQL query for update
    update_query = f"""
    UPDATE GAMBLER
    SET {', '.join(fields_to_update)}
    WHERE gambler_id = %s;
    """
    values.append(gambler_id)

    # Query to fetch updated profile
    select_query = """
    SELECT gambler_id, gam_name, email, password, join_date, balance
    FROM GAMBLER
    WHERE gambler_id = %s;
    """

    conn = connect_db()
    if conn:
        try:
            conn.autocommit = False  # Start transaction
            with conn.cursor() as cur:
                # Execute update query
                cur.execute(update_query, values)
                # Fetch updated profile
                cur.execute(select_query, (gambler_id,))
                updated_profile = cur.fetchone()

                # Commit transaction
                conn.commit()

                # Print updated profile
                if updated_profile:
                    print("Updated Profile:")
                    print(f"Gambler ID: {updated_profile[0]}")
                    print(f"Name: {updated_profile[1]}")
                    print(f"Email: {updated_profile[2]}")
                    print(f"Password: {updated_profile[3]}")
                    print(f"Join Date: {updated_profile[4]}")
                    print(f"Balance: {updated_profile[5]}")
                else:
                    print("Gambler not found after update.")

        except Exception as e:
            conn.rollback()  # Rollback transaction on error
            print(f"Transaction failed: {e}")
        finally:
            conn.close()

# Example usage
if __name__ == "__main__":
    gambler_id = input("Enter your gambler ID: ")

    print("Enter new values for the fields you want to update. Leave blank to keep current values.")
    new_name = input("New name (gam_name): ").strip() or None
    new_password = input("New password: ").strip() or None
    new_email = input("New email: ").strip() or None
    print("-" * 40)
    
    update_gambler_profile_transaction(gambler_id, new_name, new_email, new_password)
