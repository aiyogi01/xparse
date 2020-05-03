from xparse.regular.automata import TableRow, Table, Nfa, Dfa


def test_table_row():
    row = TableRow({"a": 1, "b": 2})
    print(row)

