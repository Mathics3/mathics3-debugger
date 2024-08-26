"""
Mathics3 Debugger Builtin Functions

These functions allow you to set events for entering the debugger when \
an event is triggered, or enter the debugger immediately.
"""

import mathics.eval.tracing as tracing
from mathics.core.builtin import Builtin
from mathics.core.evaluation import Evaluation
from mathics.core.symbols import SymbolTrue

from pymathics.debugger.tracing import call_event_debug

EVENT_OPTIONS = {
    "SymPy": "False",
    "Numpy": "False",
    "mpmath": "False",
    "apply": "false",
}

class DebugActivate(Builtin):
    """
    <dl>
      <dt>'DebugActivate'[$options$]
      <dd>Set to enter debugger entry on certain event
    </dl>

    >> DebugActivate[SymPy -> True]
     = ...
    """

    options = EVENT_OPTIONS
    summary_text = """set events to go into the Mathics3 Debugger REPL"""

    # The function below should start with "eval"
    def eval(self, evaluation: Evaluation, options: dict):
        "DebugActivate[OptionsPattern[DebugActivate]]"
        for event_name in tracing.TraceEventNames:
            option = self.get_option(options, event_name, evaluation)
            event_is_debugged = option == SymbolTrue
            if event_is_debugged:
                tracing.hook_entry_fn = call_event_debug
                tracing.hook_exit_fn = tracing.return_event_print
            if event_name == "mpmath":
                tracing.run_mpmath = (
                    tracing.run_mpmath_traced if event_is_debugged else tracing.run_fast
                )
            elif event_name == "SymPy":
                tracing.run_sympy = (
                    tracing.run_sympy_traced if event_is_debugged else tracing.run_fast
                )


class Debugger(Builtin):
    """
    <dl>
      <dt>'Debugger'[]
      <dd>enter debugger entry on certain event
    </dl>

    X> Debugger[]
     = ...
    """

    summary_text = """get into Mathics3 Debugger REPL"""

    def eval(self, evaluation: Evaluation):
        "Debugger[]"
        call_event_debug(tracing.TraceEvent.debugger, Debugger.eval, evaluation)


class TraceActivate(Builtin):
    """
    <dl>
      <dt>'TraceActivate'[$options$]
      <dd>Set event tracing and debugging.
    </dl>

    >> TraceActivate[SymPy -> True]
     = ...
    """

    options = EVENT_OPTIONS
    summary_text = """Set/unset tracing and debugging"""

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
