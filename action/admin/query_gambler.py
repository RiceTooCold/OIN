import pandas as pd
from ..Action import Action
from ..util import *

# Function to fetch user details without showing the password
class fetch_gambler_details(Action):
    def exec(self, conn, db, cur):
        print(conn)
        conn.send("[INPUT]Enter the gambler ID to fetch details: ".encode('utf-8'))
        gambler_id = conn.recv(4096).decode("utf-8")
        
        table = ""
        table += ("-" * 40)
        table += "\n"
        
        gambler_query = """
        SELECT 
            gambler_id, 
            gam_name, 
            email, 
            join_date, 
            balance 
        FROM GAMBLER
        WHERE gambler_id = %s;
        """
        
        bets_query = """
        SELECT 
            bet_time, 
            rec_id, 
            which_side, 
            amount, 
            status 
        FROM GAMBLER_BETS
        WHERE gamb_id = %s
        ORDER BY bet_time DESC
        LIMIT 5;
        """
        
        total_amount_query = """
        SELECT 
            COALESCE(SUM(amount), 0)
        FROM GAMBLER_BETS
        WHERE gamb_id = %s;
        """
        
        try:
            cur.execute(gambler_query, (gambler_id, ))
            
            gambler_details = cur.fetchone()

            if gambler_details:
                
                table = "\n".join([
                    "User Details:",
                    f"Gambler ID: {gambler_details[0]}",
                    f"Name: {gambler_details[1]}",
                    f"Email: {gambler_details[2]}",
                    f"Join Date: {gambler_details[3]}",
                    f"Balance: {gambler_details[4]}",
                    "-" * 40,
                    "Last 5 Bets:"
                    "\n"
                ])
                
                conn.sendall(("[TABLE]" + '\n' + table).encode('utf-8'))
                
                # Fetch total bet amount
                cur.execute(total_amount_query, (gambler_id,))
                total_amount = cur.fetchone()[0]  # 回傳的也是 tuple 所以如果只要第一個數據 那就要用 [0]

                # Fetch last 5 bets
                cur.execute(bets_query, (gambler_id,))
                bets = cur.fetchall()
                if bets:
                    
                    #columns = ["Bet Time", "Record ID", "Side", "Amount", "Status"]
                    # bets_df = pd.DataFrame(bets, columns=columns)
                    
                    data_table = print_table(bets, cur)
                    
                    # send table
                    conn.sendall(data_table.encode('utf-8'))
                    
                    #send amount
                    conn.sendall((f"\nTotal Amount of All Bets: {total_amount}" + '\n' + "[END]").encode('utf-8'))
                    
                else:
                    msg = "No bets found for this gambler."
                    conn.sendall((f"\n{msg}" + '\n' + "[END]").encode('utf-8'))
            else:
                conn.send("No gambler found with the given ID.".encode('utf-8'))
        except Exception as e:
            print(f"Error fetching gambler details: {e}")
        finally:
            return None


# Example usage
if __name__ == "__main__":
    gambler_id = input("Enter the gambler ID to fetch details: ")
    print("-" * 40)
    fetch_gambler_details(gambler_id)

