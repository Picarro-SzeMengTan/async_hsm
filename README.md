# async_hsm

This framework for Asynchronous Hierarchical State Machines written in Python3 using 
the asyncio module. It was forked from Dean Hall's farc project which is based on 
Miros Samek's algorithm described in [QP](www.state-machine.com).
[This book](https://newcontinuum.dl.sourceforge.net/project/qpc/doc/PSiCC2.pdf)
describes QP and how to program hierarchical state machines.

This framework has fewer than 1000 LOC.  It allows the programmer to create
highly-concurrent programs by using a "message-passing" system and
run-to-completion message handlers within a state-machine architecture.
With these tools, complex, asynchronous operations are decomposed
into managable chunks of code.

In the paragraph above message-passing is in quotes because async_hsm is doing
object reference copy and not object copy or serialization.
This leaves the programmer open to nasty side-effects.
For example, if you pass a list object and the recipient modifies the list,
the sender experiences those modifications even after the message was passed.

Known Issue: On windows, Ctrl+C is supressed by asyncio event loop's
run_forever() ([bug report](https://bugs.python.org/issue23057)).
The workaround is to inject an event to awake the event loop.


## Release History

2018/07/11  0.2.0
- Renamed package as async_hsm. 

- The algorithm for traversing the hierarchical state machine has been 
  rewritten so that it gives the same results as the comprehensive example
  in section 2.3.15 of "Practical UML statecharts in C/C++".

- The state machine classes have been rewritten to use conventional methods 
  rather than static ones which require the state machine to be passed as 
  the first argument.

- It is now possible to define state machines using a table-driven format.
  The examples Hsm_test.py and Hsm_test_tabled.py show how the same state
  machine may be entered in the two formats.

2019/05/15  0.1.1
- Removed 'initialState' argument from async_hsm.Hsm() constructor;
  framework now expects Hsm/Ahsm classes to have 'initial()' method.
- Made state methods private in examples to demonstrate a best-practice.
- Created async_hsm.Framework.run_forever() helper function.
- Misc comment and doctring improvements

2018/10/09  0.1.0   Initial release
