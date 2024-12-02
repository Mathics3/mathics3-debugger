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

from getopt import getopt, GetoptError

# Our local modules
from pymathics.trepan.processor.command.base_cmd import DebuggerCommand
from pymathics.trepan.lib.stack import print_stack_trace


class BacktraceCommand(DebuggerCommand):
    """**backtrace** [*options*] [*count*]

    Print backtrace of all stack frames, or innermost *count* frames.

    An arrow indicates the 'current frame'. The current frame determines
    the context used for many debugger commands such as expression
    evaluation or source-line listing.

    *options* are:

       -h | --help    - give this help
       -b | --builtin - show Mathics3 builtin methods
       -e | --expr    - show Mathics3 Expressions

    Examples:
    ---------

       backtrace      # Print a full stack trace
       backtrace 2    # Print only the top two entries

    """

    aliases = ("bt", "where")
    short_help = "Print backtrace of stack frames"

    DebuggerCommand.setup(locals(), category="stack", max_args=4, need_stack=True)

    def run(self, args):

        try:
            opts, args = getopt(args[1:], "hbe", "help".split())
        except GetoptError as err:
            # print help information and exit:
            print(str(err))  # will print something like "option -a not recognized"
            return

        bt_opts = {
            "width": self.settings["width"],
            "builtin": False,
            "expression": False
        }
        # FIXME should convert opts -e and -b to Enum type and
        # check that it isn't set twice.
        for o, _ in opts:
            if o in ("-h", "--help"):
                self.proc.commands["help"].run(["help", "backtrace"])
                return
            elif o in ("-b", "--builtin"):
                bt_opts["builtin"] = True
            elif o in ("-e", "--expression"):
                bt_opts["expression"] = True
            else:
                self.errmsg(f"unhandled option '{o}'")
            pass

        if len(args) > 0:
            at_most = len(self.proc.stack)
            if at_most == 0:
                self.errmsg("Stack is empty.")
                return False
            min_value = -at_most + 1
            count = self.proc.get_int(
                args[0],
                min_value=min_value,
                cmdname="backtrace",
                default=0,
                at_most=at_most,
            )
            if count is None:
                return False
            if count < 0:
                count = at_most - count
                pass
            elif 0 == count:
                count = None
        else:
            count = None
            pass

        if not self.proc.curframe:
            self.errmsg("No stack.")
            return False
        print_stack_trace(
            self.proc, count, style=self.settings["style"], opts=bt_opts
        )
        return False

    pass


if __name__ == "__main__":
    from pymathics.trepan.processor import cmdproc
    from pymathics.trepan.lib.repl import DebugREPL

    d = DebugREPL()
    cp = d.core.processor
    command = BacktraceCommand(cp)
    command.run(["backtrace", "wrong", "number", "of", "args"])

    def nest_me(cp, command, i):
        import inspect

        if i > 1:
            cp.curframe = inspect.currentframe()
            cp.stack, cp.curindex = cmdproc.get_stack(cp.curframe, None, None, cp)
            print("-" * 10)
            command.run(["backtrace"])
            print("-" * 10)
            command.run(["backtrace", "1"])
        else:
            nest_me(cp, command, i + 1)
        return

    def ignore_me(cp, command, i):
        print("=" * 10)
        nest_me(cp, command, 1)
        print("=" * 10)
        cp.core.add_ignore(ignore_me)
        nest_me(cp, command, 1)
        return

    cp.forget()
    command.run(["backtrace"])
    print("-" * 10)
    ignore_me(cp, command, 1)
    command.run(["backtrace", "1"])
    print("-" * 10)
    command.run(["backtrace", "3"])
    print("-" * 10)
    pass
