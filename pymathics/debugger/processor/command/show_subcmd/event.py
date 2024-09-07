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

import mathics.eval.tracing as tracing
from mathics.core.rules import BuiltinRule

# Our local modules
from trepan.processor.command.base_subcmd import DebuggerSubcommand

from pymathics.debugger.tracing import (
    TraceEventNames,
    apply_builtin_fn_traced,
    apply_builtin_fn_print,
)


class ShowEvent(DebuggerSubcommand):
    """**set event** *event* {on|off|tracing}]

    Sets the Mathics events that the debugger will stop on. Event names are:
    `SymPy`, `mpmath`, and `NumPy`

    `all` can be used as an abbreviation for listing all event names.

    Examples:
    ---------

      show event Sympy
      show event

    See also:
    ---------

    `set trace`, `show trace`, and `show events`. `help step` lists event names.
    """

    in_list = True
    min_args = 0
    min_abbrev = len("ev")
    short_help = "Set execution-tracing event set"

    # FIXME: setting tracing defeats all debugging
    # Also, DRY this code

    def run(self, args):
        if len(args) == 0:
            args = TraceEventNames

        for event_name in args:
            if event_name not in TraceEventNames:
                self.errmsg(f"show event: Invalid argument {event_name} ignored.")
                return

            if event_name == "SymPy":
                replace_fn= tracing.run_sympy
                if replace_fn == tracing.run_sympy_traced:
                    status = "debug"
                elif replace_fn == tracing.call_event_print:
                    status = "tracing"
                else:
                    status = "off"
            elif event_name == "mpmath":
                replace_fn= tracing.run_mpmath
                if replace_fn == tracing.run_mpmath_traced:
                    status = "debug"
                elif replace_fn == tracing.call_event_print:
                    status = "tracing"
                else:
                    status = "off"
                status = (
                    "on" if tracing.run_mpmath == tracing.run_mpmath_traced else "off"
                )
            elif event_name == "apply":
                replace_fn = BuiltinRule.do_replace
                if replace_fn == apply_builtin_fn_traced:
                    status = "debug"
                elif replace_fn == apply_builtin_fn_print:
                    status = "tracing"
                else:
                    status = "off"
            elif event_name == "debugger":
                continue
            else:
                status = "??"

            self.msg(f"Event {event_name} is {status}")

    pass
    min_abbrev = len("ev")
    short_help = "Show event debugging"
    pass
