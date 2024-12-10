# Oin Sports Betting Platform

## 簡介

**Oin Sports Betting Platform** 是一個專為運動博彩愛好者設計的先進伺服器系統。該系統支援 **gamblers**（賭客）與 **administrators**（管理者），提供即時下注、個人資料管理、ROI 排行等功能。系統使用 Python 實作，採用 socket 處理通訊，並利用多執行緒實現同時多連線處理。

---

## 功能

### 通用功能
- **Welcome Interface**: 提供用戶友好的介面，適用於新用戶與回訪用戶。
- **Threaded Connections**: 支援多用戶同時連線，確保即時下注體驗。
- **Database Integration**: 強大的後端數據管理系統，用於管理用戶和投注數據。

---

### Welcome Page 功能
- **Query Standings**: 查詢賽季排行榜，了解當前運動聯賽狀況。
- **Fetch Games by Date**: 按日期查看可投注的比賽。
- **Query Bet Type**: 查詢投注類型。
- **Login**: 登入平台。
- **Registration**: 註冊新用戶。
- **Exit**: 離開平台。

---

### Gamblers 功能
- **Query Standings**: 查詢賽季排行榜。
- **Fetch Gambler Details**: 查看賭客詳細資料。
- **Query Game**: 根據比賽 ID 或其他條件查詢比賽信息。
- **Fetch Games by Date**: 按日期篩選可投注比賽。
- **Query Bet Type**: 查詢當前支持的投注類型。
- **Handle Bet Transaction**: 下單或更新投注。
- **Update Profile**: 更新個人資料（如姓名、聯絡方式等）。
- **Deposit**: 進行帳戶充值操作。
- **Log Out**: 安全登出平台。

---

### Administrators 功能
- **Fetch Top Gamblers by ROI**: 按 ROI 查詢排名前五的賭客。
- **Fetch Bets by Date**: 按日期查詢投注記錄。
- **Open New Bets with Odds**: 為新比賽開放投注並設置賠率。
- **Settle Game**: 結算比賽結果，分配獎金。
- **Log Out**: 安全登出平台。

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

## 開發環境

- Windows 11

- Python: 3.10.6

  - psycopg2: 2.9.10
  - pandas: 2.2.2
  - tabulate: 0.9.0

- PostgreSQL: 16.4
