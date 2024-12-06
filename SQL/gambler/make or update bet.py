import psycopg2
from datetime import datetime
from decimal import Decimal  # Import Decimal

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

    return new_id

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

                # Fetch gambler's balance
                balance_query = "SELECT balance FROM GAMBLER WHERE gambler_id = %s;"
                cur.execute(balance_query, (gamb_id,))
                result = cur.fetchone()
                if not result:
                    print("Invalid Gambler ID.")
                    return
                current_balance = result[0]

                # Fetch existing bets
                existing_bets_query = """
                SELECT bet_time, rec_id, which_side, amount
                FROM GAMBLER_BETS
                WHERE gamb_id = %s AND rec_id = %s AND status = 'Pending'
                ORDER BY bet_time DESC;
                """
                cur.execute(existing_bets_query, (gamb_id, rec_id))
                existing_bets = cur.fetchall()

                if existing_bets:
                    print("\nYour existing bets for this record:")
                    for idx, bet in enumerate(existing_bets, start=1):
                        print(f"{idx}. Bet Time: {bet[0]}, Side: {bet[2]}, Amount: {bet[3]}")

                    # Ask to add new bet or cancel an existing one
                    action = input("\nDo you want to add a new bet or cancel an existing one? (a/c): ").strip().lower()
                    if action == "c":
                        bet_idx = int(input("Enter the number of the bet you want to cancel: "))
                        if 1 <= bet_idx <= len(existing_bets):
                            bet_time_to_modify = existing_bets[bet_idx - 1][0]
                            bet_amount = existing_bets[bet_idx - 1][3]
                            cancel_query = """
                            UPDATE GAMBLER_BETS
                            SET status = 'Cancelled'
                            WHERE gamb_id = %s AND bet_time = %s;
                            """
                            cur.execute(cancel_query, (gamb_id, bet_time_to_modify))
                            print(f"Bet with time {bet_time_to_modify} cancelled.")

                            # Add back balance and add cashflow record
                            new_balance = current_balance + bet_amount
                            addback_balance_query = "UPDATE GAMBLER SET balance = %s WHERE gambler_id = %s;"
                            cur.execute(addback_balance_query, (new_balance, gamb_id))

                            # Generate new transaction ID
                            trans_id = generate_transaction_id(cur)

                            cashflow_query = """
                            INSERT INTO CASHFLOW_RECORD (trans_id, gamb_id, trans_type, cashflow, time)
                            VALUES (%s, %s, %s, %s, %s);
                            """
                            cur.execute(cashflow_query, (trans_id, gamb_id, "Bet Cancelled", bet_amount, datetime.now()))
                        else:
                            print("Invalid bet selection.")
                    elif action == "a":
                       # Add new bet
                        which_side = input("Choose which side to bet on (Home/Away): ").strip().capitalize()
                        if which_side not in ["Home", "Away"]:
                            print("Invalid side choice.")
                            return

                        # Determine the corresponding odd
                        if which_side == "Home":
                            selected_odd = Decimal(odd_1)
                        else:
                            selected_odd = Decimal(odd_2)

                        try:
                            amount = Decimal(input("Enter the amount to bet: "))
                            if amount <= 0:
                                print("Invalid amount. It must be greater than 0.")
                                return
                            if amount > current_balance:
                                print(f"Insufficient balance. Your current balance is {current_balance}.")
                                return
                        except ValueError:
                            print("Invalid amount. Please enter a numeric value.")
                            return

                        # Deduct balance and add cashflow record
                        new_balance = current_balance - amount
                        deduct_balance_query = "UPDATE GAMBLER SET balance = %s WHERE gambler_id = %s;"
                        cur.execute(deduct_balance_query, (new_balance, gamb_id))

                        # Generate new transaction ID
                        trans_id = generate_transaction_id(cur)

                        cashflow_query = """
                        INSERT INTO CASHFLOW_RECORD (trans_id, gamb_id, trans_type, cashflow, time)
                        VALUES (%s, %s, %s, %s, %s);
                        """
                        cur.execute(cashflow_query, (trans_id, gamb_id, "Bet", -amount, datetime.now()))

                        add_bet_query = """
                        INSERT INTO GAMBLER_BETS (bet_time, gamb_id, rec_id, which_side, odd, amount, status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s);
                        """
                        new_bet_time = latest_modified.replace(hour=datetime.now().hour, minute=datetime.now().minute, second=datetime.now().second)
                        cur.execute(add_bet_query, (new_bet_time, gamb_id, rec_id, which_side, selected_odd, amount, "Pending"))
                        print(f"Bet successfully added at {new_bet_time}.")
                        print(f"Transaction ID: {trans_id}")
                        print(f"Selected Odd: {selected_odd}")
                        print(f"New balance: {new_balance}")
                    else:
                        print("Invalid action. Exiting.")
                else:
                    # Add new bet
                    which_side = input("Choose which side to bet on (Home/Away): ").strip().capitalize()
                    if which_side not in ["Home", "Away"]:
                        print("Invalid side choice.")
                        return

                    # Determine the corresponding odd
                    if which_side == "Home":
                        selected_odd = Decimal(odd_1)
                    else:
                        selected_odd = Decimal(odd_2)

                    try:
                        amount = Decimal(input("Enter the amount to bet: "))
                        if amount <= 0:
                            print("Invalid amount. It must be greater than 0.")
                            return
                        if amount > current_balance:
                            print(f"Insufficient balance. Your current balance is {current_balance}.")
                            return
                    except ValueError:
                            print("Invalid amount. Please enter a numeric value.")
                            return

                        # Deduct balance and add cashflow record
                    new_balance = current_balance - amount
                    deduct_balance_query = "UPDATE GAMBLER SET balance = %s WHERE gambler_id = %s;"
                    cur.execute(deduct_balance_query, (new_balance, gamb_id))
                    # Generate new transaction ID
                    trans_id = generate_transaction_id(cur)

                    cashflow_query = """
                    INSERT INTO CASHFLOW_RECORD (trans_id, gamb_id, trans_type, cashflow, time)
                    VALUES (%s, %s, %s, %s, %s);
                    """
                    cur.execute(cashflow_query, (trans_id, gamb_id, "Bet", -amount, datetime.now()))
                    add_bet_query = """
                    INSERT INTO GAMBLER_BETS (bet_time, gamb_id, rec_id, which_side, odd, amount, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """
                    new_bet_time = latest_modified.replace(hour=datetime.now().hour, minute=datetime.now().minute, second=datetime.now().second)
                    cur.execute(add_bet_query, (new_bet_time, gamb_id, rec_id, which_side, selected_odd, amount, "Pending"))
                    print(f"Bet successfully added at {new_bet_time}.")
                    print(f"Transaction ID: {trans_id}")
                    print(f"Selected Odd: {selected_odd}")
                    print(f"New balance: {new_balance}")
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
