# -*- coding: utf-8 -*-
#
#  Copyright (C) 2024 Rocky Bernstein
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
from pymathics.debugger.processor.command.base_cmd import DebuggerCommand


class BreakCommand(DebuggerCommand):
    """**break** [*options*] [if *condition*]]

    Sets a breakpoint, i.e. stopping point just before the
    execution of the event specified in *options*.

    Examples:
    ---------

       break --mpmath
       break --sympy
       break --numpy
    """

    aliases = ("b", "breakpoint")
    short_help = "Set breakpoint at specified line or function"

    DebuggerCommand.setup(locals(), category="breakpoints", need_stack=True)

    def run(self, args):

        break_opts = {
            "mpmath": False,
            "builtin": False,
            "sympy": False
        }

        try:
            opts, args = getopt(args[1:], "hmsn", "help".split())

        except GetoptError as err:
            # print help information and exit:
            print(str(err))  # will print something like "option -a not recognized"
            return
        return
        for o, _ in opts:
            if o in ("-h", "--help"):
                self.proc.commands["help"].run(["help", "backtrace"])
                return
            elif o in ("-b", "--builtin"):
                break_opts["builtin"] = True
            elif o in ("-e", "--expression"):
                break_opts["expression"] = True
            else:
                self.errmsg(f"unhandled option '{o}'")
            pass



if __name__ == "__main__":

    # def do_parse(cmd, a):
    #     name = "break"
    #     cmd.proc.current_command = name + " " + " ".join(a)
    #     print(a, "\n\t", parse_break_cmd(cmd.proc, [name] + a))

    # def do_run(cmd, a):
    #     name = "break"
    #     cmd.proc.current_command = name + " " + " ".join(a)
    #     print(a)
    #     cmd.run([name] + a)

    # import sys

    # from trepan.debugger import Trepan

    # d = Trepan()
    # command = BreakCommand(d.core.processor)
    # command.proc.frame = sys._getframe()
    # command.proc.setup()

    # do_parse(command, [""])
    # import inspect
    # line = inspect.currentframe().f_lineno
    # do_parse(command, [str(line)])
    # do_parse(command, ["%s:%s" % (__file__, line)])

    # def foo():
    #     return "bar"

    # do_parse(command, ["foo()"])
    # do_parse(command, ["os.path"])
    # do_parse(command, ["os.path", "5"])
    # import os.path
    # do_parse(command, ["os.path.join()"])
    # do_parse(command, ["if", "True"])
    # do_parse(command, ["foo()", "if", "True"])
    # do_parse(command, ["os.path:10", "if", "True"])

    # do_run(command, [""])
    # do_run(command, ["command.run()"])
    # do_run(command, ["89"])
    # command.run(["break", __file__ + ":10"])
    # command.run(["break", "foo"])
    pass
