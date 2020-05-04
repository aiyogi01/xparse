"""
Module for defining finite automatons.
"""

from xparse.exceptions import *

EPSILON = "'e"
DOT = "dot"


# ----------------------------------------------------------------------
#       Helper functions
# ----------------------------------------------------------------------

def flatten_lists(*lists):
    """Flatten several lists into one list.

    Examples
    --------
    >>> flatten_lists([0, 1, 2], [3, 4, 5])
    [0, 1, 2, 3, 4, 5]

    Parameters
    ----------
    lists : an arbitrary number of iterable collections
        The type of the collections is not limited to lists,
        they can also be sets, tuples, etc.

    Returns
    -------
    flat_list : a flattened list
    """
    return [x for sublist in lists for x in sublist]


def set_union(*sets):
    """Return the union of sets.

    Examples
    --------
    >>> set_union({0, 1, 2}, {2, 3}, {3, 4})
    {0, 1, 2, 3, 4}

    Parameters
    ----------
    sets : an arbitrary number of iterable collections
        The the type of the collection is not limited to sets,
        they can also be lists, tuples, ect.

    Returns
    -------
    set_union : set which contains all items of the collections
    """
    return set(flatten_lists(*sets))


# ----------------------------------------------------------------------
#     Look-up tables
# ----------------------------------------------------------------------

class TableRow:
    """
    Representation of a row in a table.
    """
    def __init__(self, data=None, default=None):
        """Instantiate a table row from a dictionary.

        Examples
        --------
        Create a table row which contains the columns "a" and "b" and
        which returns an empty set for non-existing columns.

        >>> row = TableRow({"a": {0}, "b": {1}}, default=set)

        Get columns.

        >>> row["a"]
        {0}
        >>> row["c"]
        set()

        Parameters
        ----------
        data : a dictionary

        default : default value to return if a column does not exist
            If the default object is callable, that callable is called
            to construct the actual return value. Otherwise the object
            itself is returned.
        """
        if data is not None and not isinstance(data, dict):
            raise AutomatonError("Unsupported type: %s" % type(data))
        self.default = default
        self.data = {} if not data else data

    def _return_default(self):
        """Return the default value.

        If the default return object is callable, construct the actual
        return value by calling that object.
        """
        if callable(self.default):
            return self.default()
        else:
            return self.default

    def __getitem__(self, item):
        """Get the value for a column in the table row (use []).

        If the column does not exist, return the default value.
        """
        return self.data.get(item, self._return_default())

    def __setitem__(self, item, value):
        """Set the value of a column in the table row."""
        self.data[item] = value

    def __str__(self):
        """Get the string representation of the row.

        Returns
        -------
        string : string representation
        """
        return str(self.data)

    def __repr__(self):
        return str(self)

    @property
    def columns(self):
        """Get a list of all column names in the the table row.

        Examples
        --------
        >>> row = TableRow({"a": 0, "b": 1, "d": 3})
        >>> row.columns
        ['a', 'b', 'd']

        Returns
        -------
        column_names : a list of all column names in the table
        """
        return sorted(self.data.keys())

    def map(self, func):
        """Apply a function to all values in the row and return a new
        table row.

        Examples
        --------
        Add 10 to all column values of a table row.

        >>> row = TableRow({"a": 1, "b": 2})
        >>> row.map(lambda x: x + 10)
        {'a': 11, 'b': 12}

        Parameters
        ----------
        func : a callable object which takes one argument

        Returns
        -------
        table_row : a new table row with updated column values
        """
        return TableRow(
            {k: func(v) for k, v in self.data.items()},
            default=self.default
        )


