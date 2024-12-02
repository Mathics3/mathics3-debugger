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

# Our local modules
from trepan.processor.command.alias import AliasCommand as TrepanAliasCommand


class AliasCommand(TrepanAliasCommand):
    pass

if __name__ == "__main__":
    # Demo it.
    from pymathics.trepan.processor.command import mock

    d, cp = mock.dbg_setup()
    command = AliasCommand(cp)
    command.run(["alias", "yy", "foo"])
    command.run(["alias", "yy", " foo"])
    command.run(["alias", "yy" "step"])
    command.run(["alias"])
    command.run(["alias", "yy" "next"])
    pass
