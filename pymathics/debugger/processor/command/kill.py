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
import signal

# Our local modules
from trepan.processor.command.kill import KillCommand as TrepanKillCommand


class KillCommand(TrepanKillCommand):
    pass


if __name__ == "__main__":

    def handle(*args):
        print("signal received")
        pass

    signal.signal(28, handle)

    from trepan.processor.command import mock

    d, cp = mock.dbg_setup()
    command = KillCommand(cp)
    print(command.complete(""))
    command.run(["kill", "wrong", "number", "of", "args"])
    command.run(["kill", "28"])
    command.run(["kill!"])
