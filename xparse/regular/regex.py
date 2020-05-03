from xparse.grammar import Terminal, NonTerminal, Return, Grammar
from xparse.regular import Nfa, Dfa
from xparse.lexer import CharacterStream
from xparse.parser import RecursiveDescentParser

from xparse.exceptions import *


__all__ = ["match", "compile"]


# ----------------------------------------------------------------------
#       Grammar
# ----------------------------------------------------------------------

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


grammar = Grammar(union, concat, star, item)


# ----------------------------------------------------------------------
#       Match function
# ----------------------------------------------------------------------

lexer = CharacterStream(special_characters="()*|?+", general_class="char", escape_character="\\")
parser = RecursiveDescentParser(grammar=grammar, lexer=lexer)


def compile(pattern):
    parser.parse(pattern)
    nfa = parser.return_value
    dfa = Dfa(nfa)
    return dfa


def match(pattern, string):
    if isinstance(pattern, str):
        automaton = compile(pattern)
    elif isinstance(pattern, (Nfa, Dfa)):
        automaton = pattern
    else:
        raise AutomatonError("First argument should be a sting or a finite automaton.")
    return automaton.match(string)


# ----------------------------------------------------------------------
#       Testing
# ----------------------------------------------------------------------

def main():
    import re
    import time

    # pattern = "(a?a?)*b"
    # string = "aaaaaaaaaaaa"
    pattern = "(a|b)*c"
    string = "abc"

    c1 = compile(pattern)
    c2 = re.compile(pattern)

    start = time.time()
    for _ in range(1000):
        r = match(c1, string)
        delta = time.time() - start
    print("Homebrew: %s, in: %s" % (r, delta))

    start = time.time()
    for _ in range(1000):
        r = re.match(c2, string)
        delta = time.time() - start
    print("Standard: %s, in: %s" % (bool(r), delta))


if __name__ == "__main__":
    main()
