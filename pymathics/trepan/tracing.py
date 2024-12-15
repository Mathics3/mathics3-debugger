import inspect
import re
import time
from enum import Enum
from typing import Callable

import mathics.eval.tracing as eval_tracing
from mathics.core.evaluation import Evaluation
from mathics.core.rules import FunctionApplyRule
from mathics.core.symbols import (
    Symbol,
    SymbolConstant,
    SymbolTrue,
    SymbolFalse,
    strip_context,
)
from trepan.debugger import Trepan

from pymathics.trepan.lib.format import format_element, pygments_format

from typing import Dict, List


TraceEventNames = (
    "Debugger",  # a direct call to Debugger[]
    "Get",  # Get[] builtin call
    "Numpy",  # traps calls to Numpy functions
    "SymPy",  # traps calls to SymPy functions
    "apply",  # applying a function that is *not* a Boxing function
    "applyBox",  # applying a function that *is* a Boxing function
    "evaluate",  # calling an evaluate() method, e.g. Expression.evaluate()
    "evalMethod",  # calling a built-in evaluation method Class.eval_xxx()
    "evalFunction",  # calling an evaluation  eval_Xxx() of mathics.eval
    "mpmath",  # traps calls to mpmath functions
    "parse",  # traps calls to parse()
)
TraceEvent = Enum("TraceEvent", TraceEventNames)

# Event filtering masks. An empty list
# means not filtering. To remove filtering
# though set the event to False.
# Setting an event to True force the last
# set of filters to go into effect.
#
event_filters: Dict[str, List[str]] = {
    "Get": [],
    "Numpy": [],
    "SymPy": [],
    "apply": [],
    "applyBox": [],
    "evaluate-entry": [],  # Before evaluate()
    "evaluate-result": [],  # After evaluate() when we have a value
    "evalMethod": [],
    "evalFunction": [],
    "mpmath": [],
}


dbg = None

saved_methods: Dict[str, Callable] = {}


def apply_builtin_fn_traced_common(
    self, expression, vars, options: dict, evaluation, trace_boxing: bool
):
    """
    Common routine to trace debugger on a Mathics apply function.
    """
    vars_noctx = dict(((strip_context(s), vars[s]) for s in vars))
    if self.pass_expression:
        vars_noctx["expression"] = expression

    if options and self.check_options:
        if not self.check_options(options, evaluation):
            return None

    if (
        eval_tracing.hook_entry_fn is not None
        and bool(re.match("^System`[A-Z][A-Za-z0-9]+Box", expression.head.name))
        == trace_boxing
    ):
        args = (self, expression, vars, options, evaluation)
        skip_call = eval_tracing.hook_entry_fn(TraceEvent.apply, *args)
    else:
        skip_call = False

    if not skip_call:
        if options:
            return self.function(evaluation=evaluation, options=options, **vars_noctx)
        else:
            return self.function(evaluation=evaluation, **vars_noctx)


def apply_builtin_box_fn_traced(
    self, expression, vars, options: dict, evaluation: Evaluation
):
    """Trace or debug an apply function that is a Boxing apply"""
    return self.apply_builtin_fn_traced_common(
        expression, vars, options, evaluation, True
    )


def apply_builtin_fn_traced(
    self, expression, vars, options: dict, evaluation: Evaluation
):
    """Trace or debug an apply function that is not a Boxing apply"""
    return apply_builtin_fn_traced_common(
        self, expression, vars, options, evaluation, False
    )


def apply_builtin_fn_print(
    self, expression, vars, options: dict, evaluation: Evaluation
):
    """
    Run debugger on a builtin function call.
    """
    vars_noctx = dict(((strip_context(s), vars[s]) for s in vars))
    if self.pass_expression:
        vars_noctx["expression"] = expression

    if options and self.check_options:
        if not self.check_options(options, evaluation):
            return None

    global dbg
    if dbg is None:
        from pymathics.trepan.lib.repl import DebugREPL

        dbg = DebugREPL()

    style = dbg.settings["style"]
    mathics_str = format_element(expression)
    msg = dbg.core.processor.msg
    msg(f"apply: {pygments_format(mathics_str, style)}")

    if options:
        return self.function(evaluation=evaluation, options=options, **vars_noctx)
    else:
        return self.function(evaluation=evaluation, **vars_noctx)


