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

import mathics.eval.files_io.files as io_files

from trepan.processor.command.base_subcmd import DebuggerSubcommand

import mathics.eval.tracing as tracing
from pymathics.trepan.__main__ import EVALUATION_APPLY

from pymathics.trepan.tracing import (
    TraceEventNames,
    apply_builtin_fn_traced,
    apply_builtin_fn_print,
    call_event_debug,
    call_event_get,
)
from mathics.core.rules import FunctionApplyRule

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
                self.errmsg("set event: expecting another argument: 'on', 'off', 'trace' or 'debug'")
                return
            on_off = args[i]
            i += 1
            if on_off not in ("on", "off", "trace", "debug"):
                self.errmsg(f"set events: expecting argument: 'on', 'off', 'trace' or 'debug'; got: '{on_off}'")
                return

            if event_name in ("Get", "all"):
                if on_off in ("on", "debug"):
                    io_files.GET_PRINT_FN = call_event_get
                elif on_off == "trace":
                    io_files.GET_PRINT_FN = io_files.print_line_number_and_text
                else:
                    io_files.GET_PRINT_FN = None

            elif event_name in ("SymPy", "all"):
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
                    FunctionApplyRule.apply_function = apply_builtin_fn_traced
                elif on_off == "trace":
                    FunctionApplyRule.apply_function = apply_builtin_fn_print
                else:
                    FunctionApplyRule.apply_function = EVALUATION_APPLY


    pass


if __name__ == "__main__":
    from pymathics.trepan.processor.command import mock, set as Mset

    d, cp = mock.dbg_setup()
    s = Mset.SetCommand(cp)
    sub = SetEvent(s)
    sub.name = "event"
    for args in (("mpmath", "trace"), ("SymPy", "debug"), ("SymPy", "foo"), ("bogus",)):
        sub.run(args)
        pass
    pass
