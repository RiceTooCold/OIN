from .Action import Action
class Exit(Action):
    def exec(self, conn, db, cur):
        conn.send(f'[EXIT]Exit system. GoddBye~\n'.encode('utf-8'))
        return -2