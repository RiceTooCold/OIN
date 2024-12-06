import pandas as pd

# 匯入 betodds 資料
betodds_csv_path = "./Tables/BET_ODDS_RECORD.csv"
betodds_df = pd.read_csv(betodds_csv_path)

# 確保 Record_id 按數字順序排序，去除非唯一組合
betodds_df = betodds_df.sort_values(by=["G_id", "BetType_id", "Record_id"]).drop_duplicates(
    subset=["G_id", "BetType_id"],
    keep="first"
)

# 將結果匯出為新的 CSV 文件
output_csv_path = "unique_betodds.csv"
betodds_df.to_csv(output_csv_path, index=False)

print(f"已成功匯出去重後的資料至 {output_csv_path}")
