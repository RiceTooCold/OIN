from ..Action import Action
from ..util import *

# Function to update gambler's profile and send the updated record
class update_gambler_profile_transaction(Action):
    def exec(self, conn, db, cur, user):
        # Prompt for gambler ID

        gambler_id = user.get_userid()

        # Instructions for updating fields
        conn.send(
            "\nEnter new values for the fields you want to update. Leave blank to keep current values.\n".encode('utf-8')
        )
        conn.send("[GET]New name (gam_name): ".encode('utf-8'))
        new_name = conn.recv(1024).decode('utf-8').strip() or None
        conn.send("[GET]New password: ".encode('utf-8'))
        new_password = conn.recv(1024).decode('utf-8').strip() or None
        conn.send("[GET]New email: ".encode('utf-8'))
        new_email = conn.recv(1024).decode('utf-8').strip() or None
        conn.send(("-" * 40 + "\n").encode('utf-8'))

        fields_to_update = []
        values = []

        if new_name:
            fields_to_update.append("gam_name = %s")
            values.append(new_name)
        if new_email:
            fields_to_update.append("email = %s")
            values.append(new_email)
        if new_password:
            fields_to_update.append("password = %s")
            values.append(new_password)

        if not fields_to_update:
            conn.send("No updates provided. Nothing to change.\n".encode('utf-8'))
            return

        # Build dynamic SQL query for update
        update_query = f"""
        UPDATE GAMBLER
        SET {', '.join(fields_to_update)}
        WHERE gambler_id = %s;
        """
        values.append(gambler_id)

        # Query to fetch updated profile
        select_query = """
        SELECT gambler_id, gam_name, email, password, join_date, balance
        FROM GAMBLER
        WHERE gambler_id = %s;
        """

        try:
            # db.autocommit = False  # Start transaction

            # Execute update query
            cur.execute(update_query, values)

            # Fetch updated profile
            cur.execute(select_query, (gambler_id,))
            updated_profile = cur.fetchone()

            # Commit transaction
            db.commit()

            # Send updated profile
            if updated_profile:
                response = "Updated Profile:\n"
                response += f"Gambler ID: {updated_profile[0]}\n"
                response += f"Name: {updated_profile[1]}\n"
                response += f"Email: {updated_profile[2]}\n"
                response += f"Password: {updated_profile[3]}\n"
                response += f"Join Date: {updated_profile[4]}\n"
                response += f"Balance: {updated_profile[5]}\n"
                conn.sendall(("-------------\n" + response + "-------------\n\n").encode('utf-8'))
            else:
                conn.send("Gambler not found after update.\n".encode('utf-8'))

        except Exception as e:
            db.rollback()  # Rollback transaction on error
            conn.send(f"Transaction failed: {e}\n".encode('utf-8'))
        finally: 
            return None