class Table:
    """
    A lookup table (implemented as a list of dictionaries).
    """
    def __init__(self, data=None, default=None):
        """Instantiate a table from a sequence of rows.

        Examples
        --------
        Create a table with columns "a", "b" and "c" and the default
        return value 0.

        >>> table = Table([{"a": 1, "b": 2}, {"a": 2, "c": 3}], default=0)

        Parameters
        ----------
        data : an iterable collection of table rows
            The table rows may be dictionaries or TableRow objects.

        default : default value to return if a column does not exist
            If the default object is callable, that callable is called
            to construct the actual return value. Otherwise the object
            itself is returned.
        """
        self.default = default
        self.data = self._process_data(data)

    def _process_data(self, data):
        """Convert data to a list of TableRow objects.

        Parameters
        ----------
        data : an iterable collection of table rows
            The table rows may be dictionaries or TableRow objects.

        Returns
        -------
        table_rows : list of TableRow objects
        """
        result = []

        if data is None:
            return result

        for row in data:
            if isinstance(row, dict):
                result.append(TableRow(row, default=self.default))
            elif isinstance(row, TableRow):
                result.append(TableRow(row.data, default=self.default))
            else:
                raise AutomatonError("Unsupported type: %s" % type(row))

        return result

    def __getitem__(self, row_index):
        """Get the i-th row of the table.

        Parameters
        ----------
        row_index : table row index

        Returns
        -------
        row : a TableRow object with the specified index
        """
        return self.data[row_index]

    def __len__(self):
        """Get the number of rows in the table.

        Returns
        -------
        lengths : number of rows in the table
        """
        return len(self.data)

    def __iter__(self):
        """Get an iterator over the rows of the table.

        Returns
        -------
        iterator : iterator over the TableRow objects of the table
        """
        return iter(self.data)

    def __str__(self):
        """Get a string representation of the table.

        Examples
        --------
        >>> table = Table([{"a": {1, 2}, "b": {2}}, {"a": {3}}], default=set)

        ===== ========== =========
                a          b
        ===== ========== =========
          0     {1, 2}    {2}
          1     {3}       set()
        ===== ========== =========

        Returns
        -------
        string : string representation of the table
        """
        # Get the width of the index column and of all table columns.
        widths = [len(str(len(self) - 1))] + self._column_widths()

        # Construct a string templates to represent the rows.
        template = "|" + "|".join([" {:>%d} " %
                                   width for width in widths]) + "|"

        # Construct the separator row which separates the table header
        # from the table body.
        separator = "|" + \
            "+".join([(width + 2) * "-" for width in widths]) + "|"

        # Construct the header string and the row strings.
        header = template.format("", *self.columns)
        rows = [
            template.format(i, *[str(self[i][column]) for column in self.columns])
                for i in range(len(self))
        ]

        # Construct the whole string representation.
        table = [header, separator] + rows
        return "\n".join(table)

    def _column_widths(self):
        """Get the widths of the table columns measured in number of
        characters.

        Example
        -------
        >>> table = Table([{"a": 1, "b": 2}, {"a": 3}], default=None)
        >>> table._column_widths()
        [1, 4]

        In this table the column "a" would occupy maximally 1 character,
        while the column "b" would need 4 characters to represent the
        string "None" in the second row of the table. So the return
        value would be: [1, 4]

        Returns
        -------
        widths : list of integers
            The width of a column specifies how many characters the
            string representations of its values will occupy maximally.
        """
        result = []
        for column in self.columns:
            values = [str(column)] + [str(self[row][column])
                                      for row in range(len(self))]
            widths = [len(string) for string in values]
            result.append(max(widths))
        return result

    @property
    def columns(self):
        """Get a list of all columns names of the table.

        Examples
        --------
        >>> table = Table([{"a": 1, "b": 2}, {"a": 3, "c": 4}])
        >>> table.columns
        ['a', 'b', 'c']

        Returns
        -------
        column_names : a list of all column names
        """
        return sorted(set_union(*[row.columns for row in self]))

    @property
    def final(self):
        """Get the index of the last row in the table.

        Returns
        -------
        index : index of the last row
        """
        return len(self) - 1

    @classmethod
    def with_empty_row(cls, default=None):
        """Create a table with one empty row.

        Parameters
        ----------
        default : default return value for non-existing columns

        Returns
        -------
        table : a table with one empty row
        """
        return cls([{}], default=default)

    def map(self, func):
        """Apply a function to all values in the table and return a new
        table.

        Examples
        --------
        Add 10 to all values in the table.

        >>> table = Table([{"a": 1, "b": 2}, {"a": 3, "b": 4}])
        >>> table.map(lambda x: x + 10).as_list()
        [{'a': 11, 'b': 12}, {'a': 13, 'b': 14}]

        Parameters
        ----------
        func : a callable object which takes one argument

        Returns
        -------
        table : a new table with updated values
        """
        return Table([row.map(func) for row in self], default=self.default)

    def as_list(self):
        """Convert the table to a list of dictionaries.

        Examples
        --------
        >>> table = Table([{"a": 1, "b": 2}, {"a": 3, "b": 4}])
        >>> table.as_list()
        [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}]

        Returns
        -------
        list: list of dictionaries representing the table
        """
        return [row.data for row in self.data]


