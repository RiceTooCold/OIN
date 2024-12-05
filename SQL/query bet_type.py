import psycopg2

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "dbname": "OIN",
    "user": "postgres",
    "password": "705046",
}

# Function to connect to the database
def connect_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# Function to fetch all bet types and display them with numbered options
def display_bet_types():
    query = "SELECT type_id, type_name FROM BET_TYPE;"
    conn = connect_db()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(query)
                results = cur.fetchall()
                if results:
                    print("Available Bet Types:")
                    options = {str(index + 1): row for index, row in enumerate(results)}
                    for num, row in options.items():
                        print(f"{num}. {row[1]}")
                    return options
                else:
                    print("No bet types found.")
                    return {}
        except Exception as e:
            print(f"Error fetching bet types: {e}")
            return {}
        finally:
            conn.close()

# Function to display the manual of a selected bet type
def display_bet_manual(selected_option, options):
    if selected_option in options:
        type_id, type_name = options[selected_option]
        query = "SELECT manual FROM BET_TYPE WHERE type_id = %s;"
        conn = connect_db()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(query, (type_id,))
                    manual = cur.fetchone()
                    if manual:
                        print(f"Manual for {type_name}:")
                        print(manual[0])
                    else:
                        print("Manual not found for the selected bet type.")
            except Exception as e:
                print(f"Error fetching manual: {e}")
            finally:
                conn.close()
    else:
        print("Invalid selection. Please choose a valid option.")

# Main function to execute the feature
def main():
    options = display_bet_types()
    if options:
        selected_option = input("Enter the number of the bet type to see its manual: ")
        print("-" * 40)
        display_bet_manual(selected_option, options)

# Example usage
if __name__ == "__main__":
    main()
