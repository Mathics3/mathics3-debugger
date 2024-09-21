from mathics.builtin.patterns import Blank, BlankNullSequence, BlankSequence, OptionsPattern, Pattern
from mathics.core.atoms import Atom
from mathics.core.element import BaseElement
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.pattern import AtomPattern, ExpressionPattern
from mathics.core.rules import FunctionApplyRule, Rule
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import SymbolRule
from mathics_pygments.lexer import MathematicaLexer
from pygments import highlight
from pygments.formatters import Terminal256Formatter

# from mathics.builtin.pattern import Pattern


mma_lexer = MathematicaLexer()


def format_element(element: BaseElement) -> str:
    """Formats a Mathics3 element more like the way it might be
    entered in Mathics3, hiding some of the internal Element representation.

    This includes removing some context markers on symbols, or
    internal object representations like ListExpression.

    """
    if isinstance(element, Symbol):
        return element.short_name
    elif isinstance(element, Atom):
        return str(element)
    elif isinstance(element, AtomPattern):
        return element.get_name(short=True)
    elif isinstance(element, (Blank, BlankNullSequence, BlankSequence)):
        if isinstance(element, Blank):
            name = "_"
        elif isinstance(element, BlankSequence):
            name = "__"
        else:
            name = "___"

        if len(element.expr.elements) == 0:
            return name
        else:
            return f"{name}.{element.expr.elements}"

    elif isinstance(element, FunctionApplyRule):
        function_class = element.function.__self__.__class__
        function_name = f"{function_class.__module__}.{function_class.__name__}"
        return f"{format_element(element.pattern)} -> {function_name}()"
    elif isinstance(element, (Expression, ExpressionPattern)):
        if element.head is SymbolRule:
            return f"{format_element(element.elements[0])} -> {format_element(element.elements[1])}"
        else:
            return f"{format_element(element.head)}[%s]" % (
                ", ".join([format_element(element) for element in element.elements]),
            )
    elif isinstance(element, ListExpression):
        return "{%s}" % (
            ", ".join([format_element(element) for element in element.elements]),
        )
    elif isinstance(element, OptionsPattern):
        return "{%s}" % (
            ", ".join([format_element(element) for element in element.elements]),
        )
    # FIXME handle other than 2 arguments...
    elif isinstance(element, Pattern) and len(element.elements) == 2:
        first_arg = element.elements[0]
        second_arg = element.elements[1]
        return f"{format_element(first_arg)}{format_element(second_arg)}"
    elif isinstance(element, Rule):
        return f"{format_element(element.pattern)} -> {format_element(element.replace)}"
    return str(element)


def pygments_format(mathics_str: str, style) -> str:
    """Add terminial formatting for a Mathics3 string
    ``mathics_str``, using pygments style ``style``.
    """
    if style is None:
        return mathics_str
    terminal_formatter = Terminal256Formatter(style=style)
    return highlight(mathics_str, mma_lexer, terminal_formatter)
