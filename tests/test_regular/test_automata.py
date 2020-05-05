import pytest

from xparse.regular.automata import TableRow, Table, Nfa, Dfa, flatten_lists, set_union, AutomatonError


@pytest.mark.parametrize("lists, result", [
    ([[1, 2, 3], [4, 5]], [1, 2, 3, 4, 5]),
    ([[1], [2], [3]],     [1, 2, 3]),
    ([[], [], [1]],       [1])
])
def test_flatten_lists(lists, result):
    assert flatten_lists(*lists) == result


@pytest.mark.parametrize("sets, result", [
    ([{1, 2, 3}, {4, 5}], {1, 2, 3, 4, 5}),
    ([{1}, {2}, {2}],     {1, 2}),
    ([set(), set(), {1}], {1})
])
def test_set_union(sets, result):
    assert set_union(*sets) == result


def test_create_empty_table_row():
    row = TableRow()
    assert row.data == {}
    assert row.default is None


def test_table_row_exception():
    with pytest.raises(AutomatonError) as e:
        TableRow("string")
    assert e.value.args[0] == "Unsupported type: <class 'str'>"


@pytest.mark.parametrize("this, other, result", [
    (TableRow({0: "a"}, None), "not-a-table-row", False),
    (TableRow(), TableRow(), True),
    (TableRow({0: "a"}, None), TableRow({0: "a"}, None), True),
    (TableRow({0: "a"}, None), TableRow({0: "a"}, int), False),
    (TableRow({0: "a"}, None), TableRow({1: "a"}, None), False)
])
def test_table_row_equality(this, other, result):
    assert (this == other) is result


def test_table_row_get_default_value():
    row0 = TableRow(default=None)
    row1 = TableRow(default=int)
    assert row0[100] is None
    assert row1[100] == 0


def test_table_row_get_value():
    row = TableRow({0: "a"})
    assert row[0] == "a"


def test_table_row_set_value():
    row = TableRow()
    row[10] = "a"
    assert row[10] == "a"


def test_table_row_string_representation():
    row = TableRow({0: "a"})
    assert str(row) == "{0: 'a'}"


def test_table_row_columns():
    row = TableRow({"a": 0, "c": 2})
    assert row.columns == ["a", "c"]


def test_table_row_map():
    row = TableRow({0: "world", 1: "sun"})
    assert row.map(lambda x: "hello " + x).data == {0: "hello world", 1: "hello sun"}


def test_create_empty_table():
    table = Table()
    assert table.data == []
    assert table.default is None


def test_create_table_from_table_rows():
    table = Table([TableRow({0: "a"}), TableRow({0: "b"})], default=None)
    assert table.data == [TableRow({0: "a"}), TableRow({0: "b"})]
    assert table.default is None


def test_create_table_from_dicts():
    table = Table([{0: "a"}, {0: "b"}], default=None)
    assert table.data == [TableRow({0: "a"}), TableRow({0: "b"})]
    assert table.default is None


def test_table_exception():
    with pytest.raises(AutomatonError) as e:
        Table("string")
    assert e.value.args[0] == "Unsupported type: <class 'str'>"


@pytest.mark.parametrize("this, other, equal", [
    (Table(), Table(), True),
    (Table(), "not-a-table", False),
    (Table([{0: "a"}, {1: "b"}], default="x"), Table([{0: "a"}, {1: "b"}], default="x"), True),
    (Table([{0: "a"}, {1: "b"}], default="x"), Table([{0: "a"}, {1: "b"}], default="y"), False),
    (Table([{0: "a"}, {2: "c"}], default="x"), Table([{0: "a"}, {1: "b"}], default="x"), False)
])
def test_table_equality(this, other, equal):
    assert (this == other) is equal


@pytest.mark.parametrize("default, expected", [
    (1, 1),
    (int, 0),
    (set, set())
])
def test_table_default_value(default, expected):
    table = Table([{0: "a"}, {1: "b"}], default=default)
    assert table[1]["a"] == expected


def test_table_get_row():
    table = Table([{0: "a"}, {1: "b"}], default=str)
    assert table[0] == TableRow({0: "a"}, default=str)
    assert table[1] == TableRow({1: "b"}, default=str)


@pytest.mark.parametrize("table, length", [
    (Table(), 0),
    (Table([{0: "a"}]), 1),
    (Table([{0: "a"}, {0: "b"}]), 2)
])
def test_table_length(table, length):
    assert len(table) == length


def test_table_iterator():
    table = Table([{0: 0}, {0: 1}, {0: 2}])
    for i, row in enumerate(table):
        assert row[0] == i


def test_table_string_representation():
    table = Table([{0: "a"}, {1: "b"}], default="x")
    representation = str(table)
    assert "| 0 | a | x |" in representation
    assert "| 1 | x | b |" in representation


def test_table_columns():
    table = Table([{"a": 0, "b": 1}, {"c": 2}])
    assert table.columns == ["a", "b", "c"]


def test_table_get_final_row_index():
    table = Table([{"a": 0, "b": 1}, {"c": 2}])
    assert table.final == 1


def test_table_with_empty_row():
    table = Table.with_empty_row(default=int)
    assert len(table) == 1
    assert table[0] == TableRow(default=int)


def test_table_map():
    table = Table([{"a": 1}, {"b": 2}])
    assert table.map(lambda x: x + 100) == Table([{"a": 101}, {"b": 102}])


def test_table_as_list():
    table = Table([{"a": 0, "b": 1}, {"c": 2}])
    assert table.as_list() == [{"a": 0, "b": 1}, {"c": 2}]
