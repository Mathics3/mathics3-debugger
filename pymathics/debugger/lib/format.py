from mathics.core.atoms import Atom
from mathics.core.element import BaseElement
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.rules import Rule
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import SymbolRule
from mathics_pygments.lexer import MathematicaLexer
from pygments import highlight
from pygments.formatters import Terminal256Formatter

# from mathics.core.pattern import Pattern


mma_lexer = MathematicaLexer()


def format_element(element: BaseElement) -> str:
    """
    Formats a Mathics3 element more like the way it might be
    entered, hiding some of the internal Element representation.

    This includes context markers on symbols, or internal
    object representations like ListExpression.
    """
    if isinstance(element, Symbol):
        # print("XXX is Symbol")
        return element.short_name
    elif isinstance(element, Atom):
        # print("XXX is atom")
        return str(element)
    elif isinstance(element, ListExpression):
        # print("XXX is atom")
        return "{%s}" % (
            ", ".join([format_element(element) for element in element.elements]),
        )
    # elif isinstance(element, Blank):
    #     # print("XXX is atom")

    #     return str(element)
    elif isinstance(element, Expression):
        # print("XXX is expression")
        if element.head is SymbolRule:
            return f"{format_element(element.elements[0])}->{format_element(element.elements[1])}"
        else:
            return f"{format_element(element.head)}[%s]" % (
                ", ".join([format_element(element) for element in element.elements]),
            )
    elif isinstance(element, Rule):
        # print("XXX is Symbol")
        return f"{format_element(element.pattern)}->{format_element(element.replace)}"
    return str(element)


def pygments_format(mathics_str: str, style) -> str:
    """Add terminial formatting for a Mathics3 string
    ``mathics_str``, using pygments style ``style``.
    """
    if style is None:
        return mathics_str
    terminal_formatter = Terminal256Formatter(style=style)
    return highlight(mathics_str, mma_lexer, terminal_formatter)
