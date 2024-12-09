import psycopg2
from datetime import datetime
import pandas as pd

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

# Function to fetch all bets for a specific date
def fetch_bets_by_date(bet_date):
    conn = connect_db()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
            # Fetch all bets for the given date
            bets_query = """
            SELECT 
                gb.bet_time,
                gb.gamb_id,
                gb.rec_id,
                gb.which_side,
                gb.odd,
                gb.amount,
                CASE
                    WHEN g.home_win = 'W' AND gb.which_side = 'Home' THEN 'Win'
                    WHEN g.home_win = 'L' AND gb.which_side = 'Away' THEN 'Win'
                    ELSE 'Lose'
                END AS result,
                CASE
                    WHEN g.home_win = 'W' AND gb.which_side = 'Home' THEN gb.amount * gb.odd
                    WHEN g.home_win = 'L' AND gb.which_side = 'Away' THEN gb.amount * gb.odd
                    ELSE 0
                END AS winnings
            FROM GAMBLER_BETS gb
            JOIN BET_ODDS_RECORD bor ON gb.rec_id = bor.record_id
            JOIN GAME g ON bor.game_id = g.game_id
            WHERE DATE(g.game_date) = %s
            ORDER BY gb.amount DESC, winnings DESC;
            """
            cur.execute(bets_query, (bet_date,))
            bets = cur.fetchall()

            # Check if bets exist
            if not bets:
                print(f"No bets found for the date {bet_date}.")
                return

            # Create a DataFrame for better visualization
            columns = [
                "Bet Time", "Gambler ID", "Record ID", "Which Side", "Odd",
                "Amount", "Result", "Winnings"
            ]
            bets_df = pd.DataFrame(bets, columns=columns)

            # Display the DataFrame
            print("\nBets for Date:", bet_date)
            print(bets_df)

    except Exception as e:
        print(f"Error fetching bets: {e}")
    finally:
        conn.close()

# Example usage
if __name__ == "__main__":
    try:
        bet_date = input("Enter the date to fetch bets (YYYY-MM-DD): ").strip()
        datetime.strptime(bet_date, "%Y-%m-%d")  # Validate date format
        fetch_bets_by_date(bet_date)
    except ValueError:
        print("Invalid date format. Please enter a date in YYYY-MM-DD format.")
