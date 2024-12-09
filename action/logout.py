from .Action import Action
class logout(Action):
    def exec(self, conn, db, cur, user):
        conn.send("Successfully Logout\n".encode('utf-8'))
        return -1