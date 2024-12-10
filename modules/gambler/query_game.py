import pandas as pd
from ..Action import Action
from ..util import *


class query_game(Action):
    # Function to fetch game details, related bet types, and match history
    def fetch_game_details(self, game_id, conn, db, cur):
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
        WHERE bor.game_id = %s;
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
        try:
            # Fetch game details
            cur.execute(game_query, (game_id,))
            game_details = cur.fetchone()
            if not game_details:
                conn.send("No game found with the given ID.\n".encode('utf-8'))
                return None, None
                    
            # Display game details
            game_date, home_team_id, away_team_id, home_team, away_team, home_score, away_score, status = game_details
            details = (
                "-----------------------\n"
                f"Game Date: {game_date}\n"
                f"Home Team: {home_team} vs Away Team: {away_team}\n"
                f"Status: {status}\n"
            )
            if status != "Not yet started":
                details += f"Score: {home_team} {home_score} - {away_score} {away_team}\n"
            conn.sendall(("[TABLE]" + '\n' + details + '-----------------------\n\n' + "[END]").encode('utf-8'))
            
            # Fetch and display related bet types
            cur.execute(bet_type_query, (game_id,))
            bet_types = cur.fetchall()
            if bet_types:
                bet_details = "Available Bet Types for This Game:\n"
                for idx, (record_id, type_id, type_name, odd_1, odd_2) in enumerate(bet_types, start=1):
                    bet_details += f"{idx}. {type_name}\n   Odds: Home ({odd_1}), Away ({odd_2})\n"
                conn.sendall(bet_details.encode('utf-8'))
            else:
                conn.send("No bet types available for this game.\n".encode('utf-8'))
                    
            # Fetch history as DataFrame
            cur.execute(history_query, (home_team_id, away_team_id, away_team_id, home_team_id, game_date))
            history_data = cur.fetchall()
            if history_data:
                # Convert history data to DataFrame
                columns = ["Match Date", "Home Team", "Away Team", "Home Score", "Away Score", "Winner"]
                history_df = pd.DataFrame(history_data, columns=columns)
                
                data_table = print_table(history_data, cur, columns)    
                # Display DataFrame and statistics
                # history_df.to_string(index=False)
                conn.send("\nLatest 10 matches:\n".encode('utf-8'))
                conn.send(data_table.encode('utf-8'))
                home_wins = (history_df["Winner"] == "Home").sum()
                away_wins = (history_df["Winner"] == "Away").sum()
                stats = (
                    f"\n\nOverall Record Before This Game:\n"
                    f"{home_team} (Home) won {home_wins} times.\n"
                    f"{away_team} (Away) won {away_wins} times.\n\n"
                )
                conn.sendall(stats.encode('utf-8'))
                return bet_types, history_df
            else:
                conn.send("No match history available for these teams before this game.\n\n".encode('utf-8'))
            return bet_types, pd.DataFrame()
                    
        except Exception as e:
            conn.send(f"Error fetching game details: {e}\n".encode('utf-8'))
            return None, None

    # Function to handle gambling phase
    def gambling_phase(self, bet_types, conn, db, cur):
        if not bet_types:
            conn.send("No available bet types. Exiting gambling phase.\n".encode('utf-8'))
            return

        while True:
            conn.send("\n[GET]Do you want to enter the gambling phase? Enter the bet type number or 0 to exit.\n--->".encode('utf-8'))
            bet_choice = conn.recv(1024).decode('utf-8').strip()
            try:
                bet_choice = int(bet_choice)
                if bet_choice == 0:
                    conn.send("Exiting gambling phase.\n\n".encode('utf-8'))
                    break
                elif 1 <= bet_choice <= len(bet_types):
                    record_id, _, type_name, odd_1, odd_2 = bet_types[bet_choice - 1]
                    response = (
                        f"You chose to bet on {type_name}.\n"
                        f"Selected Record ID: {record_id}\n"
                    )
                    conn.sendall((response + '\n').encode('utf-8'))
                    break
                else:
                    conn.send("Invalid choice. Please enter a valid number.\n".encode('utf-8'))
            except ValueError:
                conn.send("Invalid input. Please enter a number.\n".encode('utf-8'))

    def exec(self, conn, db, cur, user):
        conn.send("\n[GET]Enter the Game ID to fetch details: ".encode('utf-8'))
        game_id = conn.recv(1024).decode('utf-8').strip()
        bet_types, history_df = self.fetch_game_details(game_id, conn, db, cur)
        if bet_types:
            self.gambling_phase(bet_types, conn, db, cur)
        return None
