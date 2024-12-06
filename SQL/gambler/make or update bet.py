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

# Main function to handle bets
def handle_bet_transaction():
    conn = connect_db()
    if not conn:
        return

    try:
        # Start a transaction
        with conn:
            with conn.cursor() as cur:
                # Input for the gambler bet
                gamb_id = input("Enter your Gambler ID: ").strip()
                rec_id = input("Enter the Record ID: ").strip()

                # Fetch odds for the selected record
                record_query = """
                SELECT record_id, odd_1, odd_2, latest_modified, status
                FROM BETS_ODD_RECORD
                WHERE record_id = %s;
                """
                cur.execute(record_query, (rec_id,))
                record = cur.fetchone()

                if not record:
                    print("Invalid Record ID.")
                    return
                _, odd_1, odd_2, latest_modified, status = record

                # Check if the record is expired
                if status == "Expired":
                    print("This record has expired. You cannot place a bet on it.")
                    return

                print(f"   Odds: Home ({odd_1}), Away ({odd_2})")

                # Fetch existing bets
                existing_bets_query = """
                SELECT bet_time, rec_id, which_side, amount, status
                FROM GAMBLER_BETS
                WHERE gamb_id = %s AND rec_id = %s AND status != 'Completed'
                ORDER BY bet_time DESC;
                """
                cur.execute(existing_bets_query, (gamb_id, rec_id))
                existing_bets = cur.fetchall()

                if existing_bets:
                    print("\nYour existing bets for this record:")
                    for idx, bet in enumerate(existing_bets, start=1):
                        print(f"{idx}. Bet Time: {bet[0]}, Side: {bet[2]}, Amount: {bet[3]}, Status: {bet[4]}")

                    # Ask to add new bet or update existing one
                    action = input("\nDo you want to add a new bet or update an existing one? (a/u): ").strip().lower()
                    if action == "u":
                        bet_idx = int(input("Enter the number of the bet you want to update: "))
                        if 1 <= bet_idx <= len(existing_bets):
                            bet_time_to_modify = existing_bets[bet_idx - 1][0]
                            modify_action = input("Do you want to modify or cancel? (m/c): ").strip().lower()

                            if modify_action == "m":
                                # Update bet side
                                new_side = input("Enter the new side (Home/Away): ").strip().capitalize()
                                if new_side in ["Home", "Away"]:
                                    update_side_query = """
                                    UPDATE GAMBLER_BETS
                                    SET which_side = %s, bet_time = %s
                                    WHERE gamb_id = %s AND bet_time = %s;
                                    """
                                    new_bet_time = latest_modified.replace(hour=datetime.now().hour, minute=datetime.now().minute, second=datetime.now().second)
                                    cur.execute(update_side_query, (new_side, new_bet_time, gamb_id, bet_time_to_modify))
                                    print(f"Bet side updated to {new_side} with new time {new_bet_time}.")
                                else:
                                    print("Invalid side choice.")
                                    return

                                # Update bet amount
                                new_amount = float(input("Enter the new amount: "))
                                update_amount_query = """
                                UPDATE GAMBLER_BETS
                                SET amount = %s
                                WHERE gamb_id = %s AND bet_time = %s;
                                """
                                cur.execute(update_amount_query, (new_amount, gamb_id, new_bet_time))
                                print(f"Bet amount updated to {new_amount}.")
                            elif modify_action == "c":
                                # Cancel bet
                                cancel_query = """
                                UPDATE GAMBLER_BETS
                                SET status = 'Cancelled'
                                WHERE gamb_id = %s AND bet_time = %s;
                                """
                                cur.execute(cancel_query, (gamb_id, bet_time_to_modify))
                                print(f"Bet with time {bet_time_to_modify} cancelled.")
                            else:
                                print("Invalid modification action.")
                        else:
                            print("Invalid bet selection.")
                    elif action == "a":
                        # Add new bet
                        which_side = input("Choose which side to bet on (Home/Away): ").strip().capitalize()
                        if which_side not in ["Home", "Away"]:
                            print("Invalid side choice.")
                            return

                        try:
                            amount = float(input("Enter the amount to bet: "))
                            if amount <= 0:
                                print("Invalid amount. It must be greater than 0.")
                                return
                        except ValueError:
                            print("Invalid amount. Please enter a numeric value.")
                            return

                        add_bet_query = """
                        INSERT INTO GAMBLER_BETS (bet_time, gamb_id, rec_id, which_side, amount, status)
                        VALUES (%s, %s, %s, %s, %s, %s);
                        """
                        new_bet_time = latest_modified.replace(hour=datetime.now().hour, minute=datetime.now().minute, second=datetime.now().second)
                        cur.execute(add_bet_query, (new_bet_time, gamb_id, rec_id, which_side, amount, "Pending"))
                        print(f"Bet successfully added at {new_bet_time}.")
                    else:
                        print("Invalid action. Exiting.")
                else:
                    # Add a new bet if no existing bets
                    which_side = input("Choose which side to bet on (Home/Away): ").strip().capitalize()
                    if which_side not in ["Home", "Away"]:
                        print("Invalid side choice.")
                        return

                    try:
                        amount = float(input("Enter the amount to bet: "))
                        if amount <= 0:
                            print("Invalid amount. It must be greater than 0.")
                            return
                    except ValueError:
                        print("Invalid amount. Please enter a numeric value.")
                        return

                    add_bet_query = """
                    INSERT INTO GAMBLER_BETS (bet_time, gamb_id, rec_id, which_side, amount, status)
                    VALUES (%s, %s, %s, %s, %s, %s);
                    """
                    new_bet_time = latest_modified.replace(hour=datetime.now().hour, minute=datetime.now().minute, second=datetime.now().second)
                    cur.execute(add_bet_query, (new_bet_time, gamb_id, rec_id, which_side, amount, "Pending"))
                    print(f"Bet successfully added at {new_bet_time}!")

                # Commit transaction
                conn.commit()

    except Exception as e:
        print(f"Error handling bet: {e}")
        conn.rollback()  # Rollback transaction in case of error
    finally:
        conn.close()

# Example usage
if __name__ == "__main__":
    handle_bet_transaction()
