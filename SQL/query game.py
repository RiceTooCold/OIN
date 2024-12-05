import psycopg2
from psycopg2 import sql
from datetime import datetime

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

# Function to fetch games by date with conditional score display and stadium name
def fetch_games_by_date(date):
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
    conn = connect_db()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(query, (date,))
                results = cur.fetchall()
                if results:
                    print(f"Games on {date}:")
                    for row in results:
                        game_id, game_date, home_team, away_team, stadium_name, home_score, away_score, status = row
                        print(f"GameId: {game_id}")
                        print(f"Date: {game_date}")
                        print(f"Stadium: {stadium_name}")
                        print(f"Home Team: {home_team} vs Away Team: {away_team}")
                        print(f"Status: {status}")
                        if status != 'Not yet started':
                            print(f"Score: {home_team} {home_score} - {away_score} {away_team}")
                        print("-" * 40)
                else:
                    print(f"No games found on {date}.")
        except Exception as e:
            print(f"Error fetching games: {e}")
        finally:
            conn.close()

# Example usage
if __name__ == "__main__":
    date = input("Enter the date (YYYY-MM-DD) to search for games: ")
    fetch_games_by_date(date)
