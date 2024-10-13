`Mathics3 <https://mathics.org>`_ Debugger Module

Until we have some proper documentation here are some examples.


# Example session

In order to enable debugging in Mathics3, install ``mathics3-debugger``.
Inside a mathics3 session run::

  In[1]:= LoadModule["pymathics.debugger"]
  Out[1]= "pymathics.debugger"

Next you need to active some events to trigger going into the debugger::

  In[2]:= DebugActivate[mpmath->True]
  Out[2]=

Other events include: "Debugger", "Get", "Numpy", "SymPy", "apply", and "evalMethd".

In the above, ``mpmath->True goes into the debugger anytime an mpmath function is called.
``Exp[1.0]`` is such a function::

  In[3]:= Exp[1.0]
  mpmath call  : mpmath.ctx_base.StandardBaseContext.power(2.718281828459045, 1.0)
  (/tmp/mathics-core/mathics/eval/arithmetic.py:68 @88): run_mpmath
  mp 68             result_mp = tracing.run_mpmath(mpmath_function, *mpmath_args)
  (Mathics3 Debug)

A useful command to run is ``bt -b`` which shows the Buitin Function calls in the call stack::

    (Mathics3 Debug) bt -b
    B#0 (2) Power[z__]
              called from file '/tmp/mathics-core/mathics/core/builtin.py' at line 659
    B#1 (3) Power[x_, y_]
              called from file '/tmp/mathics-core/mathics/builtin/arithfns/basic.py' at line 477

To get a list of all debugger commands::

    (Mathics3 Debug) help *
    List of all debugger commands:
        alias      down   help  mathics3      reload  trepan3k
        backtrace  eval   info  printelement  set     up
        continue   frame  kill  python        show

When you are done inspecting things, run ``continue`` (or short-hand ``c``) to resume execution::

    (Mathics3 Debug) c
    mpmath result: 2.71828182845905
    Out[3]= 2.71828


## Post-mortem debugging::



  mathics --post-mortem
  # Find a Python bug in Mathics3 and trigger that.
  # I modified Compress.eval() and added 1/0

  In[1]:= Compress["abc"]
    Traceback (most recent call last):
    File "/tmp/mathicsscript", line 8, in <module>
    sys.exit(main())
             ^^^^^
    ...
    ZeroDivisionError: division by zero
    Uncaught exception. Entering post-mortem debugger...
    (/tmp/mathics/builtin/compress.py:37 @6): eval
    !! 37         1/0
    R=> (<class 'ZeroDivisionError'>, ZeroDivisionError('division by zero'),

    (Trepan3k:pm) load trepan3k_mathics3
    loaded command: "mathics3"
    loaded command: "mbacktrace"
    loaded command: "mup"
    loaded command: "printelement"
    (Trepan3k:pm) mbt -b
    B>0 (0) Compress[expr_, OptionsPattern[Compress]]
              called from file '/src/external-vcs/github/Mathics3/mathics-core/mathics/builtin/compress.py' at line 37
    B>1 (36) Compress[expr_, OptionsPattern[Compress]]
               called from file '/src/external-vcs/github/Mathics3/mathics-core/mathics/builtin/compress.py' at line 37
    (Trepan3k:pm)
