from typing import Optional, List, Union

from xparse.grammar import Terminal, NonTerminal, Action
from xparse.lexer import Token

__all__ = ['ParseTree']


class Leaf:
    
    def __init__(self, terminal: Terminal, token: Optional[Token] = None):
        self.terminal = terminal
        self.token = token

    def visual_str(self, indent=""):
        return indent + "Leaf('{}')".format(self.token.lexeme)

    def visual_repr(self, indent=""):
        return indent + "<Leaf(terminal={}, token={})".format(
            self.terminal, self.token)

    def __str__(self):
        return self.visual_str()

    def __repr__(self):
        return self.visual_repr()


class Node:
    def __init__(self, production=None, children=None):
        """Initialize a node from a production.

        Parameters
        ----------
        production : a production
            The production specifies the children of the node.

        children : children of the node (default= None)
            Collection of leafs, nodes or actions.

        """
        self.production = production
        self.children = children if children is not None else []

    def visual_str(self, indent=""):
        node = indent + "Node('{}')".format(self.production.head.name)
        children = [child.visual_str(indent + 4 * " ")
                    for child in self.children]
        return "\n".join([node] + children)

    def visual_repr(self, indent=""):
        node = indent + "<Node(head={}, production={})>".format(
            self.production.head.name, self.production)
        children = [child.visual_repr(indent + 4 * " ")
                    for child in self.children]
        return "\n".join([node] + children)

    def __str__(self):
        return self.visual_str()

    def __repr__(self):
        return self.visual_repr()

    def set_from_production(self, production):
        """Set the attributes of the node from a production.

        This methods adds a child to the node for each production
        element: it adds a leaf if a production element is a terminal,
        an empty node if a production element is a non-terminal,
        an action as it is.

        Parameters
        ----------
        production : a production
            The production specifies the children of the node.

        """
        self.production = production
        for element in production:
            if isinstance(element, Terminal):
                self.children.append(Leaf(element))
            elif isinstance(element, NonTerminal):
                self.children.append(Node())
            elif isinstance(element, Action):
                self.children.append(element)
            else:
                pass


class ParseTree:

    def __init__(self, tokens, productions):
        """Initialize a parse tree from tokens and productions.

        Parameters
        ----------
        tokens : a sequence of tokens
            A sequence of tokens which has been parsed by a parser.

        productions : a sequence of productions
            A sequence of productions that has been successfully applied
            by a top-down parser to parse the sequence of tokens.

        """
        self.root = Node() if productions else None
        self.leaves = []

        self._i = 0
        self._build_tree(self.root, productions)
        delattr(self, "_i")

        self._find_leaves()
        self._add_tokens(tokens)

        if self.root.production.return_value is not None:
            self.return_value = self._return_value(self.root)
        else:
            self.return_value = None

    def walk_tree(self, action=None):
        self._visit_node(self.root, action)

    def _build_tree(self, node, productions):
        # Get the current production from the productions stack
        # and initialise the node from the production.
        production = productions[self._i]
        node.set_from_production(production)
        # Increase the index pointing to the stack elements and
        # process all children of the node.
        self._i += 1
        for child in node.children:
            if isinstance(child, Node):
                self._build_tree(child, productions)

    def _visit_node(self, element, action=None):
        """Visit a node of a parse tree and all its descendants
        recursively.

        Apply an optional action to all visited elements.

        Parameters
        ----------
        element : an element of the parse tree
            The element can be a leaf, a node or an action

        action : a function to be applied to the element
            The function should take one parameter.

        """
        if action is not None:
            action(element)
        if isinstance(element, Node):
            for child in element.children:
                self._visit_node(child, action)

    def _register_leaf(self, node):
        if isinstance(node, Leaf):
            self.leaves.append(node)

    def _find_leaves(self):
        self.walk_tree(action=self._register_leaf)

    def _add_tokens(self, tokens: List[Token]):
        for leaf, token in zip(self.leaves, tokens):
            leaf.token = token

    def _return_value(self, node: Union[Node, Leaf]):
        if isinstance(node, Leaf):
            return node.token.lexeme
        elif isinstance(node, Node):
            if node.production.return_value is not None:
                action = node.production.return_value.func
            else:
                action = self._this
            args = [self._return_value(child) for child in node.children]
            if node.production.return_value is not None \
                    and node.production.return_value.args is not None:
                indices = node.production.return_value.args
                args = [args[i] for i in indices]
            return action(*args)
        else:
            raise TypeError("Not implemented!")

    @staticmethod
    def _this(x):
        return x

    def __str__(self):
        return str(self.root)

    def __repr__(self):
        return repr(self.root)
