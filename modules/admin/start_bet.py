from datetime import datetime
from ..Action import Action
from ..util import *


# Function to open new bets for a specific game and allow setting odds
class open_new_bets_with_odds(Action):
    def exec(self, conn, db, cur, user):
        try:
            # Fetch existing bet odds for the game
            conn.send("\n[GET]Enter the Game ID to open new bets: ".encode('utf-8'))
            game_id = conn.recv(1024).decode('utf-8').strip()

            fetch_odds_query = """
            SELECT record_id, type_id, odd_1, odd_2, status
            FROM BET_ODDS_RECORD
            WHERE game_id = %s AND status = 'Not yet started'
            """
            cur.execute(fetch_odds_query, (game_id,))
            bet_records = cur.fetchall()

            if not bet_records:
                conn.send(f"No bet records found with status 'Not yet started' for Game ID: {game_id}.\n".encode('utf-8'))
                return

            conn.send(f"Found {len(bet_records)} bet record(s) for Game ID {game_id} ready to open:\n".encode('utf-8'))

            # Allow admin to set odds for each bet record
            for record in bet_records:
                record_id, type_id, old_odd_1, old_odd_2, status = record
                conn.send(f"\nRecord ID: {record_id}, Type ID: {type_id}, Status: {status}\n".encode('utf-8'))

                # Input new odds
                try:
                    conn.send(f"[GET]Enter new Odd 1 (Home) for Record ID {record_id}: ".encode('utf-8'))
                    new_odd_1 = float(conn.recv(1024).decode('utf-8').strip())

                    conn.send(f"[GET]Enter new Odd 2 (Away) for Record ID {record_id}: ".encode('utf-8'))
                    new_odd_2 = float(conn.recv(1024).decode('utf-8').strip())

                    if new_odd_1 <= 0 or new_odd_2 <= 0:
                        conn.send("Odds must be positive numbers.\n".encode('utf-8'))
                        return
                except ValueError:
                    conn.send("Invalid input for odds. Please enter numeric values.\n".encode('utf-8'))
                    return

                # Update bet record with new odds and status
                update_odds_query = """
                UPDATE BET_ODDS_RECORD
                SET odd_1 = %s, odd_2 = %s, status = 'Processing', latest_modified = %s
                WHERE record_id = %s;
                """
                cur.execute(update_odds_query, (new_odd_1, new_odd_2, datetime.now(), record_id))
                conn.send(f"\n!!\nUpdated Record ID {record_id} with new Odds: Home ({new_odd_1}), Away ({new_odd_2}).\n".encode('utf-8'))

            # Commit transaction
            db.commit()
            conn.send(f"Successfully opened new bets for Game ID {game_id}.\n\n".encode('utf-8'))

        except Exception as e:
            conn.send(f"Error opening new bets: {e}\n".encode('utf-8'))
            conn.rollback()


# # Example usage
# if __name__ == "__main__":
#     try:
#         game_id = input("Enter the Game ID to open new bets: ").strip()
#         open_new_bets_with_odds(game_id)
#     except ValueError:
#         print("Invalid Game ID. Please enter a valid ID.")
