from tabulate import tabulate
def print_table(rows, cur, columns):
    # rows = cur.fetchall()
    if columns is None:
        columns = [desc[0] for desc in cur.description]

    return tabulate(rows, headers=columns, tablefmt="github")