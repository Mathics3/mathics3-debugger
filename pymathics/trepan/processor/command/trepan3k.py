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
import sys

from pymathics.trepan.tracing import call_trepan3k

# Our local modules
from pymathics.trepan.processor.command.base_cmd import DebuggerCommand

class Trepan3KCommand(DebuggerCommand):
    """**trepan3k**

    Go into trepan3k debugger.
    """

    short_help = "Drop into the trepan3k debugger"

    DebuggerCommand.setup(locals(), category="data", max_args=0)

    def run(self, args):
        call_trepan3k(self.proc)


if __name__ == "__main__":
    from pymathics.trepan.lib.repl import DebugREPL

    d = DebugREPL()
    command = Trepan3KCommand(d.core.processor)
    command.proc.frame = sys._getframe()
    command.proc.setup()
    if len(sys.argv) > 1:
        print("Type Python commands and exit to quit.")
        print(sys.argv[1])
        print(command.run(["python"]))
    pass
