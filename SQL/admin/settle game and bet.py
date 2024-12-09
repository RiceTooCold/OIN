import psycopg2
from datetime import datetime
from decimal import Decimal

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

# Generate a new transaction ID based on the table's current max ID
def generate_transaction_id(cur):
    query = """
    SELECT trans_id 
    FROM CASHFLOW_RECORD
    ORDER BY trans_id DESC
    LIMIT 1;
    """
    cur.execute(query)
    result = cur.fetchone()

    if result:
        # Extract numeric part and increment
        last_id = result[0]
        numeric_part = int(last_id[1:])  # Skip the 'T'
        new_id = f"T{numeric_part + 1:09d}"
    else:
        # Start from the first ID if table is empty
        new_id = "T000000001"

    return new_id

# Function to settle a single game by game_id
def settle_game(game_id):
    conn = connect_db()
    if not conn:
        return

    try:
        # Start a transaction
        with conn:
            with conn.cursor() as cur:
                # Fetch match details
                game_query = """
                SELECT game_id, home_score, away_score, home_win, status
                FROM GAME
                WHERE game_id = %s;
                """
                cur.execute(game_query, (game_id,))
                game = cur.fetchone()

                if not game:
                    print("Invalid Game ID.")
                    return

                game_id, home_score, away_score, home_win, status = game

                # Ensure the game is Ongoing before settlement
                if status != "Ongoing":
                    print(f"Game ID {game_id} is not Ongoing. Current status: {status}")
                    return

                # Determine the result of the game
                if home_score > away_score:
                    home_win = 'W'
                elif home_score < away_score:
                    home_win = 'L'
                else:
                    print("The game resulted in a tie. Settlement logic does not handle ties.")
                    return

                # Update game status and home_win
                update_game_status_query = """
                UPDATE GAME
                SET status = 'Ended', home_win = %s
                WHERE game_id = %s;
                """
                cur.execute(update_game_status_query, (home_win, game_id))

                print(f"Game ID {game_id} settled. Home team result: {'Win' if home_win == 'W' else 'Loss'}.")

                # Update bet records to Expire
                update_bet_records_query = """
                UPDATE BETS_ODD_RECORD
                SET status = 'Expired'
                WHERE game_id = %s AND status = 'Processing';
                """
                cur.execute(update_bet_records_query, (game_id,))

                # Fetch bets for the match
                bets_query = """
                SELECT b.gamb_id, b.rec_id, b.which_side, b.odd, b.amount
                FROM GAMBLER_BETS b
                JOIN BETS_ODD_RECORD r ON b.rec_id = r.record_id
                WHERE r.game_id = %s AND b.status = 'Pending';
                """
                cur.execute(bets_query, (game_id,))
                bets = cur.fetchall()

                if not bets:
                    print(f"No bets to settle for Game ID: {game_id}")
                    return

                # Process each bet
                result_data = []
                for gamb_id, rec_id, which_side, odd, amount in bets:
                    # Check if the bet is won
                    is_winner = (which_side == "Home" and home_win == 'W') or (which_side == "Away" and home_win == 'L')
                    winnings = Decimal(0)

                    if is_winner:
                        # Calculate winnings
                        winnings = Decimal(amount) * Decimal(odd)

                        # Update gambler balance
                        update_balance_query = "UPDATE GAMBLER SET balance = balance + %s WHERE gambler_id = %s;"
                        cur.execute(update_balance_query, (winnings, gamb_id))

                        # Add cashflow record
                        trans_id = generate_transaction_id(cur)
                        cashflow_query = """
                        INSERT INTO CASHFLOW_RECORD (trans_id, gamb_id, trans_type, cashflow, time)
                        VALUES (%s, %s, %s, %s, %s);
                        """
                        cur.execute(cashflow_query, (trans_id, gamb_id, "Earn", winnings, datetime.now()))
                        print(f"Bet won by Gambler {gamb_id}. Winnings: {winnings}. Transaction ID: {trans_id}")

                    # Update bet status to 'Completed'
                    update_bet_status_query = """
                    UPDATE GAMBLER_BETS SET status = 'Completed' WHERE gamb_id = %s AND rec_id = %s;
                    """
                    cur.execute(update_bet_status_query, (gamb_id, rec_id))


                # Commit transaction
                conn.commit()
                print(f"Settlement completed for Game ID {game_id}.")

    except Exception as e:
        print(f"Error settling game: {e}")
        conn.rollback()  # Rollback transaction in case of error
    finally:
        conn.close()

# Example usage
if __name__ == "__main__":
    try:
        game_id = input("Enter the Game ID to settle: ").strip()
        settle_game(game_id)
    except ValueError:
        print("Invalid Game ID. Please enter a valid ID.")