# ----------------------------------------------------------------------
#     NFA
# ----------------------------------------------------------------------

class Nfa:
    """
    An NFA (non-deterministic finite automaton).
    """

    def __init__(self, data):
        """Instantiate an Nfa object from a sequence of transition
        rules.

        Parameters
        ----------
        data : a sequence of transition rules
            Data may be a Table object, a sequence of TableRow objects
            or a sequence of dictionaries.

        """
        self.table = self._process_data(data)

        self._epsilon_closure = \
            [self._find_epsilon_closure(n) for n in range(len(self))]

    def __len__(self):
        """Get the number of states in the NFA.

        Returns
        -------
        number_of_states : number of states
            The number of states corresponds to the length of the
            transition table.
        """
        return len(self.table)

    def __getitem__(self, state):
        """Get all possible transitions for a state.

        Parameters
        ----------
        state : a state of the NFA represented as an integer

        Returns
        -------
        possible_transitions : possible transitions for the state
            The possible transitions for a state are represented as
            one row of a transition table.
        """
        return self.table[state]

    def __str__(self):
        """Get a string representation of the NFA in form of a look-up
        table.

        Returns
        -------
        string : string representation
        """
        return str(self.table)

    @staticmethod
    def _process_data(data):
        """Convert data to a Table object.

        Parameters
        ----------
        data : an iterable collection of table rows
            Data may be a Table object, a collection of TableRow objects
            or a collection of dictionaries.

        Returns
        -------
        table : a Table object
        """
        if isinstance(data, Table):
            return data

        return Table(data, default=set)

    def _find_epsilon_closure(self, state):
        """
        Find the epsilon closure of a state.

        The epsilon clojure of a state is a set of states of the NFA
        which include the initial state itself and all those states
        which can be reached via epsilon-transitions from that initial
        state.

        Parameters
        ----------
        state : state of the NFA represented as an integer

        Returns
        -------
        epsilon_clojure : set of states represented as a set of integers
        """
        def iter_search(states, update):
            if not update:
                return states
            update = update - states
            states = states | update
            update = set_union(*[self[u][EPSILON] for u in update])
            return iter_search(states, update - states)

        return iter_search({state}, self[state][EPSILON])

    @staticmethod
    def _concat_tables(*tables):
        """
        Concatenate several tables which represent NFA transition
        states.

        The default return value of the resultant table is the default
        return value of the first table.

        Examples
        --------
        >>> table_1 = Table([{"a": {1}, "b": {1}}, {}], default=None)

        ===== ======== ========
                a        b
        ===== ======== ========
          0     {1}      {1}
          1     None     None
        ===== ======== ========

        >>> table_2 = Table([{"c": {1}}, {}], default=None)

        ===== ========
                c
        ===== ========
          0     {1}
          1     None
        ===== ========


        Concatenated tables:

        ===== ======== ======== ========
                a        b        c
        ===== ======== ======== ========
          0     {1}      {1}      None
          1     None     None     None
          2     None     None     {3}
          3     None     None     None
        ===== ======== ======== ========

        Parameters
        ----------
        tables : NFA transition tables
            The tables should contains sets of integers as values.

        Returns
        -------
        table, offsets : concatenated table and a list of offsets
            In the resultant table the transition states are adjusted
            to the new row indexing. The offsets are integers which
            point at the beginnings of the original tables in the
            resultant table.
        """
        # Get the default return value of the first table.
        default = tables[0].default

        # Calculate the lengths of the tables.
        lengths = [len(table) for table in tables]

        # Calculate the offsets.
        offsets = [0] + [sum(lengths[:i + 1]) for i in range(len(tables) - 1)]

        # Construct new tables with adjusted transitional states.
        shifted = [table.map(lambda x: {elem + i for elem in x})
                   for table, i in zip(tables, offsets)]

        # Construct the resultant table.
        result = Table(
            [row for table in shifted for row in table], default=default)

        return result, offsets

    def epsilon_closure(self, states):
        """
        Get the epsilon closure of a state or a set of states.

        The epsilon clojure is the initial set of states itself plus all
        states of the NFA which can be reached by epsilon-transitions
        from those initial states.

        Parameters
        ----------
        states : a state or a set of states
            One single state is represented by an integer, a set of
            states is represented by an iterable collection of integers.

        Returns
        -------
        epsilon_closure : set of states
            The set of states is represented by a set of integers.
        """
        if isinstance(states, int):
            return self._epsilon_closure[states]
        return set_union(*[self._epsilon_closure[state] for state in states])

    @property
    def final(self):
        """Get the final state of the NFA.

        Returns
        -------
        state : final state represented by integer
        """
        return len(self) - 1

    def get_input_characters(self, states):

        return set_union(
            *[self[state].columns for state in states]) - {EPSILON}

    def is_final(self, states):
        """
        Does a set of states constitute a final state?

        It does constitute a final state if the (single) final state of
        the NFA is contained therein.

        Parameters
        ----------
        states : a set of states
            The set of states is represented as an iterable collection
            of integers.

        Returns
        -------
        result : boolean
        """
        return self.final in states

    def transition(self, states, char):
        """
        Transition on character input from the initial set of states to
        the resultant set of states.

        Parameters
        ----------
        states : an initial set of states
            The set of states is represented as an iterable collection
            of integers.

        char : input character

        Returns
        -------
        resultant_states : set of resultant states
            The resultant states are represented as a set of integers.
        """
        start = self.epsilon_closure(states)
        end = set_union(*[self[state][char] for state in start])
        return self.epsilon_closure(end)

    def match(self, string):
        """
        Match a string.

        Parameters
        ----------
        string : an input string

        Returns
        -------
        result : boolean
        """
        states = {0}
        for char in string:
            states = self.transition(states, char)
            if not states:
                return False
        return self.is_final(states)

    @classmethod
    def epsilon(cls):
        """
        Construct an epsilon-NFA.

        Returns
        -------
        epsilon_nfa : an NFA which accepts only epsilon
        """
        return cls([{EPSILON: {1}}, {}])

    @classmethod
    def char(cls, char):
        """
        Construct a single character NFA.

        Parameters
        ----------
        char : a character

        Returns
        -------
        char_nfa : an NFA which accepts only a single character
        """
        return cls([{char: {1}}, {}])

    @classmethod
    def concat(cls, *nfas):
        """
        Construct a concatenation of NFAs.

        Parameters
        ----------
        nfas : a variable number of Nfa objects

        Returns
        -------
        concat_nfa : an NFA which is a concatenation of the initial NFAs
        """
        # Concatenate tables.
        table, offsets = cls._concat_tables(*[nfa.table for nfa in nfas])

        # Connect the original tables by linking the last row of a
        # preceding table with the first row of the following table by
        # an epsilon-transition.
        for offset in offsets[1:]:
            table[offset - 1][EPSILON] = {offset}

        return cls(table)

    @classmethod
    def union(cls, *nfas):
        """
        Construct a union of NFAs.

        Parameters
        ----------
        nfas : a variable number of Nfa objects

        Returns
        -------
        union_nfa : an NFA which is the union of the initial NFAs
        """
        # Create two table with an empty row, one for the initial state
        # of the NFA and one for the final state.
        tables = [Table.with_empty_row(default=set)] +\
                 [nfa.table for nfa in nfas] +\
                 [Table.with_empty_row(default=set)]

        # Concatenate tables.
        table, offsets = cls._concat_tables(*tables)

        # Link the initial state of the NFA with the first rows of the
        # original tables by epsilon transitions.
        table[0][EPSILON] = set(offsets[1:-1])

        # Link the last rows of the original tables with the final state
        # of the NFA by epsilon transitions.
        for offset in offsets[2:]:
            table[offset - 1][EPSILON] = {table.final}

        return cls(table)

    @classmethod
    def star(cls, nfa):
        """
        Construct a Kleene-star NFA.

        Parameters
        ----------
        nfa : an NFA object

        Returns
        -------
        star_nfa : an NFA which is a Kleene-star of the initial NFA
        """
        # Create two table with an empty row, one for the initial state
        # of the NFA and one for the final state.
        tables = [Table.with_empty_row(default=set),
                  nfa.table,
                  Table.with_empty_row(default=set)]

        # # Concatenate tables.
        table, _ = cls._concat_tables(*tables)

        # Link the initial state of the NFA with the first row of the
        # original table and with the final state of the NFA by
        # epsilon-transitions.
        table[0][EPSILON] = {1, table.final}

        # Link the last row of the original table with the initial and
        # the final state of the NFA by an epsilon-transition.
        table[table.final - 1][EPSILON] = {0, table.final}

        return cls(table)