def call_event_debug(event: TraceEvent, fn: Callable, *args) -> bool:
    """
    A somewhat generic function to show an event-traced call.
    """
    global dbg
    if dbg is None:
        from pymathics.trepan.lib.repl import DebugREPL

        dbg = DebugREPL()

    msg = dbg.core.processor.msg

    if event == TraceEvent.apply:
        # args[0] has the expression to be called
        style = dbg.settings["style"]
        mathics_str = format_element(args[0])
        msg(f"{event.name}: {pygments_format(mathics_str, style)}")
    else:
        if type(fn) is type or inspect.ismethod(fn) or inspect.isfunction(fn):
            name = f"{fn.__module__}.{fn.__qualname__}"
        else:
            name = str(fn)
        msg(f"{event.name} call  : {name}{args[:3]}")

    # Note: there may be a temptation to go back a frame, i.e. use
    # `f_back` to `current_frame`. However, keeping the frame `call_event_debug`,
    # it is easy for trace_dispatch to detect this a known caller
    # and remove a few *more* frames to the traced calls that led up
    # to calling us.
    current_frame = inspect.currentframe()

    # Remove any "Tracing." from event string.
    event_str = str(event).split(".")[-1]
    dbg.core.execution_status = "Running"
    dbg.core.trace_dispatch(current_frame, event_str, (fn, args))

    return False


def call_event_get(line_number: int, text: str) -> bool:
    """
    Event dispatch wrapper function for Get (<<).
    """
    global dbg
    if dbg is None:
        from pymathics.trepan.lib.repl import DebugREPL

        dbg = DebugREPL()

    current_frame = inspect.currentframe()
    if current_frame is not None:
        current_frame = current_frame.f_back

    dbg.core.execution_status = "Running"
    msg_fn = dbg.core.processor.rst_msg
    if line_number == 0:
        msg_fn(f"**Reading** **file**: {text}")
    else:
        msg_fn("%5d: %s" % (line_number, text.rstrip()))
    f_locals = current_frame.f_locals
    if "path" in f_locals:
        file_path = f_locals["path"]
    else:
        f_locals = current_frame.f_back.f_locals
        file_path = f_locals["feeder"].filename
    dbg.core.trace_dispatch(current_frame, "Get", (file_path, (line_number, text)))

    return False


# Should this be here?
def call_trepan3k(proc_obj):
    """
    Go into trepan3k - the lower-level Python debugger
    """
    core_obj = proc_obj.core
    if core_obj.python_debugger is None:
        debug_opts = {
            "settings": core_obj.debugger.settings,
            "interface": proc_obj.intf[-1],
        }
        core_obj.python_debugger = Trepan(opts=debug_opts)

    event = "line"
    python_core_obj = core_obj.python_debugger.core
    python_core_obj.execution_status = "Running"
    python_core_obj.processor.event_processor(proc_obj.curframe, event, None)
    print("call done")
    return


def debug_evaluate(self, evaluation, status: str, orig_expr=None):
    """
    Called from a decorated Python @trace_evaluate .evaluate()
    method when DebugActivate["evaluate" -> True]
    """
    global dbg
    if dbg is None:
        from pymathics.trepan.lib.repl import DebugREPL

        dbg = DebugREPL()

    current_frame = inspect.currentframe()
    if current_frame is not None:
        current_frame = current_frame.f_back
        if current_frame is not None:
            current_frame = current_frame.f_back

    dbg.core.execution_status = "Running"
    event_str = "evaluate-entry" if status == "Evaluating" else "evaluate-result"
    dbg.core.trace_dispatch(
        current_frame, event_str, (self, evaluation, status, orig_expr)
    )


