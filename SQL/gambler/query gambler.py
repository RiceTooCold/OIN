import psycopg2
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

# Function to fetch user details without showing the password
def fetch_gambler_details(gambler_id):
    gambler_query = """
    SELECT 
        gambler_id, 
        gam_name, 
        email, 
        join_date, 
        balance 
    FROM GAMBLER
    WHERE gambler_id = %s;
    """
    bets_query = """
    SELECT 
        gb.bet_time, 
        gb.rec_id, 
        gb.which_side, 
        gb.amount, 
        gb.status,
        CASE
            WHEN g.status != 'Ended' THEN 'Processing'
            WHEN g.home_win = 'W' AND gb.which_side = 'Home' THEN 'Win'
            WHEN g.home_win = 'L' AND gb.which_side = 'Away' THEN 'Win'
            ELSE 'Lose'
        END AS result
    FROM GAMBLER_BETS gb
    JOIN BET_ODDS_RECORD bor ON gb.rec_id = bor.record_id
    JOIN GAME g ON bor.game_id = g.game_id
    WHERE gb.gamb_id = %s
    ORDER BY 
        CASE 
            WHEN g.status != 'Ended' THEN 1
            ELSE 2
        END ASC,
        gb.bet_time DESC
    LIMIT 10;
    """
    total_amount_query = """
    SELECT 
        COALESCE(SUM(amount), 0)
    FROM GAMBLER_BETS
    WHERE gamb_id = %s;
    """
    conn = connect_db()
    if conn:
        try:
            with conn.cursor() as cur:
                # Fetch gambler details
                cur.execute(gambler_query, (gambler_id,))
                gambler_details = cur.fetchone()
                if gambler_details:
                    print("User Details:")
                    print(f"Gambler ID: {gambler_details[0]}")
                    print(f"Name: {gambler_details[1]}")
                    print(f"Email: {gambler_details[2]}")
                    print(f"Join Date: {gambler_details[3]}")
                    print(f"Balance: {gambler_details[4]}")
                    print("-" * 40)

                    # Fetch total bet amount
                    cur.execute(total_amount_query, (gambler_id,))
                    total_amount = cur.fetchone()[0]

                    # Fetch last 5 bets with results
                    cur.execute(bets_query, (gambler_id,))
                    bets = cur.fetchall()
                    if bets:
                        # Convert bets to DataFrame
                        columns = ["Bet Time", "Record ID", "Side", "Amount", "Status", "Result"]
                        bets_df = pd.DataFrame(bets, columns=columns)

                        # Display DataFrame and total amount
                        print("Last 5 Bets:")
                        print(bets_df)
                        print(f"\nTotal Amount of All Bets: {total_amount}")
                    else:
                        print("No bets found for this gambler.")
                else:
                    print("No gambler found with the given ID.")
        except Exception as e:
            print(f"Error fetching gambler details: {e}")
        finally:
            conn.close()

# Example usage
if __name__ == "__main__":
    gambler_id = input("Enter the gambler ID to fetch details: ")
    print("-" * 40)
    fetch_gambler_details(gambler_id)
