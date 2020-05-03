from xparse.grammar import Terminal, NonTerminal, Return, Grammar
from xparse.parser import RecursiveDescentParser
from xparse.lexer import CharacterStream


# -----------------------------------------------------------------------------
#     Grammar
# -----------------------------------------------------------------------------

# Non-terminals
stmt = NonTerminal("stmt")

# Productions
stmt += Terminal("+") + stmt + stmt >> Return(lambda x, y: x + y, args=[1, 2]) \
      | Terminal("-") + stmt + stmt >> Return(lambda x, y: x - y, args=[1, 2]) \
      | Terminal("digit") >> Return(int)

# Grammar
prefix_grammar = Grammar(stmt)


# -----------------------------------------------------------------------------
#     Parse
# -----------------------------------------------------------------------------

lexer = CharacterStream(
    admissible_characters="+-0123456789",
    special_characters="+-",
    general_class="digit")

parser = RecursiveDescentParser(grammar=prefix_grammar, lexer=lexer)

string = "-+12+34"

print("RESULT:")
print(parser.parse(string))

print("\nPARSE TREE:")
print(str(parser.parse_tree))
print(repr(parser.parse_tree))

print("\nLEAVES:")
print(parser.parse_tree.leaves)

print("\nRETURN VALUE:")
print(parser.return_value)

print(str(prefix_grammar))
