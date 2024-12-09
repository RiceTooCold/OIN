import psycopg2
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

# Function to open new bets for a specific game and allow setting odds
def open_new_bets_with_odds(game_id):
    conn = connect_db()
    if not conn:
        return

    try:
        # Start a transaction
        with conn:
            with conn.cursor() as cur:
                # Fetch existing bet odds for the game
                fetch_odds_query = """
                SELECT record_id, type_id, odd_1, odd_2, status
                FROM BET_ODDS_RECORD
                WHERE game_id = %s AND status = 'Not yet started';
                """
                cur.execute(fetch_odds_query, (game_id,))
                bet_records = cur.fetchall()

                if not bet_records:
                    print(f"No bet records found with status 'Not yet started' for Game ID: {game_id}.")
                    return

                print(f"Found {len(bet_records)} bet record(s) for Game ID {game_id} ready to open:")

                # Allow admin to set odds for each bet record
                for record in bet_records:
                    record_id, type_id, old_odd_1, old_odd_2, status = record
                    print(f"\nRecord ID: {record_id}, Type ID: {type_id},  Status: {status}")

                    # Input new odds
                    try:
                        new_odd_1 = float(input(f"Enter new Odd 1 (Home) for Record ID {record_id}: "))
                        new_odd_2 = float(input(f"Enter new Odd 2 (Away) for Record ID {record_id}: "))

                        if new_odd_1 <= 0 or new_odd_2 <= 0:
                            print("Odds must be positive numbers.")
                            return
                    except ValueError:
                        print("Invalid input for odds. Please enter numeric values.")
                        return

                    # Update bet record with new odds and status
                    update_odds_query = """
                    UPDATE BET_ODDS_RECORD
                    SET odd_1 = %s, odd_2 = %s, status = 'Processing', latest_modified = %s
                    WHERE record_id = %s;
                    """
                    cur.execute(update_odds_query, (new_odd_1, new_odd_2, datetime.now(), record_id))
                    print(f"Updated Record ID {record_id} with new Odds: Home ({new_odd_1}), Away ({new_odd_2}).")

                # Commit transaction
                conn.commit()
                print(f"Successfully opened new bets for Game ID {game_id}.")

    except Exception as e:
        print(f"Error opening new bets: {e}")
        conn.rollback()  # Rollback transaction in case of error
    finally:
        conn.close()

# Example usage
if __name__ == "__main__":
    try:
        game_id = input("Enter the Game ID to open new bets: ").strip()
        open_new_bets_with_odds(game_id)
    except ValueError:
        print("Invalid Game ID. Please enter a valid ID.")
