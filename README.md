# Oin Sports Betting Platform

## 簡介

**Oin Sports Betting Platform** 是一個專為運動博彩愛好者設計的先進伺服器系統。該系統支援 **gamblers**（賭客）與 **administrators**（管理者），提供即時下注、個人資料管理、ROI 排行等功能。系統使用 Python 實作，採用 socket 處理通訊，並利用多執行緒實現同時多連線處理。

---

## 功能

### 通用功能
- **Welcome Interface** : 提供用戶友好的介面，適用於新用戶與回訪用戶。
- **Threaded Connections** : 支援多用戶同時連線，確保即時下注體驗。
- **Database Integration** : 強大的後端數據管理系統，用於管理用戶和投注數據。

---

### Welcome Page 功能  for 未登入的 User （一般使用者）
- **NBA historical season standings** : 查詢賽季排行榜，了解當前運動聯賽狀況，可當作投注前的評估考量。
- **Games on a specific date** : 按日期查看可投注的比賽，也可用來搜尋一些日子前的資訊，無論是滿足自身對 NBA 戰績的好奇或是為了賭注
- **Specific Game Info** : 透過前一個功能所獲得的 game_id 可以拿來用在此功能，並了解更詳細的對戰情況。
- **Bets type** : 查詢投注類型，
- **Login** : 登入平台。
- **Registration** : 註冊新用戶。
- **Exit** : 離開平台。

---

### Gamblers 功能  for 已登入的 User （一般使用者）
- **NBA historical season standings** : 查詢賽季排行榜，了解當前運動聯賽狀況，可當作投注前的評估考量。
- **Specific Game Info** : 透過前一個功能所獲得的 game_id 可以拿來用在此功能，並了解更詳細的對戰情況。
- **Games on a specific date** : 按日期查看可投注的比賽，也可用來搜尋一些日子前的資訊，無論是滿足自身對 NBA 戰績的好奇或是為了賭注
- **Bets type** : 查詢投注類型，
- **Gambler Profile** : 查看賭客詳細資料。
- **Make bets or Update historical bets** : 下單或更新投注。
- **Update Profile** : 更新個人資料（如姓名、email、password等）。
- **Top up** : 進行帳戶充值操作。
- **Log Out** : 安全登出平台。

---

### Administrators 功能  for （管理員／業務經營者）
- **Top5 Gamblers** : 按 ROI 查詢排名前五的賭客。
- **Bets on a specific date** : 按日期查詢投注記錄。
- **Open bets** : 為即將開始的比賽開放投注並設置賠率。
- **Settle the game** : 結算比賽結果，分配獎金。所有金流都會被更新到 cashflow 的 table。
- **Log Out** : 安全登出平台。

---

## 使用方式

- 使用備份檔 `OIN_backup.backup` 復原資料庫
- 在 `utils.py` 設定**資料庫名稱** (DB_NAME)、**使用者名稱** (DB_USER)、**主機位置** (DB_HOST)及**通訊埠** (DB_PORT)

1. 啟動伺服器：
   ```bash
   python3 server.py [port]
2. 啟動客戶端：
   ```bash
   python3 client.py [ip] [port]

如果跑不動 就把 python3 改成 python


## 技術細節
- 使用 Socket 建立 client-server 連線，搭配 Multithreading 達成多人同時連線 (本來有打算使用 select，但由於實作太過麻煩，故改成用 thread)
- 資料庫使用 PostgreSQL，使用套件 Psycopg2 對資料庫進行操作
- **交易管理** : 針對我們每個有 update 的功能，都有設 ROLLBACK 以及 COMMIT 的機制，若在過程中透過 try catch 機制抓到有 error ，就會執行 ROLLBACK 將已更新的資料返回，另外 COMMIT 則會在所有資料都正確被更新後，就會執行，並完成本次 transaction，如此即可避免遇到 dirty read 或其他髒資料。 詳細就不把檔案列出來，只要檔名有 update 的就會有。
- **併行控制** : 由於我們開發到現在的系統並沒有兩個User 以上會對同一個資源做爭取的行為，故併行控制對我們而言並不是件需要特別考慮的事，故無須特別處理。

## 程式說明
1. `./server.py`
-     包含伺服器端的主要功能。
-     在連接資料庫後，透過 socket 建立監聽服務，接收來自客戶端的連線請求。
-     每當接收到一個客戶端連線，會啟動一個獨立的執行緒（thread）處理該連線，確保伺服器能並行處理多個客戶端。
2. `./client.py`
-     包含客戶端的主要功能。
-     持續從伺服器接收訊息並顯示於終端機。
-     當訊息包含特定標籤時，根據標籤執行對應的操作，例如讀取使用者輸入、讀取表格、關閉 socket 連線並結束程式。
-     對於不同 user 會進到不同 function 去做 handling
3. `./util.py`
- 一些與 server, client 有關的資料會放在這，以及連接 database 要用的資訊也會在這，另外一些有趣 function 也放在這
4. `./module` 資料夾
-     所有程式會用到的 function 都放在這，並依不同邏輯和使用對象分成共同使用, admin, gambler 去加以分類，另外以及用來記錄 role 用的 user folder
-     所有功能都繼承抽象類別 Action，使團隊在使用或維護 function 會更加輕鬆方便 
5. `./module/admin` 資料夾
-     存放與 admin 相關的 function，皆為 py + SQL 的組合
6. `./module/gambler` 資料夾
-     存放與 gambler 相關的 function，皆為 py + SQL 的組合
7. `./module/user` 資料夾
-     存放一個 class，用來在日後被宣告時，去辨別登入的 user 是 admin 還是 gambler，如此也大大簡化維護的方式，也使 code 相對簡潔有力。
8. `./data_and_recource` 資料夾
-     存放組內自己的資料用的

## 開發環境

- Windows 11

- Python: 3.11.4

  - psycopg2: 2.9.9
  - pandas: 2.2.2
  - tabulate: 0.9.0

- PostgreSQL: 16.4
