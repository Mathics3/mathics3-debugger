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

import inspect

# Our local modules
from trepan.processor.command.info_subcmd.args import InfoArgs as TrepanInfoArgs


class InfoArgs(TrepanInfoArgs):
    __doc__ = TrepanInfoArgs.__doc__
    pass


if __name__ == "__main__":
    from pymathics.trepan.processor.command import mock, info as Minfo

    d, cp = mock.dbg_setup()
    i = Minfo.InfoCommand(cp)
    sub = InfoArgs(i)
    print(sub.run([]))
    cp.curframe = inspect.currentframe()
    print(sub.run([]))

    def nest_me(sub, cp, b=1):
        cp.curframe = inspect.currentframe()
        print(sub.run([]))
        return

    print("-" * 10)
    nest_me(sub, cp, 3)
    print("-" * 10)
    nest_me(sub, cp)
    pass
