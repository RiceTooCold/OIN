from ..Action import Action
from ..util import *
from datetime import datetime

class Deposit(Action):
    def generate_transaction_id(self, cur):
        query = """
        SELECT trans_id 
        FROM CASHFLOW_RECORD
        ORDER BY trans_id DESC
        LIMIT 1;
        """
        cur.execute(query)
        result = cur.fetchone()

        if result:
            # Extract numeric part and increment
            last_id = result[0]
            numeric_part = int(last_id[1:])  # Skip the 'T'
            new_id = f"T{numeric_part + 1:09d}"
        else:
            # Start from the first ID if table is empty
            new_id = "T000000001"

        return new_id
      
    def exec(self, conn, db, cur, user):
        try:
            conn.send("\nHere for you to top up your balance!\n".encode('utf-8'))
            conn.send("[GET]Enter the amount of money you want to add: ".encode('utf-8'))
            amount = conn.recv(4096).decode('utf-8').strip()

            trans_id = self.generate_transaction_id(cur)

            cashflow_query = """
                INSERT INTO CASHFLOW_RECORD (trans_id, gamb_id, trans_type, cashflow, time)
                VALUES (%s, %s, %s, %s, %s);
                """
            cur.execute(cashflow_query, (trans_id, user.get_userid(), "Deposit", amount, datetime.now()))

            balance_query = """
                Select balance
                From Gambler
                where gambler_id = %s;
            """
            cur.execute(balance_query, (user.get_userid(), ))

            remaining = cur.fetchone()[0]
            
            remaining = float(remaining) + float(amount)
            update_game_status_query = """
                UPDATE GAMBLER
                SET balance = %s
                WHERE gambler_id = %s;
                """
            cur.execute(update_game_status_query, (remaining, user.get_userid()))
            db.commit()
            conn.send("Successfully update the balance!\n\n".encode('utf-8'))
        except Exception as e:
            conn.send(f"Error update balcane: {e}\n".encode('utf-8'))
            db.rollback()  
        finally:
          return None
        