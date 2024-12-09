import psycopg2
from ..Action import Action
from ..util import *

# Function to manage bet odds update
class manage_bet_odds(Action):
    
    # Function to fetch bet odds record details
    def fetch_bet_odds_record(self, record_id, conn, cur):
        query = """
        SELECT 
            record_id, 
            game_id, 
            odd_1, 
            odd_2, 
            status 
        FROM BET_ODDS_RECORD
        WHERE record_id = %s;
        """
        try:
            cur.execute(query, (record_id,))
            record = cur.fetchone()
            if record:
                return record
            else:
                conn.send(f"No record found with ID: {record_id}\n".encode('utf-8'))
                return None
        except Exception as e:
            conn.send(f"Error fetching bet odds record: {e}\n".encode('utf-8'))
            return None
                
    # Function to update bet odds
    def update_bet_odds(self, record_id, new_odd_1, new_odd_2, conn, db, cur):
        query = """
        UPDATE BET_ODDS_RECORD
        SET odd_1 = %s, odd_2 = %s
        WHERE record_id = %s AND status != 'Expired'; 
        """
        try:
            cur.execute(query, (new_odd_1, new_odd_2, record_id))
            if cur.rowcount == 0:
                conn.send(f"Cannot update record with ID {record_id}. Either it doesn't exist or its status is 'Completed'.\n".encode('utf-8'))
            else:
                db.commit()
                conn.send(f"Bet odds successfully updated for Record ID {record_id}.\n".encode('utf-8'))
        except Exception as e:
            conn.send(f"Error updating bet odds: {e}\n".encode('utf-8'))
            

    def exec(self, conn, db, cur):
        conn.send("[INPUT]Enter the Record ID to update odds: ".encode('utf-8'))
        record_id = conn.recv(1024).decode('utf-8')  # 假設這裡使用 conn.recv 接收用戶輸入
        record = self.fetch_bet_odds_record(record_id, conn, cur)
        print(record)
        if record:
            record_details = (
                "\nCurrent Record Details:\n"
                f"Record ID: {record[0]}\n"
                f"Game ID: {record[1]}\n"
                f"Odd 1: {record[2]}\n"
                f"Odd 2: {record[3]}\n"
                f"Status: {record[4]}\n"
            )
            conn.sendall(("[TABLE]" + '\n' + record_details + '\n' + "[END]").encode('utf-8'))
            
            if record[4] == "Expired":
                conn.send("\nThis record has a 'Expired' status and cannot be updated.\n".encode('utf-8'))
            else:
                try:
                    conn.send("[INPUT]Enter new Odd 1: ".encode('utf-8'))
                    new_odd_1 = float(conn.recv(1024).decode('utf-8').strip())
                    
                    conn.send("[INPUT]Enter new Odd 2: ".encode('utf-8'))
                    new_odd_2 = float(conn.recv(1024).decode('utf-8').strip())
                    
                    self.update_bet_odds(record_id, new_odd_1, new_odd_2, conn, db, cur)
                except ValueError:
                    conn.send("Invalid input. Odds must be numeric values.\n".encode('utf-8'))
                finally:
                    return None
# Example usage
if __name__ == "__main__":
    manage_bet_odds()
