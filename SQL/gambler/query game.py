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
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# Function to fetch game details, related bet types, and match history
def fetch_game_details(game_id):
    game_query = """
    SELECT 
        g.game_date,
        t1.team_id AS home_team_id,
        t2.team_id AS away_team_id,
        t1.name AS home_team,
        t2.name AS away_team,
        g.home_score,
        g.away_score,
        g.status
    FROM GAME g
    LEFT JOIN TEAM t1 ON g.home_team_id = t1.team_id
    LEFT JOIN TEAM t2 ON g.away_team_id = t2.team_id
    WHERE g.game_id = %s;
    """
    bet_type_query = """
    SELECT 
        bor.record_id,
        bt.type_id,
        bt.type_name, 
        bor.odd_1,
        bor.odd_2
    FROM BET_ODDS_RECORD bor
    JOIN BET_TYPE bt ON bor.type_id = bt.type_id
    WHERE bor.game_id = %s 
        AND bor.status != 'Not yet started';
    """
    history_query = """
    SELECT 
        g.game_date AS match_date,
        t1.name AS home_team,
        t2.name AS away_team,
        g.home_score,
        g.away_score,
        CASE WHEN g.home_win = 'W' THEN 'Home' ELSE 'Away' END AS winner
    FROM GAME g
    LEFT JOIN TEAM t1 ON g.home_team_id = t1.team_id
    LEFT JOIN TEAM t2 ON g.away_team_id = t2.team_id
    WHERE ((g.home_team_id = %s AND g.away_team_id = %s) OR 
           (g.home_team_id = %s AND g.away_team_id = %s))
      AND g.game_date < %s
      AND g.status != 'Not yet started'
    ORDER BY g.game_date DESC
    LIMIT 10;
    """
    
    conn = connect_db()
    if conn:
        try:
            with conn.cursor() as cur:
                # Fetch game details
                cur.execute(game_query, (game_id,))
                game_details = cur.fetchone()
                if not game_details:
                    print("No game found with the given ID.")
                    return None, None
                
                # Display game details
                game_date, home_team_id, away_team_id, home_team, away_team, home_score, away_score, status = game_details
                print(f"Game Date: {game_date}")
                print(f"Home Team: {home_team} vs Away Team: {away_team}")
                print(f"Status: {status}")
                if status != "Not yet started":
                    print(f"Score: {home_team} {home_score} - {away_score} {away_score}")
                
                # Fetch and display related bet types
                print("\nAvailable Bet Types for This Game:")
                cur.execute(bet_type_query, (game_id,))
                bet_types = cur.fetchall()
                if bet_types:
                    for idx, (record_id, type_id, type_name, odd_1, odd_2) in enumerate(bet_types, start=1):
                        print(f"{idx}. {type_name}")
                        print(f"   Odds: Home ({odd_1}), Away ({odd_2})")
                else:
                    print("No bet types available for this game.")
                
                # Fetch history as DataFrame
                cur.execute(history_query, (home_team_id, away_team_id, away_team_id, home_team_id, game_date))
                history_data = cur.fetchall()
                if history_data:
                    # Convert history data to DataFrame
                    columns = ["Match Date", "Home Team", "Away Team", "Home Score", "Away Score", "Winner"]
                    history_df = pd.DataFrame(history_data, columns=columns)
                    
                    # Print DataFrame
                    print("\nLatest 10 matches:")
                    print(history_df)

                    # Calculate and display win statistics
                    home_wins = (history_df["Winner"] == "Home").sum()
                    away_wins = (history_df["Winner"] == "Away").sum()
                    print(f"\nOverall Record Before This Game:")
                    print(f"{home_team} (Home) won {home_wins} times.")
                    print(f"{away_team} (Away) won {away_wins} times.")
                    
                    return bet_types, history_df
                else:
                    print("No match history available for these teams before this game.")
                    return bet_types, pd.DataFrame()
                
        except Exception as e:
            print(f"Error fetching game details: {e}")
            return None, None
        finally:
            conn.close()

# Function to handle gambling phase
def gambling_phase(bet_types):
    if not bet_types:
        print("No available bet types. Exiting gambling phase.")
        return

    while True:
        print("\nDo you want to enter the gambling phase? Enter the bet type number or 0 to exit.")
        try:
            bet_choice = int(input("Your choice: "))
            if bet_choice == 0:
                print("Exiting gambling phase.")
                break
            elif 1 <= bet_choice <= len(bet_types):
                record_id, _, type_name, odd_1, odd_2 = bet_types[bet_choice - 1]
                print(f"You chose to bet on {type_name}.")
                print(f"Selected Record ID: {record_id}")
                break
            else:
                print("Invalid choice. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

# Example usage
if __name__ == "__main__":
    game_id = input("Enter the Game ID to fetch details: ").strip()
    bet_types, history_df = fetch_game_details(game_id)
    if bet_types:
        gambling_phase(bet_types)



