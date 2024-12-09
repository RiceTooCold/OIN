import psycopg2
import pandas as pd
from ..Action import Action
from ..util import *

# Function to fetch top gamblers by ROI
class fetch_top_gamblers_by_roi(Action):
    def exec(self, conn, db, cur, user):
        try:
            # Query to calculate ROI for each gambler
            roi_query = """
                SELECT 
                gb.gambler_id,
                gb.gam_name,
                COALESCE(SUM(CASE WHEN gbb.status = 'Completed' THEN gbb.amount ELSE 0 END), 0) AS total_bet,
                COALESCE(SUM(CASE 
                    WHEN gbb.status = 'Completed' AND g.home_win = 'W' AND gbb.which_side = 'Home' THEN gbb.amount * gbb.odd
                    WHEN gbb.status = 'Completed' AND g.home_win = 'L' AND gbb.which_side = 'Away' THEN gbb.amount * gbb.odd
                    ELSE 0 END), 0) AS total_earn,
                CASE 
                    WHEN SUM(CASE WHEN gbb.status = 'Completed' THEN gbb.amount ELSE 0 END) > 0 THEN
                        (SUM(CASE 
                            WHEN gbb.status = 'Completed' AND g.home_win = 'W' AND gbb.which_side = 'Home' THEN gbb.amount * gbb.odd
                            WHEN gbb.status = 'Completed' AND g.home_win = 'L' AND gbb.which_side = 'Away' THEN gbb.amount * gbb.odd
                            ELSE 0 END) / 
                        SUM(CASE WHEN gbb.status = 'Completed' THEN gbb.amount ELSE 0 END)) * 100
                    ELSE 0
                END AS roi
                FROM GAMBLER gb
                LEFT JOIN GAMBLER_BETS gbb ON gb.gambler_id = gbb.gamb_id
                LEFT JOIN BET_ODDS_RECORD bor ON gbb.rec_id = bor.record_id
                LEFT JOIN GAME g ON bor.game_id = g.game_id
                GROUP BY gb.gambler_id, gb.gam_name
                ORDER BY roi DESC
                LIMIT 5;
                """
            cur.execute(roi_query)
            top_gamblers = cur.fetchall()
            if top_gamblers:
                # Convert to DataFrame for better visualization
                columns = ["Gambler ID", "Gambler Name", "Total Bet Amount", "Total Earned", "ROI (%)"]
                # top_gamblers_df = pd.DataFrame(top_gamblers, columns=columns)

                # Prepare data for sending
                table_output = print_table(top_gamblers, cur, columns)
                # Send result to the client
                conn.sendall("\nTop 5 Gamblers by ROI:\n".encode('utf-8'))
                # conn.sendall(("[TABLE]" + '\n' + table_output + '\n' + "[END]").encode('utf-8'))
                conn.sendall((table_output + '\n\n').encode('utf-8'))  
                
            else:
                conn.sendall("No completed bets found to calculate ROI.\n".encode('utf-8'))

        except Exception as e:
            error_message = f"Error fetching top gamblers by ROI: {e}\n"
            conn.sendall(error_message.encode('utf-8'))


# # Example usage
# if __name__ == "__main__":
#     fetch_top_gamblers_by_roi()