# ----------------------------------------------------------------------
#     DFA
# ----------------------------------------------------------------------

class Dfa:
    """
    A DFA (deterministic finite automaton).
    """
    def __init__(self, nfa):
        """Instantiate a Dfa from an Nfa object.

        Parameters
        ----------
        nfa : an Nfa object

        """
        self.table, self.finals = self._translate_nfa(nfa)

    def __str__(self):
        """Get a string representation of the DFA."""
        rows = [self.table[row] for row in sorted(self.table.keys())]
        return str(Table(rows))

    @staticmethod
    def _translate_nfa(nfa):
        """Translate an NFA into a DFA.

        Parameters
        ----------
        nfa : an Nfa object

        Returns
        -------
        dfa_table, finals : a DFA look-up table and a set of final
            states
        """
        data = {0: {}}
        finals = set()

        initial_state = frozenset(nfa.epsilon_closure(0))
        registered_states = {initial_state: 0}
        stack = [initial_state]

        while stack:
            nfa_state = stack.pop()
            dfa_state = registered_states[nfa_state]

            if dfa_state not in data:
                data[dfa_state] = {}
            row = data[dfa_state]

            input_chars = nfa.get_input_characters(nfa_state)

            # print("Start state:", nfa_state)
            # print("Input chars:", input_chars)
            # print()

            for char in sorted(input_chars):
                new_nfa_state = frozenset(nfa.transition(nfa_state, char))
                # print("'%s' -> %s" % (char, new_nfa_state))
                if new_nfa_state not in registered_states:
                    new_dfa_state = len(registered_states)
                    registered_states[new_nfa_state] = new_dfa_state
                    stack.append(new_nfa_state)
                else:
                    new_dfa_state = registered_states[new_nfa_state]
                row[char] = new_dfa_state

            # print()
            # print("Registered states:", registered_states)
            # print("Stack:", stack)
            # print("Row %d: %s" % (dfa_state, row))
            # print("\n----------------\n")

            if nfa.is_final(nfa_state):
                finals.add(registered_states[nfa_state])

        return data, finals

    def is_final(self, state):
        """Is the state a final state in the DFA?

        Parameters
        ----------
        state : a state of the DFA represented as an integer

        Returns
        -------
        result : boolean
        """
        return state in self.finals

    def match(self, string):
        """Match an input string.

        Parameters
        ----------
        string : an input string

        Returns
        -------
        result : boolean
        """
        state = 0
        for char in string:
            try:
                state = self.table[state][char]
            except KeyError:
                return False
        return self.is_final(state)


# ----------------------------------------------------------------------
#     Tests
# ----------------------------------------------------------------------

def main():
    # nfa = Nfa.concat(Nfa.char("a"), Nfa.union(Nfa.char("b"), Nfa.epsilon()))
    # print(nfa.match("ab"))
    # print(nfa.match("a"))

    # table = Table([{"a": {1}, "b": {2}}, {"a": {3}, "c": {4}}], default=set)
    # print(table)

    a = Nfa.char("a")
    b = Nfa.char("b")

    c = Nfa.concat(a, b)
    print(c)

    print()

    u = Nfa.union(a, b)
    print(u)

    print()

    s = Nfa.star(a)
    print(s)

    print()

    dfa = Dfa(u)
    print(dfa.table)
    print(dfa.finals)


if __name__ == "__main__":
    main()
