import inspect
from typing import Callable
import mathics.eval.tracing as tracing

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
        from pymathics.debugger.repl import DebugREPL
        dbg = DebugREPL()
    current_frame = inspect.currentframe()
    # Remove "Tracing."
    event_str = str(event).split(".")[-1]
    dbg.core.trace_dispatch(current_frame, event_str, args)

    return False
