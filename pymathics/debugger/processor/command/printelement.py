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

from mathics.core.element import BaseElement
from mathics.core.pattern import AtomPattern, ExpressionPattern
from mathics.core.rules import FunctionApplyRule, Rule
from pymathics.debugger.processor.command.base_cmd import DebuggerCommand
from pymathics.debugger.lib.format import format_element, pygments_format

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

        if not isinstance(value, (AtomPattern, BaseElement, ExpressionPattern, FunctionApplyRule, Rule)):
            self.errmsg(f"text: {text} does not evaluate to a type I know about; is {type(value)}")
            return

        mathics_str = format_element(value)
        self.msg(pygments_format(mathics_str, self.settings["style"]))
    pass


if __name__ == "__main__":
    pass
