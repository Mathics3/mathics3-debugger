"""
Mathics3 Debugger Builtin Functions

These functions allow you to set events for entering the debugger when \
an event is triggered, or enter the debugger immediately.
"""

import inspect
import mathics.core.parser
import mathics.eval.files_io.files as io_files
import mathics.eval.tracing as tracing

from mathics.core.builtin import Builtin
from mathics.core.evaluation import Evaluation
from mathics.core.rules import FunctionApplyRule
from mathics.core.symbols import SymbolTrue

from pymathics.debugger.tracing import (
    TraceEventNames,
    apply_builtin_fn_print,
    apply_builtin_fn_traced,
    call_event_debug,
    call_event_get,
    call_trepan3k,
)

EVENT_OPTIONS = {
    "SymPy": "False",
    "Get": "False",
    "Numpy": "False",
    "mpmath": "False",
    "apply": "False",
    "parse": "False",
}

parse_untraced = mathics.core.parser.parse

# FIXME:

# We assume FunctionApplyRule.apply_function hasn't previously been
# overwritten at LoadModule["pymathics.debugger"] time, so
# the below save to EVALUATION_APPLY is pristine.
# Eventually we might change  mathics.core.rules.FunctionApplyRule
# in some way to make this more robust.
EVALUATION_APPLY = FunctionApplyRule.apply_function


class DebugActivate(Builtin):
    """
    <dl>
      <dt>'DebugActivate'[$options$]
      <dd>Set to enter debugger entry on certain event
    </dl>

    $options$ include:
    <ul>
      <li>'SymPy': debug SymPy calls
      <li>'NumPy':  debug NumPy calls
      <li>'mpmath': debug mpmath calls
      <li>'apply'; debug function apply calls
    </ul>

    >> DebugActivate[SymPy -> True]
     = ...
    """

    options = EVENT_OPTIONS
    summary_text = """set events to go into the Mathics3 Debugger REPL"""

    # The function below should start with "eval"
    def eval(self, evaluation: Evaluation, options: dict):
        "DebugActivate[OptionsPattern[DebugActivate]]"
        for event_name in TraceEventNames:
            option = self.get_option(options, event_name, evaluation)
            event_is_debugged = option == SymbolTrue
            if event_is_debugged:
                tracing.hook_entry_fn = call_event_debug
                tracing.hook_exit_fn = tracing.return_event_print
            if event_name == "mpmath":
                tracing.run_mpmath = (
                    tracing.run_mpmath_traced if event_is_debugged else tracing.run_fast
                )
            elif event_name == "Get":
                io_files.DEFAULT_TRACE_FN = (
                    call_event_get if event_is_debugged else None
                )
            elif event_name == "SymPy":
                tracing.run_sympy = (
                    tracing.run_sympy_traced if event_is_debugged else tracing.run_fast
                )
            elif event_name == "apply":
                FunctionApplyRule.apply_function = (
                    apply_builtin_fn_traced if event_is_debugged else EVALUATION_APPLY
                )


class Debugger(Builtin):
    """
    <dl>
      <dt>'Debugger'[trepan3k -> True]
      <dd>enter debugger entry on certain event
    </dl>

    X> Debugger[]
     = ...

    X> Debugger[trepan3k -> True]
     = ...
    """

    options = {"trepan3k": "False"}
    summary_text = """get into Mathics3 Debugger REPL"""

    def eval(self, evaluation: Evaluation, options: dict):
        "Debugger[OptionsPattern[Debugger]]"
        if self.get_option(options, "trepan3k", evaluation) == SymbolTrue:
            global dbg
            if dbg is None:
                from pymathics.debugger.lib.repl import DebugREPL
                dbg = DebugREPL()


            frame = inspect.currentframe()
            if frame is not None:
                dbg.core.processor.curframe = frame.f_back
                call_trepan3k(dbg.core.processor)
            else:
                print("Error getting current frame")

        else:
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
        for event_name in TraceEventNames:
            option = self.get_option(options, event_name, evaluation)
            event_is_traced = option == SymbolTrue
            if event_is_traced:
                tracing.hook_entry_fn = tracing.call_event_print
                tracing.hook_exit_fn = tracing.return_event_print
            if event_name == "mpmath":
                tracing.run_mpmath = (
                    tracing.run_mpmath_traced if event_is_traced else tracing.run_fast
                )
            elif event_name == "Get":
                io_files.DEAULT_TRACE_FN = (
                    io_files.print_line_number_and_text if event_is_traced else None
                )
            elif event_name == "SymPy":
                tracing.run_sympy = (
                    tracing.run_sympy_traced if event_is_traced else tracing.run_fast
                )
            elif event_name == "apply":
                FunctionApplyRule.apply_function = (
                    apply_builtin_fn_print if event_is_traced else EVALUATION_APPLY
                )
