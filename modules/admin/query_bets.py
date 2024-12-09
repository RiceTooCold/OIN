from datetime import datetime
from ..Action import Action
from ..util import *

# Function to fetch all bets for a specific date
class fetch_bets_by_date(Action):
    def exec(self, conn, db, cur, user):
        try:
            while True:
                try:
                    conn.send("\n[GET]Enter the date to fetch bets (YYYY-MM-DD): ".encode('utf-8'))
                    bet_date = conn.recv(1024).decode('utf-8').strip()
                    datetime.strptime(bet_date, "%Y-%m-%d")  # Validate date format
                    break
                except ValueError:
                    conn.send("Invalid date format. Please enter a date in YYYY-MM-DD format.\n".encode('utf-8'))

            # Fetch all bets for the given date
            print(bet_date)
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
                ELSE -gb.amount
            END AS winnings
            FROM GAMBLER_BETS gb
            JOIN BET_ODDS_RECORD bor ON gb.rec_id = bor.record_id
            JOIN GAME g ON bor.game_id = g.game_id
            WHERE DATE(g.game_date) = %s AND gb.status = 'Completed'
            ORDER BY winnings DESC;
            """
            cur.execute(bets_query, (bet_date,))
            bets = cur.fetchall()
            # Check if bets exist
            if not bets:
                conn.send(f"No bets found for the date {bet_date}.\n\n".encode('utf-8'))
                return

            # Create a DataFrame for better visualization
            columns = [
                "Bet Time", "Gambler ID", "Record ID", "Which Side", "Odd",
                "Amount", "Result", "Winnings"
            ]
            # bets_df = pd.DataFrame(bets, columns=columns)
            bets_data = print_table(bets, cur, columns)
            # Convert DataFrame to string for sending
            conn.send(f"\nBets for Date: {bet_date}\n".encode('utf-8'))
            conn.sendall(("[TABLE]" + '\n' + bets_data + '\n\n' + "[END]").encode('utf-8'))

        except Exception as e:
            conn.send(f"Error fetching bets: {e}\n".encode('utf-8'))
        finally:
            return None


# # Example usage
# if __name__ == "__main__":
#     try:
#         bet_date = input("Enter the date to fetch bets (YYYY-MM-DD): ").strip()
#         datetime.strptime(bet_date, "%Y-%m-%d")  # Validate date format
#         fetch_bets_by_date(bet_date)
#     except ValueError:
#         print("Invalid date format. Please enter a date in YYYY-MM-DD format.")
