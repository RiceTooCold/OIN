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

# Function to fetch bet odds record details
def fetch_bet_odds_record(record_id):
    query = """
    SELECT 
        record_id, 
        game_id, 
        odd_1, 
        odd_2, 
        status 
    FROM BET_ODDS_RECORD
    WHERE record_id = %s;
    """
    conn = connect_db()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(query, (record_id,))
                record = cur.fetchone()
                if record:
                    return record
                else:
                    print(f"No record found with ID: {record_id}")
                    return None
        except Exception as e:
            print(f"Error fetching bet odds record: {e}")
            return None
        finally:
            conn.close()

# Function to update bet odds
def update_bet_odds(record_id, new_odd_1, new_odd_2):
    query = """
    UPDATE BET_ODDS_RECORD
    SET odd_1 = %s, odd_2 = %s
    WHERE record_id = %s AND status = 'Processing';
    """
    conn = connect_db()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(query, (new_odd_1, new_odd_2, record_id))
                if cur.rowcount == 0:
                    print(f"Cannot update record with ID {record_id}. Either it doesn't exist or its status is 'Completed'.")
                else:
                    conn.commit()
                    print(f"Bet odds successfully updated for Record ID {record_id}.")
        except Exception as e:
            print(f"Error updating bet odds: {e}")
        finally:
            conn.close()

# Function to manage bet odds update
def manage_bet_odds():
    record_id = input("Enter the Record ID to update odds: ").strip()
    record = fetch_bet_odds_record(record_id)
    
    if record:
        print("\nCurrent Record Details:")
        print(f"Record ID: {record[0]}")
        print(f"Game ID: {record[1]}")
        print(f"Odd 1: {record[2]}")
        print(f"Odd 2: {record[3]}")
        print(f"Status: {record[4]}")

        if record[4] == "Completed":
            print("\nThis record has a 'Completed' status and cannot be updated.")
        else:
            try:
                new_odd_1 = float(input("Enter new Odd 1: "))
                new_odd_2 = float(input("Enter new Odd 2: "))
                update_bet_odds(record_id, new_odd_1, new_odd_2)
            except ValueError:
                print("Invalid input. Odds must be numeric values.")

# Example usage
if __name__ == "__main__":
    manage_bet_odds()
