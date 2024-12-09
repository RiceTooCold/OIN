import psycopg2
from ..Action import Action
from ..util import *


class query_bet_type(Action):
    
    # Function to fetch all bet types and display them with numbered options
    def display_bet_types(self, conn, cur):
        query = "SELECT type_id, type_name FROM BET_TYPE;"
        try:
            cur.execute(query)
            results = cur.fetchall()
            if results:
                options = {str(index + 1): row for index, row in enumerate(results)}
                response = "Available Bet Types:\n"
                for num, row in options.items():
                    response += f"{num}. {row[1]}\n"
                conn.sendall(("[TABLE]" + '\n' + response + '\n' + "[END]").encode('utf-8'))
                return options
            else:
                conn.send("No bet types found.\n".encode('utf-8'))
                return {}
        except Exception as e:
            conn.send(f"Error fetching bet types: {e}\n".encode('utf-8'))
            return {}

    # Function to display the manual of a selected bet type
    def display_bet_manual(self, selected_option, options, conn, cur):
        if selected_option in options:
            type_id, type_name = options[selected_option]
            query = "SELECT manual FROM BET_TYPE WHERE type_id = %s;"
            try:
                cur.execute(query, (type_id,))
                manual = cur.fetchone()
                if manual:
                    response = f"Manual for {type_name}:\n{manual[0]}\n"
                    conn.sendall(response.encode('utf-8'))
                else:
                    conn.send("Manual not found for the selected bet type.\n".encode('utf-8'))
            except Exception as e:
                conn.send(f"Error fetching manual: {e}\n".encode('utf-8'))
        else:
            conn.send("Invalid selection. Please choose a valid option.\n".encode('utf-8'))

    def exec(self, conn, db, cur, user):
        options = self.display_bet_types(conn, cur)
        if options:
            conn.send("[INPUT]Enter the number of the bet type to see its manual: ".encode('utf-8'))
            selected_option = conn.recv(1024).decode('utf-8').strip()
            conn.send(("-" * 40 + "\n").encode('utf-8'))
            
            self.display_bet_manual(selected_option, options, conn, cur)
            
            return None
        
# Example usage
if __name__ == "__main__":
    query_bet_type()
