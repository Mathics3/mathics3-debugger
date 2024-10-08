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
from mathics.core.list import ListExpression
from mathics.core.rules import FunctionApplyRule
from mathics.core.symbols import SymbolTrue

from pymathics.debugger.tracing import (
    TraceEventNames,
    apply_builtin_box_fn_traced,
    apply_builtin_fn_print,
    apply_builtin_fn_traced,
    call_event_debug,
    call_event_get,
    call_trepan3k,
    event_filters
)

from typing import Dict

# FIXME: DRY with debugger.tracing.TraceEventNames
EVENT_OPTIONS: Dict[str, str] = {
    "SymPy": "False",
    "Get": "False",
    "Numpy": "False",
    "mpmath": "False",
    "apply": "False",
    "apply_box": "False",
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
      <li>'Get':  debug Get[] calls, with Trace->True set
      <li>'NumPy':  debug NumPy calls
      <li>'SymPy': debug SymPy calls
      <li>'mpmath': debug mpmath calls
      <li>'apply'; debug function apply calls that are <i>not</i> boxing routines
      <li>'apply_box'; debug function apply calls that <i>are</i> boxing routines
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
            if event_name == "Debugger":
                continue
            option = self.get_option(options, event_name, evaluation)
            if option is None:
                evaluation.message("DebugActivate", "options", event_name)
                return

            event_is_debugged = (option == SymbolTrue or isinstance(option, ListExpression))
            if event_is_debugged:
                tracing.hook_entry_fn = call_event_debug
                tracing.hook_exit_fn = tracing.return_event_print
                if isinstance(option, ListExpression):
                    event_filters[event_name] = [opt.value for opt in option.elements]

            if event_name == "mpmath":
                tracing.run_mpmath = (
                    tracing.run_mpmath_traced if event_is_debugged else tracing.run_fast
                )
            elif event_name == "Get":
                io_files.GET_PRINT_FN = (
                    call_event_get if event_is_debugged else io_files.print_line_number_and_text
                )
            elif event_name == "SymPy":
                tracing.run_sympy = (
                    tracing.run_sympy_traced if event_is_debugged else tracing.run_fast
                )

            # FIXME: we need to fold in whether to track boxing or not into
            # apply_function(). As things stand now the single monkey-patched routine
            # is clobbered by apply_box below
            elif event_name == "apply":
                FunctionApplyRule.apply_function = (
                    apply_builtin_fn_traced if event_is_debugged else EVALUATION_APPLY
                )

            # FIXME: see above.
            # elif event_name == "apply_box":
            #     FunctionApplyRule.apply_function = (
            #         apply_builtin_box_fn_traced if event_is_debugged else EVALUATION_APPLY
            #     )
        print("XXX", event_filters)

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
            elif event_name == "apply":
                FunctionApplyRule.apply_function = (
                    apply_builtin_fn_print if event_is_traced else EVALUATION_APPLY
                )
