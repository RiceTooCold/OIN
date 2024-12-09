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

# Function to fetch top gamblers by ROI
def fetch_top_gamblers_by_roi():
    conn = connect_db()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
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
                top_gamblers_df = pd.DataFrame(top_gamblers, columns=columns)

                # Display results
                print("\nTop 5 Gamblers by ROI:")
                print(top_gamblers_df)
            else:
                print("No completed bets found to calculate ROI.")

    except Exception as e:
        print(f"Error fetching top gamblers by ROI: {e}")
    finally:
        conn.close()

# Example usage
if __name__ == "__main__":
    fetch_top_gamblers_by_roi()