def debug_eval_method(method_name: str, *args, **kwargs):
    global dbg
    if dbg is None:
        from pymathics.trepan.lib.repl import DebugREPL

        dbg = DebugREPL()

    current_frame = inspect.currentframe()
    if current_frame is not None:
        current_frame = current_frame.f_back
        if current_frame is not None:
            current_frame = current_frame.f_back

    dbg.core.execution_status = "Running"
    method = saved_methods.get(method_name)
    dbg.core.trace_dispatch(
        current_frame, "evalMethod", (method_name, method, *args, *kwargs)
    )
    if method is not None:
        return method(*args, **kwargs)


def pre_evaluation_debugger_hook(query, evaluation: Evaluation):
    """
    A debugger pre-evaluation hook that allows us to
    alter `evaluation` functions so we can debug or trace them
    """
    print("Pre evaluation hook called")
    for method in event_filters["evalMethod"]:
        if method == "message":
            if saved_methods.get(method) is None:
                saved_methods[method] = evaluation.message
            evaluation.message = debug_eval_method
        else:
            definition = evaluation.definitions.get_definition(
                method, only_if_exists=True
            )
            if definition is not None:
                for value in definition.downvalues:
                    if isinstance(value, FunctionApplyRule) and hasattr(
                        value, "apply_function"
                    ):
                        # FIXME: this works if there is only one eval rule!
                        if saved_methods.get(method) is None:
                            saved_methods[method] = value.apply_function
                        value.apply_function = (
                            lambda *args, **kwargs: debug_eval_method(
                                method, *args, **kwargs
                            )
                        )

    return


# We use this to track whether to check if there is
# a new message logged when performing Evaluate() tracing.
message_count: int = 0


def trace_evaluate(expr, evaluation, status: str, fn: Callable, orig_expr=None):
    """
    Print what's up with an evaluation. In contrast to debug_evaluate,
    we don't stop execution and go into a debugger.

    Called from a decorated Python @trace_evaluate .evaluate()
    method when TraceActivate["evaluate" -> True]
    """

    if evaluation.definitions.timing_trace_evaluation:
        evaluation.print_out(time.time() - evaluation.start_time)

    global dbg
    if dbg is None:
        from pymathics.trepan.lib.repl import DebugREPL

        dbg = DebugREPL()

    msg = dbg.core.processor.msg
    style = dbg.settings["style"]

    # Test and dispose of various situations where showing information
    # is pretty useless: evaluating a Symbol is the Symbol.
    # Showing the return value of a ListExpression literal is
    # also useless.
    if isinstance(expr, Symbol) and not isinstance(expr, SymbolConstant):
        return

    if (
        status == "Returning"
        and hasattr(expr, "is_literal")
        and expr.is_literal
        and hasattr(orig_expr, "is_literal")
        and orig_expr.is_literal
    ):
        return

    if orig_expr == expr:
        # If the two expressions are the same, there is no point in
        # repeating the output.
        return

    indents = "  " * evaluation.recursion_depth

    if orig_expr is not None:
        formatted_orig_expr = format_element(orig_expr)
        if fn.__name__ == "rewrite_apply_eval_step":
            if orig_expr != expr[0]:
                if status == "Returning":
                    if expr[1]:
                        status = "Rewriting"
                        arrow = " -> "
                    else:
                        return
                else:
                    arrow = " = "
                formatted_expr = format_element(expr[0])
                msg(
                    f"{indents}{status}: "
                    + pygments_format(
                        formatted_orig_expr + arrow + formatted_expr, style
                    )
                )
        else:
            formatted_expr = format_element(expr)
            assign_str = f"{formatted_orig_expr}  = {formatted_expr}"
            msg(
                f"{indents}{status}: "
                f"{pygments_format(assign_str, style)}"
            )
    elif not hasattr(fn, "__name__") or fn.__name__ != "rewrite_apply_eval_step":
        formatted_expr = format_element(expr)
        msg(f"{indents}{status}: {pygments_format(formatted_expr, style)}")
