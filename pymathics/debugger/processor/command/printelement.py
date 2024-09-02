# -*- coding: utf-8 -*-
#  Copyright (C) 2024 Rocky Bernstein
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from mathics.core.atoms import Atom
from mathics.core.element import BaseElement
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
# from mathics.core.pattern import Pattern
from mathics.core.symbols import Symbol

from pymathics.debugger.processor.command.base_cmd import DebuggerCommand

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
        return f"{format_element(element.head)}[%s]" % (
            ", ".join([format_element(element) for element in element.elements]),
        )
    return str(element)


class PrintElementCommand(DebuggerCommand):
    """**printelement** [*Mathics3 element*]

    Print a Mathics3 *expression* formatted nicely, as opposed to
    its Python-object way.
    """

    aliases = ("print-element", "pexp", "pe")
    execution_set = ["Running"]
    short_help = "Print a Mathics3 Expression nicely"
    DebuggerCommand.setup(locals(), category="running", max_args=1, need_stack=True)

    def run(self, args):
        text = self.proc.current_command[len(self.proc.cmd_name) :]
        text = text.strip()
        try:
            value = self.proc.eval(text)
        except Exception:
            return

        if not isinstance(value, BaseElement):
            self.errmsg(f"text: {text} does not evaluate to an Element type (is {type(value)}")
            return

        self.msg(format_element(value))
    pass


if __name__ == "__main__":
    pass
