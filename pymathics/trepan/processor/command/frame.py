# -*- coding: utf-8 -*-
# FIXME: DRY with trepan3k by importing modules

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

import inspect
import threading

from optparse import OptionParser

from trepan.lib import thred as Mthread
from trepan.lib.complete import complete_token
from trepan.processor.cmdproc import get_stack

# Our local modules
from trepan.processor.command.base_cmd import DebuggerCommand
from pymathics.trepan.processor.frame import FrameType, adjust_frame, frame_low_high


frame_parser = OptionParser()
frame_parser.add_option("-b", "--builtin", dest="builtin",
                     action="store_true", default=False)

frame_parser.add_option("-e", "--expression", dest="expression",
                        action="store_true", default=False)

class FrameCommand(DebuggerCommand):
    """**frame** [*frame-number*]

    Change the current frame to frame *frame-number* if specified, or the
    current frame, 0, if no frame number specified.

    A negative number indicates the position from the other or
    least-recently-entered end.  So `frame -1` moves to the oldest frame,
    and `frame 0` moves to the newest frame. Any variable or expression
    that evaluates to a number can be used as a position, however due to
    parsing limitations, the position expression has to be seen as a single
    blank-delimited parameter. That is, the expression `(5*3)-1` is okay
    while `(5 * 3) - 1)` isn't.

    **Examples:**

       frame       # Set current frame at the current stopping point
       frame 0     # Same as above
       frame B:0   # Go to the most recent builtin expression frame
       frame E:0   # Go to the most frame having an expression argument
       frame e:0   # same as above
       frame -1    # Go to the least-recent frame
       frame E:-1  # Go to the least-recent expression
       frame MainThread 0 # Switch to frame 0 of thread MainThread
       frame MainThread   # Same as above

    See also:
    ---------

    `up`, `down`, `backtrace`, and `info threads`."""

    short_help = "Select and print a stack frame"

    DebuggerCommand.setup(locals(), category="stack", max_args=2, need_stack=True)

    def complete(self, prefix):
        proc_obj = self.proc
        low, high = frame_low_high(proc_obj, None)
        ary = [str(low + i) for i in range(high - low + 1)]
        # FIXME: add in Thread names
        return complete_token(ary, prefix)

    def find_and_set_debugged_frame(self, frame, thread_id):
        """The dance we have to do to set debugger frame state to
        *frame*, which is in the thread with id *thread_id*. We may
        need to the hide initial debugger frames.
        """
        thread = threading._active[thread_id]
        thread_name = thread.name
        if (
            not self.settings["dbg_trepan"]
            and thread_name == Mthread.current_thread_name()
        ):
            # The frame we came in on ('current_thread_name') is
            # the same as the one we want to switch to. In this case
            # we need to some debugger frames are in this stack so
            # we need to remove them.
            newframe = Mthread.find_debugged_frame(frame)
            if newframe is not None:
                frame = newframe
            pass
        # FIXME: else: we might be blocked on other threads which are
        # about to go into the debugger it not for the fact this one got there
        # first. Possibly in the future we want
        # to hide the blocks into threading of that locking code as well.

        # Set stack to new frame
        self.stack, self.curindex = get_stack(frame, None, self.proc)
        self.proc.stack, self.proc.curindex = self.stack, self.curindex
        self.proc.frame_thread_name = thread_name
        return

    def run(self, args):
        """Run a frame command. This routine is a little complex
        because we allow a number parameter variations."""

        try:
            opts, args = frame_parser.parse_args(args[1:])
        except SystemExit:
            return

        frame_str = "0" if len(args) == 0 else args[0]

        if frame_str.lower().startswith("b:"):
            opts.builtin = True
            frame_str = frame_str[2:]
        elif frame_str.lower().startswith("e:"):
            opts.expression = True
            frame_str = frame_str[2:]

        frame_num = self.proc.get_an_int(
            frame_str,
            f"The 'frame' command requires a frame number. Got: {frame_str}"
            )
        if frame_num is None:
            return False

        i_stack = len(self.proc.stack)
        if i_stack == 0:
            self.errmsg("No frames recorded")
            return False

        if frame_num < -i_stack or frame_num > i_stack - 1:
            self.errmsg(
                f"Frame number has to be in the range 0 to {i_stack - 1}; "
                f"is: {frame_num}."
            )
            return False

        frame_type = FrameType.python
        if opts.builtin:
            frame_type = FrameType.builtin
        elif opts.expression:
            frame_type = FrameType.expression

        adjust_frame(self.proc, count=frame_num, is_absolute_pos=True,
                     frame_type=frame_type)
        return

if __name__ == "__main__":
    from trepan import debugger as Mdebugger

    d = Mdebugger.Trepan()
    cp = d.core.processor
    command = FrameCommand(cp)
    command.run(["frame"])
    command.run(["frame", "1"])
    print("=" * 20)
    cp.curframe = inspect.currentframe()
    cp.stack, cp.curindex = get_stack(cp.curframe, None, None, cp)

    def showit(cmd):
        print("=" * 20)
        cmd.run(["frame"])
        print("-" * 20)
        # cmd.run(["frame", "MainThread"])
        # print("-" * 20)
        # cmd.run(["frame", ".", "0"])
        # print("-" * 20)
        # cmd.run(["frame", "."])
        # print("=" * 20)
        return

    # showit(command)

    class BgThread(threading.Thread):
        def __init__(self, fn, cmd):
            threading.Thread.__init__(self)
            self.fn = fn
            self.cmd = cmd
            return

        def run(self):
            self.fn(self.cmd)
            return

        pass

    pass

    background = BgThread(showit, command)
    background.start()
    background.join()  # Wait for the background task to finish
    pass
