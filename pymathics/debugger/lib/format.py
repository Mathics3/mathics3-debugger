from mathics.builtin.patterns.basic import Blank, BlankNullSequence, BlankSequence
from mathics.builtin.patterns.composite import Pattern, OptionsPattern
from mathics.builtin.patterns.rules import RuleDelayed
from mathics.core.atoms import Atom
from mathics.core.element import BaseElement
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.pattern import AtomPattern, ExpressionPattern
from mathics.core.rules import FunctionApplyRule, Rule
from mathics.core.symbols import Symbol, SymbolList
from mathics.core.systemsymbols import (
    SymbolBlank,
    SymbolBlankNullSequence,
    SymbolBlankSequence,
    SymbolPattern,
    SymbolRule,
    SymbolRuleDelayed,
)
from mathics_pygments.lexer import MathematicaLexer
from pygments import highlight
from pygments.formatters import Terminal256Formatter

# from mathics.builtin.pattern import Pattern


mma_lexer = MathematicaLexer()


def format_list(elements: tuple) -> str:
    """
    Return Mathics3 string using the elements of a List[]
    M-expression or ListExpression object
    """
    return "{%s}" % (", ".join([format_element(element) for element in elements]),)


def format_pattern(elements: tuple) -> str:
    """
    Return Mathics3 string using the elemnents of a Pattern[] M-expression
    or Pattern object
    """
    assert len(elements) == 2
    first_arg = elements[0]
    second_arg = elements[1]
    return f"{format_element(first_arg)}{format_element(second_arg)}"


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
            return (
                f"{name}"
                f"{', '.join([format_element(element) for element in element.elements])}"
            )

    elif isinstance(element, FunctionApplyRule):
        function_class = element.function.__self__.__class__
        function_name = f"{function_class.__module__}.{function_class.__name__}"
        return f"{format_element(element.pattern)} -> {function_name}()"
    # Note ListExpression test has to come before Expression test since
    # ListExpression is a subclass of Expression
    elif isinstance(element, ListExpression):
        return format_list(element.elements)
    elif isinstance(element, (Expression, ExpressionPattern)):
        head = element.head
        # We handle printing "Expression"s which haven't been converted to an internal data structure yet
        # for example Expression[List, Integer1, Integer2] instead of ListExpression[Integer1, Integer2]
        if head is SymbolList:
            return format_list(element.elements)
        elif head is SymbolPattern and len(element.elements) == 2:
            return format_pattern(element.elements)
        elif head is SymbolRule:
            return f"{format_element(element.elements[0])} -> {format_element(element.elements[1])}"
        elif head is SymbolRuleDelayed:
            return f"{format_element(element.elements[0])} :> {format_element(element.elements[1])}"
        elif head in (SymbolBlank, SymbolBlankNullSequence, SymbolBlankSequence):
            if head is SymbolBlank:
                name = "_"
            elif head is SymbolBlankSequence:
                name = "__"
            else:
                name = "___"

            if len(element.elements) == 0:
                return name
            else:
                return (
                    f"{name}"
                    f"{', '.join([format_element(element) for element in element.elements])}"
                )

        else:
            # A general Expression.
            return f"{format_element(head)}[%s]" % (
                ", ".join([format_element(element) for element in element.elements]),
            )
    elif isinstance(element, OptionsPattern):
        return "{%s}" % (
            ", ".join([format_element(element) for element in element.elements]),
        )
    # FIXME handle other than 2 arguments...
    elif isinstance(element, Pattern) and len(element.elements) == 2:
        return format_pattern(element.elements)
    elif isinstance(element, Rule):
        return f"{format_element(element.pattern)} -> {format_element(element.replace)}"
    elif isinstance(element, RuleDelayed):
        return f"{format_element(element.pattern)} :> {format_element(element.replace)}"
    return str(element)


def pygments_format(mathics_str: str, style) -> str:
    """Add terminial formatting for a Mathics3 string
    ``mathics_str``, using pygments style ``style``.
    """
    if style is None:
        return mathics_str
    terminal_formatter = Terminal256Formatter(style=style)
    return highlight(mathics_str, mma_lexer, terminal_formatter)
