# -*- coding: utf-8 -*-
#   Copyright (C) 2024 Rocky Bernstein <rocky@gnu.org>
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
from pymathics.debugger.lib.stack import print_stack_trace


class InfoProgram(DebuggerSubcommand):
    """**info program**

    Execution status of the program. Listed are:

    * Most recent Mathics3 expression

    * Reason the program is stopped.

    """

    min_abbrev = 2  # Need at least "info pr"
    max_args = 0
    need_stack = True
    short_help = "Execution status of the program"

    def run(self, args):
        """Execution status of the program."""
        proc = self.proc
        if proc.event:
            msg = f"Mathics3 stop via a '{proc.event}' event."
            self.msg(msg)
        print_stack_trace(
            self.proc,
            1,
            style=self.settings["style"],
            opts={"expression": True, "builtin": False},
        )
        print_stack_trace(
            self.proc,
            1,
            style=self.settings["style"],
            opts={"expression": True, "builtin": True},
        )
        return


if __name__ == "__main__":
    from pymathics.debugger.processor.command import mock, info as Minfo

    d, cp = mock.dbg_setup()
    i = Minfo.InfoCommand(cp)
    sub = InfoProgram(i)
    sub.run([])
