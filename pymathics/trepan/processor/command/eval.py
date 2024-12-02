# -*- coding: utf-8 -*-
#
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

from trepan.processor.command.base_cmd import DebuggerCommand
from pymathics.trepan.processor.frame import find_builtin

class EvalCommand(DebuggerCommand):
    """**eval** *Mathics3-statement*

    Run *Mathics3-statement* in the context of the current frame.
    A variable named evaluation must be found in the current frame
    for this to work.

    Use `up -b 0` to find most recent Python stack fram associated with
    eval()

    Examples:
    ---------

        eval 1+2  # 3
        eval      # Run current source-code line

    See also:
    ---------

    `printexpression`"""

    short_help = "Print value of Mathics3 expression EXP"

    DebuggerCommand.setup(locals(), category="data", need_stack=True)

    def run(self, args):
        if 1 == len(args):
            if self.proc.current_source_text:
                text = self.proc.current_source_text.rstrip("\n")
            else:
                self.errmsg("Don't have program source text")
                return
        else:
            text = self.proc.current_command[len(self.proc.cmd_name) :]
            pass
        text = text.strip()
        frame = find_builtin(self.proc.curframe)
        if frame is None:
            self.errmsg("Cannot find an eval frame to start with")
            return

        try:
            result = self.proc.eval_mathics_line(text, frame)
            self.proc.print_mathics_eval_result(result)

        except Exception:
            pass


# if __name__ == "__main__":
#     import inspect
#     from trepan.debugger import Trepan

#     d = Trepan()
#     cp = d.core.processor
#     cp.curframe = inspect.currentframe()
#     command = EvalCommand(cp)
#     me = 10

#     # command.run([command.name, '1+2'])
#     # command.run([command.name, 'if 5: x=1'])
#     pass
