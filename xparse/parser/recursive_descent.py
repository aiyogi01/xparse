from typing import Optional, List

from xparse.grammar import Terminal, NonTerminal, Epsilon, Production, Action
from xparse.parser.parse_tree import ParseTree
from xparse.lexer import Token

_INDENT = "  "


class RecursiveDescentParser:
    """
    A recursive-descent parser.
    """
    def __init__(self, grammar, lexer, echo=False):
        """Instantiate a parser from a context-free grammar and a lexer.

        Parameters
        ----------
        grammar : a context free grammar
            The grammar is contained in a Grammar object from the module
            `grammar.py`.

        lexer : a lexer

        echo : echo the parser proceedings on the screen? (default= False)
        """
        self.grammar = grammar
        self.lexer = lexer
        self.echo = echo

        self.parse_tree = None
        self.return_value = None

        self._tokens = []       # type: List[Token]
        self._lookahead = None  # type: Optional[int]
        self._stack = []        # type: List[Production]

    def parse(self, string: str):
        """Parse an input string.

        First, a lexical analysis of the input string is performed by
        the lexer. Next, the parser performs a syntactical analysis on
        the token sequence.

        Parameters
        ----------
        string : an input string

        Returns
        -------
        result : boolean
        """
        self._reset(tokens=self.lexer.tokenize(string))
        if self._scan():
            self.parse_tree = ParseTree(
                tokens=self._tokens, productions=self._stack)
            self.return_value = self.parse_tree.return_value
            return True
        return False

    def _echo(self, message, indent=""):
        """Echo a message on the standard output stream.

        Parameters
        ----------
        message : a message to be printed

        indent : indent to print before the message
        """
        if self.echo:
            print(indent + message)

    def _reset(self, tokens):
        """Reset all attributes of the parser so that a new token
        sequence can be parsed.

        Parameters
        ----------
        tokens : a sequence of tokens
        """
        self._tokens = tokens
        self._lookahead = 0
        self._stack = []
        self.parse_tree = None
        self.return_value = None

    def _scan(self):
        """Scan the token stream produced by the lexer.

        Returns
        -------
        result : boolean
            The return value indicates whether the syntactical analysis
            has succeeded or not.

        """
        result = self._match_production_element(self.grammar[0])
        if not result or self._lookahead is not None:
            return False
        return True

    def _match_production(self, production, level=0):
        """Match a production.

        All matched terminals of a successfully matched production
        update the lookahead.

        Parameters
        ----------
        production : a production
            The production consists of terminals, non-terminals and
            optional actions.

        Returns
        -------
        result : bool
        """
        indent = _INDENT * level
        self._echo("Trying: %s " % str(production), indent=indent)

        save = self._lookahead
        for element in production:
            if not self._match_production_element(element, level + 1):
                self._lookahead = save
                self._echo("Failed!", indent=indent)
                return False
        self._echo("Succeeded!", indent=indent)
        return True

    def _match_production_element(self, production_element, level=0):
        """Switch function for the type of the production element.

        The production element can be a terminal, a non-terminal, an
        epsilon or an action. Choose and apply a corresponding match
        function.

        Parameters
        ----------
        production_element : a production element
            The production element can be a terminal, a non-terminal,
            an epsilon or an action.

        Returns
        -------
        result : bool
        """
        if isinstance(production_element, Terminal):
            return self._match_terminal(production_element)
        elif isinstance(production_element, NonTerminal):
            return self._match_non_terminal(production_element, level)
        elif isinstance(production_element, Epsilon):
            return True
        elif isinstance(production_element, Action):
            raise TypeError("Action not supported yet!")
        else:
            raise TypeError("Ha ha!")

    def _match_non_terminal(self, non_terminal, level=0):
        """Match a non-terminal.

        All production rules for the non-terminal are tried successively,
        and the successful production is pushed onto the stack.

        All terminals of the successful production update the lookahead.

        Parameters
        ----------
        non_terminal : a non-terminal
            The non-terminal should contain a sequence of production
            alternatives which can be tried successively by the parser.

        Returns
        -------
        result : bool
        """
        save = len(self._stack)
        for production in non_terminal:
            self._stack.append(production)
            if self._match_production(production, level):
                return True
            self._stack = self._stack[:save]
        return False

    def _match_terminal(self, terminal):
        """Match a terminal.

        The terminal will be matched against the token class of he token
        at which the lookahead points. A successively matched terminal
        updates the lookahead.

        Parameters
        ----------
        terminal : a terminal

        Returns
        -------
        result : bool
        """
        if self._lookahead is None:
            return False
        token_category = self._tokens[self._lookahead].category
        if token_category == terminal.name:
            self._advance_lookahead()
            return True
        return False

    def _advance_lookahead(self):
        """Advance the lookahead.

        If the end of the token stream is reached the lookahead is set
        to None. Otherwise the lookahead is increased by 1.
        """
        if self._lookahead is not None:
            increased = self._lookahead + 1
            self._lookahead = None if increased >= len(
                self._tokens) else increased
