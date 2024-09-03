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

from optparse import OptionParser

# Our local modules
from pymathics.debugger.processor.command.base_cmd import DebuggerCommand
from pymathics.debugger.processor.frame import FrameType, adjust_relative, frame_complete

up_parser = OptionParser()
up_parser.add_option("-b", "--builtin", dest="builtin",
                     action="store_true", default=False)

up_parser.add_option("-e", "--expression", dest="expression",
                     action="store_true", default=False)

class UpCommand(DebuggerCommand):
    """**up** [options] [*count*]

    *options* are:

       -h | --help    - give this help
       -b | --builtin - show Mathics3 builtin methods
       -e | --expr    - show Mathics3 Expressions

        Move the current frame up in the stack trace (to an older frame). 0 is
        the most recent frame. If no count is given, move up 1.

    See also:
    ---------

    `down` and `frame`."""
    signum = -1  # This is what distinguishes us from "down"

    DebuggerCommand.setup(locals(), category="stack", need_stack=True, max_args=2)

    # TODO: adjust for options
    def complete(self, prefix):
        proc_obj = self.proc
        return frame_complete(proc_obj, prefix, self.signum)

    def run(self, args):

        opts, args = up_parser.parse_args(args[1:])

        frame_type = FrameType.python
        if opts.builtin:
            frame_type = FrameType.builtin
        elif opts.expression:
            frame_type = FrameType.expression

        adjust_relative(self.proc, self.name, args, self.signum, frame_type)
        return False


if __name__ == "__main__":
    from pymathics.debugger.lib.repl import DebugREPL
    from trepan.processor.cmdproc import get_stack

    d = DebugREPL()
    cp = d.core.processor
    command = UpCommand(cp)
    command.run(["up"])

    def nest_me(command_proc, my_command, i):
        import inspect

        if i > 1:
            command_proc.curframe = inspect.currentframe()
            command_proc.stack, command_proc.curindex = get_stack(
                command_proc.curframe, None, None, command_proc
            )
            my_command.run(["up"])
            print("-" * 10)
            my_command.run(["up", "1"])
            print("-" * 10)
            my_command.run(["up", "-e", "1"])
            print("-" * 10)
            my_command.run(["up", "3"])
            print("-" * 10)
        else:
            nest_me(command_proc, my_command, i + 1)
        return

    cp.forget()
    nest_me(cp, command, 1)
    pass
