from datetime import datetime
from decimal import Decimal
from ..Action import Action
from ..util import *


# Function to settle a single game by game_id
class settle_game(Action):
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
        else:
            # Start from the first ID if table is empty
            new_id = "T000000001"

        return new_id

    def exec(self, conn, db, cur, user):
        try:
            conn.send("\n[GET]Enter the Game ID to settle: ".encode('utf-8'))
            game_id = conn.recv(1024).decode('utf-8').strip()

            # Fetch match details
            game_query = """
            SELECT game_id, home_score, away_score, home_win, status
            FROM GAME
            WHERE game_id = %s;
            """
            cur.execute(game_query, (game_id,))
            game = cur.fetchone()

            if not game:
                conn.send("Invalid Game ID.\n".encode('utf-8'))
                return

            game_id, home_score, away_score, home_win, status = game

            # Ensure the game is Ongoing before settlement
            if status != "Ended":
                conn.send(f"Game ID {game_id} is not ended. Current status: {status}\n".encode('utf-8'))
                return

            # Update BET_ODDS_RECORD to Expire
            update_bet_records_query = """
            UPDATE BET_ODDS_RECORD
            SET status = 'Expired'
            WHERE game_id = %s AND status = 'Processing';
            """
            cur.execute(update_bet_records_query, (game_id,))

            # Fetch bets for the match
            bets_query = """
            SELECT b.gamb_id, b.rec_id, b.which_side, b.odd, b.amount
            FROM GAMBLER_BETS b
            JOIN BET_ODDS_RECORD r ON b.rec_id = r.record_id
            WHERE r.game_id = %s AND b.status = 'Pending';
            """
            cur.execute(bets_query, (game_id,))
            bets = cur.fetchall()

            if not bets:
                conn.send(f"No bets to settle for Game ID: {game_id}\n".encode('utf-8'))
             
            else:

                for gamb_id, rec_id, which_side, odd, amount in bets:

                    is_winner = (which_side == "Home" and home_win == 'W') or (which_side == "Away" and home_win == 'L')
                    winnings = Decimal(0)

                    if is_winner:
                        
                        # Calculate earned
                        winnings = Decimal(amount) * Decimal(odd)

                        # Update gambler balance
                        update_balance_query = "UPDATE GAMBLER SET balance = balance + %s WHERE gambler_id = %s;"
                        cur.execute(update_balance_query, (winnings, gamb_id))

                        # Add cashflow record
                        trans_id = self.generate_transaction_id(cur)
                        cashflow_query = """
                        INSERT INTO CASHFLOW_RECORD (trans_id, gamb_id, trans_type, cashflow, time)
                        VALUES (%s, %s, %s, %s, %s);
                        """
                        cur.execute(cashflow_query, (trans_id, gamb_id, "Earn", winnings, datetime.now()))
                        conn.send(f"Bet won by Gambler {gamb_id}. Winnings: {winnings}. Transaction ID: {trans_id}\n".encode('utf-8'))

                    # Update bet status to 'Completed'
                    update_bet_status_query = """
                    UPDATE GAMBLER_BETS SET status = 'Completed' WHERE gamb_id = %s AND rec_id = %s;
                    """
                    cur.execute(update_bet_status_query, (gamb_id, rec_id))

            db.commit()
            conn.send(f"Settlement completed for Game ID {game_id}.\n\n".encode('utf-8'))

        except Exception as e:
            conn.send(f"Error settling game: {e}\n".encode('utf-8'))
            db.rollback()