# -*- coding: utf-8 -*-
#   Copyright (C) 2024 Rocky Bernstein
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
from pymathics.trepan.processor.command.up import UpCommand


class DownCommand(UpCommand):
    """**down** [*count*]

    *options* are:

       -h | --help    - give this help
       -b | --builtin - show Mathics3 builtin methods
       -e | --expr    - show Mathics3 Expressions

      Move the current frame down in the stack trace (to a newer frame). 0
      is the most recent frame. If no count is given, move down 1.

      See also:
      ---------

      `up` and `frame`."""

    signum = 1  # This is what distinguishes us from "up".
    short_help = "Move stack frame to a more recent selected frame"
    DebuggerCommand.setup(locals(), category="stack", need_stack=True, max_args=2)


if __name__ == "__main__":
    from pymathics.trepan.lib.repl import DebugREPL
    from trepan.processor.cmdproc import get_stack

    d = DebugREPL()
    cp = d.core.processor
    command = DownCommand(cp)
    command.run(["down"])

    def nest_me(command_proc, my_command, i):
        import inspect

        if i > 1:
            command_proc.curframe = inspect.currentframe()
            command_proc.stack, command_proc.curindex = get_stack(
                command_proc.curframe, None, None, command_proc
            )
            my_command.run(["down"])
            print("-" * 10)
            my_command.run(["down", "1"])
            print("-" * 10)
            my_command.run(["down", "-e", "1"])
            print("-" * 10)
            my_command.run(["down", "3"])
            print("-" * 10)
        else:
            nest_me(command_proc, my_command, i + 1)
        return

    cp.forget()
    nest_me(cp, command, 1)
    pass
