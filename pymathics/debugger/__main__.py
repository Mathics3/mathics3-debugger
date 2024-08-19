# -*- coding: utf-8 -*-
import mathics.eval.tracing as tracing
from mathics.core.builtin import Builtin
from mathics.core.evaluation import Evaluation
from mathics.core.symbols import SymbolTrue


class TraceActivate(Builtin):
    """
    <dl>
      <dt>'TraceActivate'[$options$]
      <dd>Set even tracing and debugging.
    </dl>

    >> TraceActivate[SymPy -> True]
     =
    """

    options = {
        "SymPy": "False",
        "Numpy": "False",
        "mpmath": "False",
        "apply": "false",
    }
    summary_text = """Set/unset tracing and debugging"""

    # The function below should start with "eval"
    def eval(self, evaluation: Evaluation, options: dict):
        "TraceActivate[OptionsPattern[TraceActivate]]"
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
