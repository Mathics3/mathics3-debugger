# -*- coding: utf-8 -*-
import inspect
from typing import Callable

import mathics.eval.tracing as tracing
from mathics.core.builtin import Builtin
from mathics.core.evaluation import Evaluation
from mathics.core.symbols import SymbolTrue

from pymathics.debugger.repl import DebugREPL

EVENT_OPTIONS = {
    "SymPy": "False",
    "Numpy": "False",
    "mpmath": "False",
    "apply": "false",
}

dbg = None

def call_event_debug(event: tracing.TraceEvent, fn: Callable, *args) -> bool:
    """
    A somehwat generic fuction to show an event-traced call.
    """
    if type(fn) == type or inspect.ismethod(fn) or inspect.isfunction(fn):
        name = f"{fn.__module__}.{fn.__qualname__}"
    else:
        name = str(fn)
    print(f"{event.name} call  : {name}{args[:3]}")
    global dbg
    if dbg is None:
        dbg = DebugREPL()
    current_frame = inspect.currentframe()
    dbg.core.trace_dispatch(current_frame, "repl", [])

    return False


def main():
    """Mathics3 Debugger setup"""

    # Save the original just for use in the restart that works via exec.
    dbg = DebugREPL()


class DebugActivate(Builtin):
    """
    <dl>
      <dt>'DebugActivate'[$options$]
      <dd>Set to enter debugger entry on certain event
    </dl>

    >> DebugActivate[SymPy -> True]
     =
    """

    options = EVENT_OPTIONS
    summary_text = """set events to got into Mathics3 Debugger REPL"""

    # The function below should start with "eval"
    def eval(self, evaluation: Evaluation, options: dict):
        "DebugActivate[OptionsPattern[DebugActivate]]"
        for event_name in tracing.TraceEventNames:
            option = self.get_option(options, event_name, evaluation)
            event_is_traced = option == SymbolTrue
            if event_is_traced:
                tracing.hook_entry_fn = call_event_debug
                tracing.hook_exit_fn = tracing.return_event_print
            if event_name == "mpmath":
                tracing.run_mpmath = (
                    tracing.run_mpmath_traced if event_is_traced else tracing.run_fast
                )
            elif event_name == "SymPy":
                tracing.run_sympy = (
                    tracing.run_sympy_traced if event_is_traced else tracing.run_fast
                )
        print("Debugger called")


class TraceActivate(Builtin):
    """
    <dl>
      <dt>'TraceActivate'[$options$]
      <dd>Set event tracing and debugging.
    </dl>

    >> TraceActivate[SymPy -> True]
     =
    """

    options = EVENT_OPTIONS
    summary_text = """Set/unset tracing and debugging"""

    # The function below should start with "eval"
    def eval(self, evaluation: Evaluation, options: dict):
        "TraceActivate[OptionsPattern[TraceActivate]]"
        # adjust_event_handlers(self, evaluation, options)
        for event_name in tracing.TraceEventNames:
            option = self.get_option(options, event_name, evaluation)
            event_is_traced = option == SymbolTrue
            if event_is_traced:
                tracing.hook_entry_fn = tracing.call_event_print
                tracing.hook_exit_fn = tracing.return_event_print
            if event_name == "mpmath":
                tracing.run_mpmath = (
                    tracing.run_mpmath_traced if event_is_traced else tracing.run_fast
                )
            elif event_name == "SymPy":
                tracing.run_sympy = (
                    tracing.run_sympy_traced if event_is_traced else tracing.run_fast
                )
