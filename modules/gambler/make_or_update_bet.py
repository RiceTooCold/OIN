from datetime import datetime
from decimal import Decimal  # Import Decimal
from ..Action import Action
from ..util import *


# Main function to handle bets
class handle_bet_transaction(Action):
    
    def next_three_day_gameRec(self, db, cur):
        query = """
        SELECT record_id, odd_1, odd_2, latest_modified, status
        FROM BET_ODDS_RECORD
        WHERE status = %s;
        """
        status = "Processing"
        cur.execute(query, (status,))
        result = cur.fetchall()
        data = None
        if result:
            data = print_table(result, cur, None)
        return data
    # Generate a new transaction ID based on the table's current max ID
    def generate_transaction_id(self, cur):
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

    def exec(self, conn, db, cur, user):
        try:
            # Input for the gambler bet
            conn.send("\n---Start make or update your own bets---\n\n".encode('utf-8'))
            gamb_id = user.get_userid()
            # 把近三天的比賽都列出來
            conn.send("Recent three day game".encode('utf-8'))
            game_table = self.next_three_day_gameRec(db, cur)
            
            conn.sendall(("[TABLE]" + '\n' + game_table + '\n' + "[END]").encode('utf-8'))
            
            while True:
                conn.send("[GET]Enter the Record ID: ".encode('utf-8'))
                rec_id = conn.recv(1024).decode('utf-8').strip()

                # Fetch odds for the selected record
                record_query = """
                SELECT record_id, odd_1, odd_2, latest_modified, status
                FROM BET_ODDS_RECORD
                WHERE record_id = %s;
                """
                cur.execute(record_query, (rec_id,))
                record = cur.fetchone()

                if not record:
                    conn.send("Invalid Record ID.\n".encode('utf-8'))
                    return

                _, odd_1, odd_2, latest_modified, status = record

                # Check if the record is expired
                if status == "Expired":
                    conn.send("This record has expired. You cannot place a bet on it. Please try again\n".encode('utf-8'))
                    return
                else:
                    break

            # conn.sendall(f"   Odds: Home ({odd_1}), Away ({odd_2})\n".encode('utf-8'))

            # Fetch gambler's balance
            balance_query = "SELECT balance FROM GAMBLER WHERE gambler_id = %s;"
            cur.execute(balance_query, (gamb_id,))
            result = cur.fetchone()
            if not result:
                conn.send("Invalid Gambler ID.\n".encode('utf-8'))
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
            print(existing_bets)
            bet_exist_or_not = 1 if existing_bets else 0

            action = "a"

            if bet_exist_or_not:
                conn.sendall("\nYour existing bets for this record:\n".encode('utf-8'))
                # conn.send("[TABLE]\n".encode('utf-8'))

                for idx, bet in enumerate(existing_bets, start=1):
                    conn.sendall(f"{idx}. Bet Time: {bet[0]}, Side: {bet[2]}, Amount: {bet[3]}\n".encode('utf-8'))

                # conn.send("[END]\n".encode('utf-8'))

                # Ask to add new bet or cancel an existing one
                conn.send("\n[GET]Do you want to add a new bet or cancel an existing one? (a/c): ".encode('utf-8'))
                action = conn.recv(1024).decode('utf-8').strip().lower()
                if action == "c":
                    conn.send("[GET]Enter the number of the bet you want to cancel: ".encode('utf-8'))
                    bet_idx = int(conn.recv(1024).decode('utf-8').strip())
                    if 1 <= bet_idx <= len(existing_bets):
                        bet_time_to_modify = existing_bets[bet_idx - 1][0]
                        bet_amount = existing_bets[bet_idx - 1][3]
                        cancel_query = """
                        UPDATE GAMBLER_BETS
                        SET status = 'Cancelled'
                        WHERE gamb_id = %s AND bet_time = %s;
                        """
                        
                        cur.execute(cancel_query, (gamb_id, bet_time_to_modify))
                        conn.send(f"Bet with time {bet_time_to_modify} cancelled.\n".encode('utf-8'))
                        
                        
                        # Add back balance and add cashflow record
                        new_balance = current_balance + bet_amount
                        addback_balance_query = "UPDATE GAMBLER SET balance = %s WHERE gambler_id = %s;"
                        cur.execute(addback_balance_query, (new_balance, gamb_id))
                        
                        
                        # Generate new transaction ID
                        trans_id = self.generate_transaction_id(cur)
                        cashflow_query = """
                        INSERT INTO CASHFLOW_RECORD (trans_id, gamb_id, trans_type, cashflow, time)
                        VALUES (%s, %s, %s, %s, %s);
                        """
                        cur.execute(cashflow_query, (trans_id, gamb_id, "Bet Cancelled", bet_amount, datetime.now()))
                    else:
                        conn.send("Invalid bet selection.\n".encode('utf-8'))
                elif action != "a":
                    conn.send("Invalid action. Exiting.\n".encode('utf-8'))
                    return

            if bet_exist_or_not == 0 or action == "a":
                # Add new bet
                while True:
                    conn.send("[GET]Choose which side to bet on (Home/Away): ".encode('utf-8'))
                    which_side = conn.recv(1024).decode('utf-8').strip().capitalize()
                    if which_side not in ["Home", "Away"]:
                        conn.send("Invalid side choice.\n".encode('utf-8'))
                    else:
                        break

                # Determine the corresponding odd
                selected_odd = Decimal(odd_1) if which_side == "Home" else Decimal(odd_2)

                while True:
                    conn.send("[GET]Enter the amount to bet: ".encode('utf-8'))
                    try:
                        amount = Decimal(conn.recv(1024).decode('utf-8').strip())
                        if amount <= 0:
                            conn.send("Invalid amount. It must be greater than 0.\n".encode('utf-8'))
                        elif amount > current_balance:
                            conn.send(f"Insufficient balance. Your current balance is {current_balance}.\n".encode('utf-8'))
                        else:
                            break
                    except ValueError:
                        conn.send("Invalid amount. Please enter a numeric value.\n".encode('utf-8'))

                # Deduct balance and add cashflow record
                new_balance = current_balance - amount
                deduct_balance_query = "UPDATE GAMBLER SET balance = %s WHERE gambler_id = %s;"
                cur.execute(deduct_balance_query, (new_balance, gamb_id))

                # Generate new transaction ID
                trans_id = self.generate_transaction_id(cur)

                cashflow_query = """
                INSERT INTO CASHFLOW_RECORD (trans_id, gamb_id, trans_type, cashflow, time)
                VALUES (%s, %s, %s, %s, %s);
                """
                cur.execute(cashflow_query, (trans_id, gamb_id, "Bet", -amount, datetime.now()))

                add_bet_query = """
                INSERT INTO GAMBLER_BETS (bet_time, gamb_id, rec_id, which_side, odd, amount, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
                """
                new_bet_time = latest_modified.replace(
                    hour=datetime.now().hour, minute=datetime.now().minute, second=datetime.now().second)
                cur.execute(add_bet_query, (new_bet_time, gamb_id, rec_id, which_side, selected_odd, amount, "Pending"))
                conn.sendall(f"\nBet successfully added at {new_bet_time}.\n".encode('utf-8'))
                conn.sendall(f"-------------\nTransaction ID: {trans_id}\nSelected Odd: {selected_odd}\nNew balance: {new_balance}\n-------------\n\n".encode('utf-8'))

            # Commit transaction
            db.commit()

        except Exception as e:
            conn.send(f"Error handling bet: {e}\n".encode('utf-8'))
            conn.rollback()  # Rollback transaction in case of error
        finally:
            return None

# Example usage
if __name__ == "__main__":
    handle_bet_transaction()
