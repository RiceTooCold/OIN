from ..Action import Action
from ..util import *


# Function to fetch games by date with conditional score display and stadium name
class fetch_games_by_date(Action):
    def exec(self, conn, db, cur, user):

        conn.send("\n[GET]Enter the date (YYYY-MM-DD) to search for games: ".encode('utf-8'))
        date = conn.recv(1024).decode('utf-8').strip()
        
        query = """
        SELECT 
            g.game_id,
            g.game_date,
            t1.name AS home_team,
            t2.name AS away_team,
            s.s_name AS stadium_name,
            CASE 
                WHEN g.status = 'Not yet started' THEN NULL
                ELSE g.home_score 
            END AS home_score,
            CASE 
                WHEN g.status = 'Not yet started' THEN NULL
                ELSE g.away_score 
            END AS away_score,
            g.status
        FROM GAME g
        LEFT JOIN TEAM t1 ON g.home_team_id = t1.team_id
        LEFT JOIN TEAM t2 ON g.away_team_id = t2.team_id
        LEFT JOIN STADIUM s ON g.stadium_id = s.stadium_id
        WHERE g.game_date = %s;
        """
        try:
            cur.execute(query, (date,))
            results = cur.fetchall()
            # print(results)
            if results:
                response = f"Games on {date}:\n\n"
                for row in results:
                    game_id, game_date, home_team, away_team, stadium_name, home_score, away_score, status = row
                    response += f"GameId: {game_id}\n"
                    response += f"Date: {game_date}\n"
                    response += f"Stadium: {stadium_name}\n"
                    response += f"Home Team: {home_team} vs Away Team: {away_team}\n"
                    response += f"Status: {status}\n"
                    if status != 'Not yet started':
                        response += f"Score: {home_team} {home_score} - {away_score} {away_team}\n"
                    response += "-" * 40 + "\n"
                conn.sendall(("[TABLE]" + '\n' + response + '\n' + "[END]").encode('utf-8'))
            else:
                conn.send(f"No games found on {date}.\n".encode('utf-8'))
        except Exception as e:
            conn.send(f"Error fetching games: {e}\n".encode('utf-8'))
        finally:
            return None

# Example usage
if __name__ == "__main__":
    fetch_games_by_date()
