from ..Action import Action
from ..util import *


# Function to fetch team performance for a specific season from GAME table
class query_standing(Action):

    def fetch_season_performance(self, season_id, conn, db, cur, user):
        query = """
        SELECT 
            t.name AS team_name,
            COUNT(*) AS total_games,
            SUM(CASE WHEN g.home_team_id = t.team_id AND g.home_win = 'W' THEN 1 
                    WHEN g.away_team_id = t.team_id AND g.home_win = 'L' THEN 1 
                    ELSE 0 END) AS wins,
            SUM(CASE WHEN g.home_team_id = t.team_id AND g.home_win = 'L' THEN 1 
                    WHEN g.away_team_id = t.team_id AND g.home_win = 'W' THEN 1 
                    ELSE 0 END) AS losses,
            ROUND((CAST(SUM(CASE WHEN g.home_team_id = t.team_id AND g.home_win = 'W' THEN 1 
                                WHEN g.away_team_id = t.team_id AND g.home_win = 'L' THEN 1 
                                ELSE 0 END) AS NUMERIC) 
                / COUNT(*)) * 100, 2) AS win_rate
        FROM TEAM t
        LEFT JOIN GAME g 
            ON g.status = 'Ended'
        AND (g.home_team_id = t.team_id OR g.away_team_id = t.team_id)
        AND g.season_id = %s
        GROUP BY t.name
        ORDER BY win_rate DESC, wins DESC, losses ASC;
        """
        try:
            # Execute query
            cur.execute(query, (season_id,))
            results = cur.fetchall()

            if not results:
                conn.sendall(f"No data found for the season {season_id}.\n".encode('utf-8'))
                return

            # Convert results to DataFrame
            columns = ["Team Name", "Total Games", "Wins", "Losses", "Win Rate (%)"]

            ranked_rows = [(rank + 1, *row) for rank, row in enumerate(results)]
            columns = ["Rank"] + columns
            data_table = print_table(ranked_rows, cur, columns)
            
            conn.sendall(f"\nTeam Performance for Season ({season_id}):\n".encode('utf-8'))
            # conn.sendall(("[TABLE]" + '\n' + data_table + '\n' + "[END]").encode('utf-8'))
            conn.sendall(data_table.encode('utf-8'))
            return data_table

        except Exception as e:
            conn.sendall(f"Error fetching current regular season performance: {e}\n".encode('utf-8'))

    def exec(self, conn, db, cur, user):

        current_season_id = 22022
        self.fetch_season_performance(current_season_id, conn, db, cur, user)

        while True:
            conn.send("\n[GET]Do you want to see performance for another regular season? (yes/no): ".encode('utf-8'))
            see_other_season = conn.recv(1024).decode('utf-8').strip().lower()
            if see_other_season == "yes":
                conn.send("[GET]Enter the season year (2013-2021): ".encode('utf-8'))
                try:
                    season_id = int(conn.recv(1024).decode('utf-8').strip()) + 20000
                    self.fetch_season_performance(season_id, conn, db, cur, user)
                except ValueError:
                    conn.send("Invalid input. Please enter a numeric season year.\n".encode('utf-8'))
            elif see_other_season == "no":
                conn.send("Exiting.\n\n".encode('utf-8'))
                break
            else:
                conn.send("Invalid input. Please type 'yes' or 'no'.\n".encode('utf-8'))

    
            