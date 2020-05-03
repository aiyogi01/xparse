from xparse.grammar import Terminal, NonTerminal, Epsilon, Return, Grammar
from xparse.parser import RecursiveDescentParser
from xparse.lexer import CharacterStream

from xparse.regular import Nfa


# -----------------------------------------------------------------------------
#     Grammar
# -----------------------------------------------------------------------------

union = NonTerminal('UNION')
concat = NonTerminal('CONCAT')
star = NonTerminal('STAR')
item = NonTerminal('ITEM')


union += concat + Terminal('|') + union >> Return(Nfa.union, args=[0, 2]) \
       | concat


concat += star + concat >> Return(Nfa.concat) \
        | star


star += item + Terminal('*') >> Return(Nfa.star, args=[0]) \
      | item + Terminal('?') >> Return(lambda x: Nfa.union(x, Nfa.epsilon()), args=[0]) \
      | item + Terminal('+') >> Return(lambda x: Nfa.concat(x, Nfa.star(x)), args=[0]) \
      | item


item += Terminal('(') + union + Terminal(')') >> Return(lambda x: x, args=[1]) \
      | Terminal('char') >> Return(Nfa.char)


regex_grammar = Grammar(union, concat, star, item)


# -----------------------------------------------------------------------------
#     Parse
# -----------------------------------------------------------------------------

lexer = CharacterStream(special_characters="()*|?+")
parser = RecursiveDescentParser(grammar=regex_grammar, lexer=lexer)

string = "(ab)+cd"

print(lexer.tokenize(string))

print("RESULT:")
print(parser.parse(string))

print("\nPARSE TREE:")
print(parser._stack)
print(str(parser.parse_tree))

print("\nLEAVES:")
print(parser.parse_tree.leaves)

print("\nRETURN VALUE:")
print(parser.return_value)

nfa = parser.return_value

print(nfa.match("abcd"))
print(nfa.match("ababcd"))
print(nfa.match("cd"))
