import psycopg2
import pandas as pd

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
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# Function to fetch team performance for a specific season from GAME table
def fetch_season_performance(season_id):
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
    conn = connect_db()
    if conn:
        try:
            with conn.cursor() as cur:
                # Execute query
                cur.execute(query, (season_id,))
                results = cur.fetchall()
                
                if not results:
                    print(f"No data found for the season {season_id}.")
                    return

                # Convert results to DataFrame
                columns = ["Team Name", "Total Games", "Wins", "Losses", "Win Rate (%)"]
                teams_df = pd.DataFrame(results, columns=columns)

                # Add a ranking column
                teams_df.insert(0, "Rank", range(1, len(teams_df) + 1))

                # Display DataFrame
                print(f"\nTeam Performance for Current Season ({season_id}):")
                print(teams_df)
                return teams_df
        except Exception as e:
            print(f"Error fetching current regular season performance: {e}")
        finally:
            conn.close()

# Main function
if __name__ == "__main__":
    # Step 1: Show current season performance
    current_season_id = 22022
    current_season_data = fetch_season_performance(current_season_id)

    # Step 2: Ask if the user wants to see another season
    while True:
        see_other_season = input("\nDo you want to see performance for another regular season? (yes/no): ").strip().lower()
        if see_other_season == "yes":
            season_id = int(input("Enter the season year (2013-2021): ")) + 20000
            fetch_season_performance(season_id)
        elif see_other_season == "no":
            print("Exiting.")
            break
        else:
            print("Invalid input. Please type 'yes' or 'no'.")
            
