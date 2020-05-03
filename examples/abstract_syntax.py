from xparse.grammar import Terminal, NonTerminal, Return, Grammar
from xparse.parser import RecursiveDescentParser
from xparse.lexer import CharacterStream


class AST:
    """
    Abstract syntax tree.
    """
    def __init__(self, node, *children):
        self.node = node
        self.children = children

    def to_list(self):
        if not self.children:
            return self.node
        else:
            children_ast = [child.to_list()
                            if isinstance(child, AST) else child
                            for child in self.children]
            return [self.node] + children_ast


# -----------------------------------------------------------------------------
#     Grammar
# -----------------------------------------------------------------------------

# Non-terminals
stmt = NonTerminal("stmt")

# Productions
stmt += Terminal("+") + stmt + stmt >> Return(AST) \
      | Terminal("-") + stmt + stmt >> Return(AST) \
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
# print(repr(parser.parse_tree))

print("\nLEAVES:")
print(parser.parse_tree.leaves)

print("\nRETURN VALUE:")
print(parser.return_value)
ast = parser.return_value
print(ast.to_list())

print("\nGRAMMAR:")
print(str(prefix_grammar))
