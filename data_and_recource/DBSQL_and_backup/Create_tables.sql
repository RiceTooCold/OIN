-- SQLBook: Code
CREATE TABLE TEAM (
    team_id BIGINT PRIMARY KEY,     -- 球隊ID，為唯一鍵
    abbreviation VARCHAR(3) NOT NULL, -- 縮寫
    name VARCHAR(20) NOT NULL,    -- 球隊名稱
    city VARCHAR(20) NOT NULL,    -- 城市
    owner VARCHAR(50)     -- 球隊擁有者
);
DROP TABLE TEAM CASCADE;
SELECT * FROM TEAM;
---------------------------------
CREATE TABLE STADIUM (
    stadium_id CHAR(4) PRIMARY KEY,  -- 體育館 ID，作為唯一鍵
    t_id BIGINT REFERENCES TEAM(team_id),  -- 關聯到 TEAM 資料表中的 team_id
    s_name VARCHAR(50) NOT NULL,  -- 體育館名稱
    capacity INT,           -- 容量
	CONSTRAINT fk_t_id FOREIGN KEY (t_id) REFERENCES TEAM(team_id)
        ON DELETE SET NULL ON UPDATE CASCADE
);
DROP TABLE STADIUM CASCADE;
SELECT * FROM STADIUM;
----------------------------------
CREATE TABLE SEASON (
    season_id INT PRIMARY KEY,       -- 賽季 ID，作為唯一鍵
    season_type VARCHAR(20) NOT NULL   -- 賽季類型，例如 Regular Season 或 Playoffs
);
DROP TABLE SEASON CASCADE;
SELECT * FROM SEASON;
-----------------------------------
CREATE TABLE TEAM_OF_SEASON (
    season_id INT REFERENCES SEASON(season_id),  -- 賽季 ID，參考 SEASON 表
    team_id BIGINT REFERENCES TEAM(team_id), -- 球隊 ID，參考 TEAM 表
    wins INT NOT NULL,                        -- 勝場數
    losses INT NOT NULL,                      -- 負場數
    playoffs BOOLEAN NOT NULL,                -- 是否進入季後賽
    PRIMARY KEY (season_id, team_id),             -- 複合主鍵，確保每個賽季每支球隊唯一
	CONSTRAINT fk_season_id FOREIGN KEY (season_id) REFERENCES SEASON(season_id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_team_id FOREIGN KEY (team_id) REFERENCES TEAM(team_id)
        ON DELETE SET NULL ON UPDATE CASCADE
);
DROP TABLE TEAM_OF_SEASON CASCADE;
SELECT * FROM TEAM_OF_SEASON;
-----------------------------------
CREATE TABLE GAME (
    game_id BIGINT PRIMARY KEY NOT NULL, -- 比賽代號，主鍵
    season_id INT NOT NULL,           -- 賽季年份，外鍵
    season_type VARCHAR(20) NOT NULL,   -- 賽季類型
    stadium_id CHAR(4),         -- 球場代號，外鍵
    home_team_id BIGINT NOT NULL,       -- 主隊代號，外鍵
    away_team_id BIGINT NOT NULL,       -- 客隊代號，外鍵
    home_score INT,                     -- 主隊得分
    away_score INT,                     -- 客隊得分
    home_win CHAR(1) CHECK (home_win IN ('W', 'L')), -- 主隊勝利
    game_date DATE NOT NULL,      -- 開賽時間
    status VARCHAR(20) NOT NULL CHECK (status IN ('Ongoing', 'Ended', 'Not yet started')), -- 狀態
    CONSTRAINT fk_season_year FOREIGN KEY (season_id) REFERENCES SEASON(season_id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_stadium_id FOREIGN KEY (stadium_id) REFERENCES STADIUM(stadium_id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_home_team_id FOREIGN KEY (home_team_id) REFERENCES TEAM(team_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_away_team_id FOREIGN KEY (away_team_id) REFERENCES TEAM(team_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);
DROP TABLE GAME CASCADE;
SELECT * FROM GAME;
-------------------------------
CREATE TABLE GAMBLER (
    gambler_id VARCHAR(10) PRIMARY KEY NOT NULL,    -- 投注者代號，主鍵
    gam_name VARCHAR(30) NOT NULL UNIQUE,     -- 投注者名稱，唯一且不可為空
    email VARCHAR(50) NOT NULL,               -- 電子郵件
    password VARCHAR(50) NOT NULL,            -- 密碼
    join_date DATE NOT NULL,                  -- 加入日期
    balance DECIMAL NOT NULL                  -- 餘額
);
DROP TABLE GAMBLER CASCADE;
SELECT * FROM GAMBLER;
--------------------------------
CREATE TABLE ADMIN (
    admin_id VARCHAR(10) PRIMARY KEY NOT NULL, -- 管理員ID，主鍵
    admin_name VARCHAR(20) NOT NULL,          -- 管理員名稱
    password VARCHAR(50) NOT NULL             -- 密碼
);
DROP TABLE ADMIN CASCADE;
SELECT * FROM ADMIN;
--------------------------------
CREATE TABLE BET_TYPE (
    type_id VARCHAR(10) PRIMARY KEY NOT NULL,            -- 下注類型代號，主鍵
    type_name VARCHAR(15) NOT NULL,                -- 類型名稱
    manual VARCHAR(500) NOT NULL                   -- 玩法說明
);
DROP TABLE BET_TYPE CASCADE;
SELECT * FROM BET_TYPE;
--------------------------------
CREATE TABLE CASHFLOW_RECORD (
    trans_id VARCHAR(10) PRIMARY KEY NOT NULL,            -- 交易代號，主鍵
    gamb_id VARCHAR(10) NOT NULL,                         -- 玩家代號，外鍵
    trans_type VARCHAR(20) NOT NULL CHECK(trans_type IN ('Earn', 'Bet','Bet Cancelled','Deposit', 'Withdraw')),               -- 交易類型
    cashflow DECIMAL NOT NULL,                      -- 現金流量
    time TIMESTAMP NOT NULL,                        -- 交易時間
    CONSTRAINT fk_gamb_id FOREIGN KEY (gamb_id) REFERENCES GAMBLER(gambler_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);
DROP TABLE CASHFLOW_RECORD CASCADE;
SELECT * FROM CASHFLOW_RECORD;
--------------------------------
CREATE TABLE GAMBLER_BETS (
    bet_time TIMESTAMP NOT NULL,                              -- 下注時間
    gamb_id VARCHAR(10) NOT NULL,                            -- 投注者代號，外鍵
    rec_id VARCHAR(10) NOT NULL,                             -- 賠率記錄代號，外鍵
    which_side VARCHAR(10) NOT NULL CHECK(which_side IN ('Home', 'Away')),    -- 下注區選擇
	odd DECIMAL NOT NULL,
    amount DECIMAL NOT NULL,                                 -- 金額
    status VARCHAR(20) NOT NULL CHECK (status IN ('Completed', 'Cancelled', 'Pending')), -- 狀態
    CONSTRAINT pk_gambler_bets PRIMARY KEY (bet_time, gamb_id, rec_id), -- 複合主鍵
    CONSTRAINT fk_gamb_id FOREIGN KEY (gamb_id) REFERENCES GAMBLER(gambler_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_rec_id FOREIGN KEY (rec_id) REFERENCES BET_ODDS_RECORD(record_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);
DROP TABLE GAMBLER_BETS CASCADE;
SELECT * FROM GAMBLER_BETS;
--------------------------------
CREATE TABLE BET_ODDS_RECORD (
    record_id VARCHAR(10) PRIMARY KEY NOT NULL,           -- 賠率記錄代號，主鍵
    game_id BIGINT NOT NULL,                         -- 比賽代號，外鍵
    type_id VARCHAR(10) NOT NULL,                         -- 下注類型代號，外鍵
    odd_1 DECIMAL NOT NULL,                         -- 賠率1
    odd_2 DECIMAL NOT NULL,                         -- 賠率2
    latest_modified TIMESTAMP NOT NULL,             -- 最後修改時間
    status VARCHAR(20) NOT NULL CHECK (status IN ('Expired', 'Processing', 'Not yet started')), -- 狀態
    CONSTRAINT fk_game_id FOREIGN KEY (game_id) REFERENCES GAME(game_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_type_id FOREIGN KEY (type_id) REFERENCES BET_TYPE(type_id)
        ON DELETE SET NULL ON UPDATE CASCADE
);
DROP TABLE BET_ODDS_RECORD CASCADE;
SELECT * FROM BET_ODDS_RECORD;
-------------------------------------

UPDATE GAME
SET status = 'Ongoing'
WHERE game_id = '42200111';

UPDATE BETS_ODD_RECORD
SET status = 'Processing'
WHERE game_id = 42200111;

UPDATE GAMBLER_BETS 
SET status = 'Pending' WHERE gamb_id = 'G000000001' AND rec_id = 'R000014581';

SELECT * FROM BET_ODDS_RECORD
WHERE game_id = 42200111;

SELECT * FROM GAMBLER_BETS
WHERE gamb_id = 'G000000001';
---------------------

SELECT * FROM BET_ODDS_RECORD
WHERE game_id = 42200212;

UPDATE BET_ODDS_RECORD
SET status = 'Not yet started'
WHERE game_id = 42200212;

SELECT *    
FROM GAME g
WHERE g.season_id % 10000 = 2022;