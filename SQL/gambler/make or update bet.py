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

# Function to fetch record odds
def fetch_record_odds(rec_id):
    query = """
    SELECT 
        record_id, odd_1, odd_2, latest_modified
    FROM BETS_ODD_RECORD
    WHERE record_id = %s;
    """
    conn = connect_db()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(query, (rec_id,))
                record = cur.fetchone()
                if not record:
                    print(f"No record found with ID: {rec_id}")
                    return None
                return record
        except Exception as e:
            print(f"Error fetching record odds: {e}")
            return None
        finally:
            conn.close()
    return None

# Function to fetch non-completed gambler bets for a record
def fetch_gambler_bets(gamb_id, rec_id):
    query = """
    SELECT bet_time, rec_id, which_side, amount, status
    FROM GAMBLER_BETS
    WHERE gamb_id = %s AND rec_id = %s AND status != 'Completed'
    ORDER BY bet_time DESC;
    """
    conn = connect_db()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(query, (gamb_id, rec_id))
                bets = cur.fetchall()
                return bets
        except Exception as e:
            print(f"Error fetching gambler bets: {e}")
            return []
        finally:
            conn.close()
    return []

# Function to cancel a bet
def cancel_gambler_bet(gamb_id, bet_time):
    query = """
    UPDATE GAMBLER_BETS
    SET status = 'Cancelled'
    WHERE gamb_id = %s AND bet_time = %s;
    """
    conn = connect_db()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(query, (gamb_id, bet_time))
                conn.commit()
                print(f"Bet with time {bet_time} successfully cancelled.")
        except Exception as e:
            print(f"Error cancelling bet: {e}")
        finally:
            conn.close()

# Function to modify a bet
def modify_gambler_bet(gamb_id, bet_time, field, value):
    query = f"""
    UPDATE GAMBLER_BETS
    SET {field} = %s
    WHERE gamb_id = %s AND bet_time = %s;
    """
    conn = connect_db()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(query, (value, gamb_id, bet_time))
                conn.commit()
                print(f"Bet with time {bet_time} successfully updated.")
        except Exception as e:
            print(f"Error modifying bet: {e}")
        finally:
            conn.close()

# Function to add a new bet
def add_new_bet(gamb_id, rec_id, which_side, amount, latest_modified):
    conn = connect_db()
    if conn:
        try:
            query = """
            INSERT INTO GAMBLER_BETS (bet_time, gamb_id, rec_id, which_side, amount, status)
            VALUES (%s, %s, %s, %s, %s, %s);
            """
            bet_time = latest_modified.replace(hour=datetime.now().hour, minute=datetime.now().minute, second=datetime.now().second)
            status = "Pending"  # Default status for a new bet
            with conn.cursor() as cur:
                cur.execute(query, (bet_time, gamb_id, rec_id, which_side, amount, status))
                conn.commit()
                print(f"Bet successfully placed at {bet_time}!")
        except Exception as e:
            print(f"Error adding new bet: {e}")
        finally:
            conn.close()

# Main function to handle bets
def handle_bet():
    conn = connect_db()
    if not conn:
        return

    try:
        # Input for the gambler bet
        gamb_id = input("Enter your Gambler ID: ").strip()
        rec_id = input("Enter the Record ID: ").strip()

        # Fetch odds for the selected record
        record = fetch_record_odds(rec_id)
        if not record:
            print("Invalid Record ID.")
            return
        _, odd_1, odd_2, latest_modified = record
        print(f"   Odds: Home ({odd_1}), Away ({odd_2})")

        # Check if gambler already has bets on this record
        existing_bets = fetch_gambler_bets(gamb_id, rec_id)
        if existing_bets:
            print("\nYour existing bets for this record:")
            for idx, bet in enumerate(existing_bets, start=1):
                print(f"{idx}. Bet Time: {bet[0]}, Side: {bet[2]}, Amount: {bet[3]}, Status: {bet[4]}")

            # Ask to add new bet or modify existing one
            action = input("\nDo you want to add a new bet or update an existing one? (a/u): ").strip().lower()
            if action == "u":
                bet_idx = int(input("Enter the number of the bet you want to update: "))
                if 1 <= bet_idx <= len(existing_bets):
                    bet_time_to_modify = existing_bets[bet_idx - 1][0]
                    modify_action = input("Do you want to modify or cancel? (m/c): ").strip().lower()
                    
                    if modify_action == "m":
                        new_side = input("Enter the new side (Home/Away): ").strip().capitalize()
                        if new_side in ["Home", "Away"]:
                            modify_gambler_bet(gamb_id, bet_time_to_modify, "which_side", new_side)
                            new_amount = float(input("Enter the new amount: "))
                            modify_gambler_bet(gamb_id, bet_time_to_modify, "amount", new_amount)
                        else:
                            print("Invalid side choice.")       
                    elif modify_action == "c":
                        cancel_gambler_bet(gamb_id, bet_time_to_modify)
                    else:
                        print("Invalid modification action.")
                else:
                    print("Invalid bet selection.")
            elif action == "a":
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

                add_new_bet(gamb_id, rec_id, which_side, amount, latest_modified)
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

            add_new_bet(gamb_id, rec_id, which_side, amount, latest_modified)

    except Exception as e:
        print(f"Error handling bet: {e}")
    finally:
        conn.close()

# Example usage
if __name__ == "__main__":
    handle_bet()
