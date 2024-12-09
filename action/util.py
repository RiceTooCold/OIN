from tabulate import tabulate
def print_table(rows, cur):
    # rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]

    return tabulate(rows, headers=columns, tablefmt="github")