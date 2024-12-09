from ..Action import Action
from ..util import *


# Function to fetch user details without showing the password
class fetch_gambler_details(Action):
    def exec(self, conn, db, cur, user):
        # Send prompt to the client for gambler ID
        separator = "-" * 40 + "\n"

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
        try:
            # Fetch gambler details
            while True:
                conn.send("[GET]Enter the gambler ID to fetch details: ".encode('utf-8'))
                gambler_id = conn.recv(1024).decode('utf-8').strip()
                cur.execute(gambler_query, (gambler_id,))
                gambler_details = cur.fetchone()
                if gambler_details:
                    break
                else:
                    conn.sendall("No gambler found with the given ID. Please try again!\n".encode('utf-8'))
            # Send gambler details to the client
            gambler_info = (
                separator + 
                f"User Details:\n"
                f"Gambler ID: {gambler_details[0]}\n"
                f"Name: {gambler_details[1]}\n"
                f"Email: {gambler_details[2]}\n"
                f"Join Date: {gambler_details[3]}\n"
                f"Balance: {gambler_details[4]}\n"
                + separator + 
                "Last 10 Bets:\n\n"
            )
            conn.sendall(gambler_info.encode('utf-8'))

            # Fetch total bet amount
            cur.execute(total_amount_query, (gambler_id,))
            total_amount = cur.fetchone()[0]

            # Fetch last 10 bets with results
            cur.execute(bets_query, (gambler_id,))
            bets = cur.fetchall()
            if bets:

                columns = ["Bet Time", "Record ID", "Side", "Amount", "Status", "Result"]
                # bets_df = pd.DataFrame(bets, columns=columns)

                # bets_str = bets_df.to_string(index=False)
                bets_data = print_table(bets, cur, columns)
                conn.sendall(bets_data.encode('utf-8'))

                # Send total amount of all bets
                conn.sendall(f"\nTotal Amount of All Bets: {total_amount}\n\n".encode('utf-8'))
            else:
                conn.sendall("No bets found for this gambler.\n".encode('utf-8'))
        except Exception as e:
            conn.sendall(f"Error fetching gambler details: {e}\n".encode('utf-8'))
        finally:
            return None



# # Example usage
# if __name__ == "__main__":
#     gambler_id = input("Enter the gambler ID to fetch details: ")
#     print("-" * 40)
#     fetch_gambler_details(gambler_id)
