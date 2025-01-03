-- SQLBook: Code
Create Index game_id
On BET_ODDS_RECORD(Game_id);

Drop Index If Exists game_id;
--------------------------------
Create Index team_id
On GAME(home_team_id, away_team_id);

Drop Index If Exists team_id;