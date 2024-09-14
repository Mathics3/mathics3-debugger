# -*- coding: utf-8 -*-
#   Copyright (C) 2024 Rocky Bernstein
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Our local modules
from trepan.processor.command.base_subcmd import DebuggerSubcommand

import mathics.eval.tracing as tracing
from pymathics.debugger.__main__ import EVALUATION_APPLY

from pymathics.debugger.tracing import (
    TraceEventNames,
    apply_builtin_fn_traced,
    apply_builtin_fn_print,
    call_event_debug,
)
from mathics.core.rules import BuiltinRule

class SetEvent(DebuggerSubcommand):

    """**set event** *event* {on|off|trace}]

    Sets the Mathics events that the debugger will stop on. Event names are:
    `SymPy`, `mpmath`, and `NumPy`

    `all` can be used as an abbreviation for listing all event names.

    Examples:
    ---------

      set event SymPy on            # Turn SymPy tracing on
      set event Sympy off NumPy on
      set event mpmath trace        # trace calls but don't stop
      set event all off             # Turn trace filter off for aall events.

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
        valid_args = list(TraceEventNames) + ["all"]
        i = 0
        while i < len(args):
            arg = args[i]
            if arg not in valid_args:
                self.errmsg(f"set event: Invalid argument {arg} ignored.")
                return
            i += 1
            event_name = arg
            if i >= len(args):
                self.errmsg("set event: expecting another argument: 'on', 'off', 'tracing' or 'debug'")
                return
            on_off = args[i]
            i += 1
            if on_off not in ("on", "off", "trace", "debug"):
                self.errmsg("set events: expecting another argument: 'on', 'off', 'tracing' or 'debug'")
                return

            if event_name in ("SymPy", "all"):
                if on_off in ("on", "debug"):
                    tracing.hook_entry_fn = call_event_debug
                    tracing.run_sympy = tracing.run_sympy_traced
                elif on_off == "trace":
                    tracing.hook_entry_fn = tracing.call_event_print
                    tracing.run_sympy = tracing.run_sympy_traced
                else:
                    tracing.run_sympy = tracing.run_fast

            elif event_name in ("mpmath", "all"):
                if on_off in ("on", "debug"):
                    tracing.hook_entry_fn = call_event_debug
                    tracing.run_mpmath = tracing.run_mpmath_traced
                elif on_off == "trace":
                    tracing.hook_entry_fn = tracing.call_event_print
                    tracing.run_mpmath = tracing.run_mpmath_traced
                else:
                    tracing.run_mpmath = tracing.run_fast

            elif event_name in ("apply", "all"):
                if on_off in ("on", "debug"):
                    BuiltinRule.apply_rule = apply_builtin_fn_traced
                elif on_off == "trace":
                    BuiltinRule.apply_rule = apply_builtin_fn_print
                else:
                    BuiltinRule.apply_rule = EVALUATION_APPLY


    pass


if __name__ == "__main__":
    from pymathics.debugger.processor.command import mock, set as Mset

    d, cp = mock.dbg_setup()
    s = Mset.SetCommand(cp)
    sub = SetEvent(s)
    sub.name = "event"
    for args in (("mpmath", "trace"), ("SymPy", "debug"), ("SymPy", "foo"), ("bogus",)):
        sub.run(args)
        pass
    pass
