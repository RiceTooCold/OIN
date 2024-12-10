from util import make_the_choise
from ..Action import Action
from ..util import *
from .query_game import query_game  

BUFFER_SIZE = 4096

# Function to fetch games by date with conditional score display and stadium name
class fetch_games_by_date(Action):
    def fetch_games(self, conn, db, cur, user):

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
            choises = []
            if results:
                response = f"Games on {date}:\n\n"
                counter = 1
                for row in results:
                    game_id, game_date, home_team, away_team, stadium_name, home_score, away_score, status = row
                    choises.append(game_id)
                    response += f"Number: {counter}\n"
                    response += f"GameId: {game_id}\n"
                    response += f"Date: {game_date}\n"
                    response += f"Stadium: {stadium_name}\n"
                    response += f"Home Team: {home_team} vs Away Team: {away_team}\n"
                    response += f"Status: {status}\n"
                    if status != 'Not yet started':
                        response += f"Score: {home_team} {home_score} - {away_score} {away_team}\n"
                    response += "-" * 40 + "\n"
                    counter += 1
                conn.sendall(("[TABLE]" + '\n' + response + '\n' + "[END]").encode('utf-8'))
                return choises
            else:
                conn.send(f"No games found on {date}.\n".encode('utf-8'))
                return None
        except Exception as e:
            conn.send(f"Error fetching games: {e}\n".encode('utf-8'))
    
    
    def see_game_details(self, choises, conn, db, cur):
        conn.send("\n[GET]Which game would you like to look at (please enter number or 0 to exit) : ".encode('utf-8'))
         
        option_idx = [x for x in range(1, len(choises)+1)]
    
        recv_msg = conn.recv(BUFFER_SIZE).decode('utf-8')
        
        while int(recv_msg) not in option_idx:
            if int(recv_msg) == 0:
                break
            msg = "[GET]Wrong input, please select "
            for idx in option_idx:
                msg = msg + f'{idx}. '
            msg += ': '
            conn.send(msg.encode('utf-8'))
            recv_msg = conn.recv(BUFFER_SIZE).decode("utf-8")
            
            
        game_id = choises[int(recv_msg)-1]
        
        func = query_game("game")
        func.fetch_game_details(game_id, conn, db, cur)
        
    def exec(self, conn, db, cur, user):
        choises = self.fetch_games(conn, db, cur, user)
        print(choises)
        print(1)
        if choises is not None:
            print(2)
            self.see_game_details(choises, conn, db, cur)
# Example usage
if __name__ == "__main__":
    choise = fetch_games_by_date()
    
