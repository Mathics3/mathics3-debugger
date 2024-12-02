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

from pymathics.trepan.lib.stack import format_stack_entry, print_expression_stack
from trepan.lib.sighandler import (
    fatal_signals,
    SigHandler as TrepanSignalHandler,
    SignalManager as TrepanSignalManager,
    canonic_signame,
    lookup_signame,
    lookup_signum,
    yes_or_no,
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

    def initialize_handler(self, signame: str):
        if signame in fatal_signals:
            return False
        signum = lookup_signum(signame)
        if signum is None:
            return False

        try:
            old_handler = signal.getsignal(signum)
        except ValueError:
            # On some OS's (Redhat 8), SIGNUM's are listed (like
            # SIGRTMAX) that getsignal can't handle.
            old_handler = None
            if signame in self.sigs:
                self.sigs.pop(signame)
                pass

        if signame in self.ignore_list:
            self.sigs[signame] = SigHandler(
                self.dbgr,
                signame,
                signum,
                old_handler,
                None,
                False,
                print_stack=False,
                pass_along=True,
            )
        else:
            self.sigs[signame] = SigHandler(
                self.dbgr,
                signame,
                signum,
                old_handler,
                self.dbgr.intf[-1].msg,
                True,
                print_stack=False,
                pass_along=False,
            )
            pass
        return True

    pass


class SigHandler(TrepanSignalHandler):
    def handle(self, signum, frame):
        """This method is called when a signal is received."""
        core = self.dbgr.core
        if self.print_method:
            self.print_method(
                f"\n(Mathics3 Trepan) Program received signal {self.signame}."
            )
        if self.print_stack:
            # Print Python's most-recent frame
            frame_lineno = (frame, frame.f_lineno)
            self.print_method((" " * 9) +
                format_stack_entry(
                    self.dbgr, frame_lineno, style=self.dbgr.settings.get("style")
                ) + "\n"
            )
            # Print Mathics3 backtrace frames
            print_expression_stack(
                core.processor, 100, style=self.dbgr.settings.get("style")
            )
        if self.b_stop:
            old_trace_hook_suspend = core.trace_hook_suspend
            core.trace_hook_suspend = True
            core.stop_reason = f"intercepting signal {self.signame} ({signum})"
            core.processor.event_processor(frame, "signal", signum)
            core.trace_hook_suspend = old_trace_hook_suspend
            pass
        if self.pass_along:
            # pass the signal to the program
            if self.old_handler:
                self.old_handler(signum, frame)
                pass
            pass
        return

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

    # from pymathics.trepan.debugger import Trepan

    # dbgr = Trepan()
    # h = SignalManager(dbgr)
    # h.info_signal(["TRAP"])
    # # Set to known value
    # h.action("SIGUSR1")
    # h.action("usr1 print pass stop")
    # h.info_signal(["USR1"])
    # # noprint implies no stop
    # h.action("SIGUSR1 noprint")
    # h.info_signal(["USR1"])
    # h.action("foo nostop")
    # # stop keyword implies print
    # h.action("SIGUSR1 stop")
    # h.info_signal(["SIGUSR1"])
    # h.action("SIGUSR1 noprint")
    # h.info_signal(["SIGUSR1"])
    # h.action("SIGUSR1 nopass stack")
    # h.info_signal(["SIGUSR1"])
    # pass
