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
""" Functions for working with Python frames"""

import inspect
import os.path as osp

from trepan.lib.format import (
    Arrow,
    format_token,
)
from trepan.lib.stack import format_stack_entry
from mathics.core.builtin import Builtin
from mathics.core.expression import Expression


def count_frames(frame, count_start=0):
    """Return a count of the number of frames"""
    count = -count_start
    while frame:
        count += 1
        frame = frame.f_back
    return count


def print_expression_stack(proc_obj, count: int, color="plain"):
    """
    Display the Python call stack but filtered so that we show only expresions.
    """
    j = 0
    intf = proc_obj.intf[-1]
    n = len(proc_obj.stack)
    for i in range(n):
        frame_lineno = proc_obj.stack[len(proc_obj.stack) - i - 1]
        frame = frame_lineno[0]
        self_obj = frame.f_locals.get("self", None)
        if isinstance(self_obj, Expression):
            if frame is proc_obj.curframe:
                intf.msg_nocr(format_token(Arrow, "E>", highlight=color))
            else:
                intf.msg_nocr("E#")
            stack_nums = f"{j} ({i}"
            intf.msg(
                f"{j} ({i}) {frame.f_code.co_qualname} {self_obj.__class__}"
                )
            intf.msg(" " * (4 + len(stack_nums)) +
                     format_stack_entry(proc_obj.debugger, frame_lineno, color=color))
            j += 1
            if j >= count:
                break

def print_mathics_stack(proc_obj, count: int, color="plain"):
    """
    Display the Python call stack but filtered so that we Builtin calls.
    """
    j = 0
    intf = proc_obj.intf[-1]
    n = len(proc_obj.stack)
    for i in range(n):
        frame, _ = proc_obj.stack[len(proc_obj.stack) - i - 1]
        self_obj = frame.f_locals.get("self", None)
        if isinstance(self_obj, Builtin):
            if frame is proc_obj.curframe:
                intf.msg_nocr(format_token(Arrow, "M>", highlight=color))
            else:
                intf.msg_nocr("B#")
            intf.msg(
                f"{j} ({i}) {frame.f_code.co_qualname} {self_obj.__class__}"
                )
            j += 1
            if j >= count:
                break


def print_stack_entry(proc_obj, i_stack: int, color="plain", opts={}):
    frame_lineno = proc_obj.stack[len(proc_obj.stack) - i_stack - 1]
    frame, _ = frame_lineno
    intf = proc_obj.intf[-1]
    if frame is proc_obj.curframe:
        intf.msg_nocr(format_token(Arrow, "->", highlight=color))
    else:
        intf.msg_nocr("##")
    intf.msg(
        f"{i_stack} {format_stack_entry(proc_obj.debugger, frame_lineno, color=color)}"
        )


def print_stack_trace(proc_obj, count=None, color="plain", opts={}):
    "Print ``count`` entries of the stack trace"
    if count is None:
        n = len(proc_obj.stack)
    else:
        n = min(len(proc_obj.stack), count)
    try:
        if opts["builtin"]:
            print_mathics_stack(proc_obj, n, color=color)
        elif opts["expression"]:
            print_expression_stack(proc_obj, n, color=color)
        else:
            for i in range(n):
                print_stack_entry(proc_obj, i, color=color, opts=opts)
    except KeyboardInterrupt:
        pass
    return


def print_dict(s, obj, title):
    if hasattr(obj, "__dict__"):
        d = obj.__dict__
        if isinstance(d, dict):
            keys = list(d.keys())
            if len(keys) == 0:
                s += f"\n  No {title}"
            else:
                s += f"\n  {title}:\n"
            keys.sort()
            for key in keys:
                s += f"    '{key}':\t{d[key]}\n"
                pass
            pass
        pass
    return s


def eval_print_obj(arg, frame, format=None, short=False):
    """Return a string representation of an object"""
    try:
        if not frame:
            # ?? Should we have set up a dummy globals
            # to have persistence?
            val = eval(arg, None, None)
        else:
            val = eval(arg, frame.f_globals, frame.f_locals)
            pass
    except Exception:
        return 'No symbol "' + arg + '" in current context.'

    return print_obj(arg, val, format, short)


def print_obj(arg, val, format=None, short=False):
    """Return a string representation of an object"""
    what = arg
    if format:
        what = format + " " + arg
        val = printf(val, format)
        pass
    s = f"{what} = {val}"
    if not short:
        s += f"\n  type = {type(val)}"
        # Try to list the members of a class.
        # Not sure if this is correct or the
        # best way to do.
        s = print_dict(s, val, "object variables")
        if hasattr(val, "__class__"):
            s = print_dict(s, val.__class__, "class variables")
            pass
        pass
    return s


# Demo stuff above
if __name__ == "__main__":

    class MockDebuggerCore:
        def canonic_filename(self, frame):
            return frame.f_code.co_filename

        def filename(self, name):
            return name

        pass

    class MockDebugger:
        def __init__(self):
            self.core = MockDebuggerCore()
            self.settings = {"maxargstrsize": 80}
            pass

        pass

    frame = inspect.currentframe()
    pyc_file = osp.join(
        osp.dirname(__file__), "__pycache__", osp.basename(__file__)[:-3] + ".pyc"
    )

    m = MockDebugger()
    print(format_stack_entry(m, (frame, 10,)))
    # print(format_stack_entry(m, (frame, 10,), color="dark"))
    # print("frame count: %d" % count_frames(frame))
    # print("frame count: %d" % count_frames(frame.f_back))
    # print("frame count: %d" % count_frames(frame, 1))
    # print("def statement: x=5?: %s" % repr(is_def_stmt("x=5", frame)))
    # # Not a "def" statement because frame is wrong spot
    # print(is_def_stmt("def foo():", frame))

    # def sqr(x):
    #     x * x

    # def fn(x):
    #     frame = inspect.currentframe()
    #     print(get_call_function_name(frame))
    #     return

    # print("=" * 30)
    # eval("fn(5)")
    # print("=" * 30)
    # print(print_obj("fn", fn))
    # print("=" * 30)
    # print(print_obj("len", len))
    # print("=" * 30)
    # print(print_obj("MockDebugger", MockDebugger))
    pass
