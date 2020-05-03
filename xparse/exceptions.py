"""
Module defining exceptions.
"""


class XParseException(Exception):
    """Base exception class."""


class GrammarError(XParseException):
    """Errors encountered in grammars."""


class LexerError(XParseException):
    """Errors encountered by a lexer."""


class ParserError(XParseException):
    """Errors encountered by a parser."""


class AutomatonError(XParseException):
    """Error encountered by a finite automaton."""
