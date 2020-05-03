"""
Parse operations like "and(or(eq(x, 1), eq(y, 2)), eq(z, 3))"
and return a dictionary in the form of

{
    "name": "and",
    "args": [
        {
            "name": "or",
            "args": [
                {
                    "name": "eq",
                    "args": ["x", "1"],
                },
                {
                    "name": "eq",
                    "args": ["y", "2"],
                }
            ]
        },
        {
            "name": "eq",
            "args": ["z", "3"]
        }
    ]
}
"""

from xparse.grammar import *
from xparse.parser import RecursiveDescentParser
from xparse.lexer import CharacterStream


# ----------------------------------------------------------------------------------------------------------------------
#       Actions
# ----------------------------------------------------------------------------------------------------------------------

def build_op(name, arguments):
    return {"name": name, "args": arguments}


def build_args(first, rest):
    if isinstance(rest, list):
        return [first] + rest
    return [first, rest]


# ----------------------------------------------------------------------------------------------------------------------
#       Grammar
# ----------------------------------------------------------------------------------------------------------------------

stmt = NonTerminal("stmt")
args = NonTerminal("args")
item = NonTerminal("item")
var = NonTerminal("var")
digit = NonTerminal("digit")

stmt += Terminal("a") + Terminal("(") + args + Terminal(")") >> Return(build_op, args=[0, 2]) \
      | Terminal("o") + Terminal("(") + args + Terminal(")") >> Return(build_op, args=[0, 2]) \
      | Terminal("e") + Terminal("(") + args + Terminal(")") >> Return(build_op, args=[0, 2]) \

args += stmt + Terminal(",") + args >> Return(build_args, args=[0, 2]) \
      | stmt \
      | item + Terminal(",") + args >> Return(build_args, args=[0, 2]) \
      | item

item += var \
      | digit

digit += Terminal("0") \
       | Terminal("1")

var += Terminal("x") \
     | Terminal("y") \
     | Terminal("z")


grammar = Grammar(stmt, args, item, digit, var)


# ----------------------------------------------------------------------------------------------------------------------
#       Parse
# ----------------------------------------------------------------------------------------------------------------------

lexer = CharacterStream(special_characters="aoe,xyz01()")
parser = RecursiveDescentParser(grammar, lexer, echo=False)


# parser.parse("e(x,y)")
parser.parse("a(e(0,1),e(x,y),e(0,0))")

print(parser.return_value)
