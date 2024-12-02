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

from pymathics.trepan.processor.command.base_cmd import DebuggerCommand


class ContinueCommand(DebuggerCommand):
    """**continue** [*location*]

    Leave the debugger read-eval print loop and continue
    execution. Subsequent entry to the debugger however may occur via
    breakpoints or explicit calls, or exceptions.

    If *location* is given, a temporary breakpoint is set at that
    position before continuing.

    Examples:
    ---------

        continue          # Continue execution

    See also:
    """

    aliases = ("c",)
    execution_set = ["Running", "Pre-execution"]
    short_help = "Continue execution of debugged program"
    DebuggerCommand.setup(locals(), category="running", max_args=1, need_stack=True)

    def run(self, args):
        self.core.step_events = None  # All events
        self.core.step_ignore = -1
        self.proc.continue_running = True  # Break out of command read loop
        return True

    pass


if __name__ == "__main__":
    import sys
    from pymathics.trepan.lib.repl import DebugREPL

    d = DebugREPL()
    cmd = ContinueCommand(d.core.processor)
    cmd.proc.frame = sys._getframe()
    cmd.proc.setup()

    for c in (
        ["continue", "wrong", "number", "of", "args"],
        ["continue"],
    ):
        d.core.step_ignore = 0
        cmd.continue_running = False
        result = cmd.run(c)
        print("Run result: %s" % result)
        print(
            "step_ignore %d, continue_running: %s"
            % (
                d.core.step_ignore,
                cmd.continue_running,
            )
        )
        pass
    pass
