# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2013-2014, 2016, 2022, 2023-2024
#   Rocky Bernstein <rocky@gnu.org>
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

"""Signal handlers."""

# TODO:
#  - Doublecheck handle_pass and other routines.
#  - can remove signal handler altogether when
#         ignore=True, print=False, pass=True
#
#
import signal

from trepan.lib.sighandler import (
    yes_or_no,
    lookup_signame,
    lookup_signum,
    canonic_signame,
    SignalManager as TrepanSignalManager,
)


class SignalManager(TrepanSignalManager):
    """Manages Signal Handling information for the debugger

    - Do we print/not print when signal is caught
    - Do we pass/not pass the signal to the program
    - Do we stop/not stop when signal is caught

    Parameter dbgr is a Debugger object. ignore is a list of
    signals to ignore. If you want no signals, use [] as None uses the
    default set. Parameter default_print specifies whether we
    print receiving a signals that is not ignored.

    All the methods which change these attributes return None on error, or
    True/False if we have set the action (pass/print/stop) for a signal
    handler.
    """

    def handle_print_stack(self, signame, print_stack):
        """Set whether we stop or not when this signal is caught.
        If 'set_stop' is True your program will stop when this signal
        happens."""
        self.sigs[signame].print_stack = print_stack
        return print_stack

    pass


# When invoked as main program, do some basic tests of a couple of functions
if __name__ == "__main__":

    for b in (
        True,
        False,
    ):
        print(f"yes_or_no of {repr(b)} is {yes_or_no(b)}")
        pass
    for signum in range(signal.NSIG):
        signame = lookup_signame(signum)
        if signame is not None:
            if not signame.startswith("SIG"):
                continue
            print(signame, signum, lookup_signum(signame))
            assert signum == lookup_signum(signame)
            # Try without the SIG prefix
            assert signum == lookup_signum(signame[3:])
            pass
        pass

    for i in (15, -15, 300):
        print("lookup_signame(%d): %s" % (i, lookup_signame(i)))
        pass

    for i in ("term", "TERM", "NotThere"):
        print(f"lookup_signum({i}): {repr(lookup_signum(i))}")
        pass

    for i in ("15", "-15", "term", "sigterm", "TERM", "300", "bogus"):
        print(f"canonic_signame({i}): {canonic_signame(i)}")
        pass

    from trepan.debugger import Trepan

    dbgr = Trepan()
    h = SignalManager(dbgr)
    h.info_signal(["TRAP"])
    # Set to known value
    h.action("SIGUSR1")
    h.action("usr1 print pass stop")
    h.info_signal(["USR1"])
    # noprint implies no stop
    h.action("SIGUSR1 noprint")
    h.info_signal(["USR1"])
    h.action("foo nostop")
    # stop keyword implies print
    h.action("SIGUSR1 stop")
    h.info_signal(["SIGUSR1"])
    h.action("SIGUSR1 noprint")
    h.info_signal(["SIGUSR1"])
    h.action("SIGUSR1 nopass stack")
    h.info_signal(["SIGUSR1"])
    pass
