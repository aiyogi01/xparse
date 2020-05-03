from typing import List, Union, Optional, Callable, Tuple


__all__ = ["Terminal", "NonTerminal", "Epsilon", "Action", "Return", "Production", "Grammar"]


# ----------------------------------------------------------------------
#       Action
# ----------------------------------------------------------------------

class Action:
    """
    Class for defining a parser action.
    """
    def __init__(self, func):
        self.func = func


# ----------------------------------------------------------------------
#       Return
# ----------------------------------------------------------------------

class Return:
    """
    Class for defining a return function of a production.
    """
    def __init__(self,
                 func: Callable,
                 args: Optional[Union[Tuple[int, ...], List[int]]] = None):
        self.func = func
        self.args = args


# ----------------------------------------------------------------------
#       Epsilon
# ----------------------------------------------------------------------

class Epsilon:
    pass


# ----------------------------------------------------------------------
#       Terminal
# ----------------------------------------------------------------------

class Terminal:
    """
    Class for defining a terminal symbol.
    """
    def __init__(self, name: str):
        """Instantiate a terminal from a name.

        Parameters
        ----------
        name : name of the terminal
        """
        self.name = name

    def __str__(self):
        """String representation."""
        return "'{}'".format(self.name)

    def __repr__(self):
        """Extended string representation for debugging."""
        return "Terminal('{}')".format(self.name)

    def __add__(self, other):
        """Combine the terminal with another object to form a
        production (use +).

        Examples
        --------
        Create a production which consists of the two terminals 'A' and 'B'.

        >>> production = Terminal('A') + Terminal('B')


        Parameters
        ----------
        other : another terminal, non-terminal, epsilon or action

        Returns
        -------
        production : a new production
            The newly constructed production consists of the terminal
            and the other object.
        """
        return Production(self, other)

    def __or__(self, other):
        """Combine the terminal with another object to form production
        alternatives (use |).

        Examples
        --------
        Create two productions the first of which consist of the
        terminal 'A' and second of the terminals 'B' and 'C'.

        >>> productions = Terminal('A') | Terminal('B') + Terminal('C')


        Parameters
        ----------
        other : another terminal, non-terminal, epsilon or action

        Returns
        -------
        productions : a ProductionAlternatives object
        """
        if isinstance(other, (Terminal, NonTerminal, Epsilon)):
            return ProductionAlternatives(Production(self), Production(other))
        else:
            raise TypeError("Unexpected type")

    def __rshift__(self, other):
        """Combine the terminal with a Return object to form a
        production (use >>).

        Examples
        --------
        Create a production which consists of the terminal 'number' and
        returns a Python integer.

        >>> production = Terminal('number') >> Return(int)


        Parameters
        ----------
        other : a Return object

        Returns
        -------
        production : a new production with the Return object
        """
        if isinstance(other, Return):
            return Production(self, return_value=other)
        else:
            raise TypeError("Unsupported type")


# ----------------------------------------------------------------------
#       NonTerminal
# ----------------------------------------------------------------------

class NonTerminal:
    """
    Class for defining a non-terminal symbol.
    """
    def __init__(self, name):
        self.name = name
        self.productions = ProductionAlternatives()

    def __str__(self):
        return self.name

    def __repr__(self):
        return "NonTerminal('{}')".format(self.name)

    def __add__(self, other):
        return Production(self, other)

    def __or__(self, other):
        if isinstance(other, (Terminal, NonTerminal, Epsilon)):
            return ProductionAlternatives(Production(self), Production(other))
        elif isinstance(other, Production):
            return ProductionAlternatives(Production(self), other)
        else:
            raise TypeError("Unsupported type")

    def __iadd__(self, other):
        if isinstance(other, (Terminal, NonTerminal, Epsilon)):
            self.productions = ProductionAlternatives(Production(other))
            self._set_head()
            return self
        elif isinstance(other, Production):
            self.productions = ProductionAlternatives(other)
            self._set_head()
            return self
        elif isinstance(other, ProductionAlternatives):
            self.productions = other
            self._set_head()
            return self
        else:
            raise TypeError("Unsupported type")

    def __iter__(self):
        return iter(self.productions)

    def __getitem__(self, item):
        return self.productions[item]

    def __rshift__(self, other):
        if isinstance(other, Return):
            return Production(self, return_value=other)
        else:
            raise TypeError("Unsupported type")

    def _set_head(self):
        for production in self.productions:
            production.head = self


# ----------------------------------------------------------------------
#       Production
# ----------------------------------------------------------------------

class Production:

    def __init__(self, *elements, return_value: Optional[Return] = None):
        self.head = None
        self.elements = list(elements)
        self.return_value = return_value

    def __str__(self):
        head = self.head.name if self.head is not None else "N.A."
        body = " ".join(str(x) for x in self.elements)
        return head + " -> " + body

    def __repr__(self):
        return "<Production: {}; Return: {}>".format(
            " ".join(repr(x) for x in self.elements),
            None if self.return_value is None else
            self.return_value.func.__name__
        )

    def __add__(self, element):
        if isinstance(element, (Terminal, NonTerminal)):
            return Production(*self.elements, element)
        else:
            raise TypeError("Unsupported type")

    def __or__(self, other):
        if isinstance(other, (Terminal, NonTerminal)):
            return ProductionAlternatives(self, Production(other))
        elif isinstance(other, Production):
            return ProductionAlternatives(self, other)
        else:
            raise TypeError("Unsupported type")

    def __iter__(self):
        return iter(self.elements)

    def __rshift__(self, other):
        if isinstance(other, Return):
            self.return_value = other
            return self
            # return Production(*self.elements, return_value=other)
        else:
            raise TypeError("Unsupported type")

    def strip(self) -> List[Union[Terminal, NonTerminal]]:
        return [element for element in self.elements
                if isinstance(element, (Terminal, NonTerminal))]


# ----------------------------------------------------------------------
#       Production Alternatives
# ----------------------------------------------------------------------

class ProductionAlternatives:

    def __init__(self, *productions):
        self.productions = productions

    def __str__(self):
        return " | ".join(str(x) for x in self.productions)

    def __repr__(self):
        return "ProductionBody: [ {} ]".format(
            " | ".join(repr(x) for x in self.productions))

    def __or__(self, other):
        if isinstance(other, (Terminal, NonTerminal, Epsilon)):
            return ProductionAlternatives(*self.productions, Production(other))
        elif isinstance(other, Production):
            return ProductionAlternatives(*(self.productions + (other,)))
        else:
            raise TypeError("Unsupported type")

    def __iter__(self):
        return iter(self.productions)

    def __getitem__(self, item):
        return self.productions[item]


# ----------------------------------------------------------------------
#       Grammar
# ----------------------------------------------------------------------

class Grammar:

    def __init__(self, *non_terminals):
        self.non_terminals = non_terminals
        self._dict = {
            non_terminal.name: non_terminal for non_terminal in non_terminals
        }

    def __str__(self):
        strings = []
        for non_terminal in self.non_terminals:
            head = non_terminal.name
            body = str(non_terminal.productions)
            strings.append(head + " -> " + body)
        return "\n".join(strings)

    def __iter__(self):
        return iter(self.non_terminals)

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.non_terminals[item]
        elif isinstance(item, str):
            return self._dict[item]
        elif isinstance(item, NonTerminal):
            return self._dict[item.name]
        else:
            raise TypeError("Unsupported type")

    def get_production(self, item: Union[str, int], index: int):
        return self[item][index]
