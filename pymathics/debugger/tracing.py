import inspect
from typing import Callable
import mathics.eval.tracing as tracing

dbg = None

def call_event_debug(event: tracing.TraceEvent, fn: Callable, *args) -> bool:
    """
    A somewhat generic fuction to show an event-traced call.
    """
    if type(fn) == type or inspect.ismethod(fn) or inspect.isfunction(fn):
        name = f"{fn.__module__}.{fn.__qualname__}"
    else:
        name = str(fn)
    print(f"{event.name} call  : {name}{args[:3]}")
    global dbg
    if dbg is None:
        from pymathics.debugger.lib.repl import DebugREPL
        dbg = DebugREPL()

    # Note: there may be a temptation to go back a frame, i.e. use
    # `f_back` to `current_frame`. However, keeping the frame `call_event_debug`,
    # it is easy for trace_dispatch to detect this a known caller
    # and remove a few *more* frames to the traced calls that led up
    # to calling us.
    current_frame = inspect.currentframe()

    # Remove any "Tracing." from event string.
    event_str = str(event).split(".")[-1]
    dbg.core.execution_status = "Running"
    dbg.core.trace_dispatch(current_frame, event_str, args)

    return False
