

# async def foo():
#     # a long async operation
#     # no value is returned

# If you want to call foo() as an asynchronous task, and doesn't care about the result:

# prepare_for_foo()
# foo()                                           
# # RuntimeWarning: coroutine foo was never awaited
# remaining_work_not_depends_on_foo()

# This is because invoking foo() doesn't actually runs the function foo(), but created a "coroutine object" instead. This "coroutine object" will be executed when current EventLoop gets a chance: awaited/yield from is called or all previous tasks are finished.

# To execute an asynchronous task without await, use loop.create_task() with loop.run_until_complete():

# prepare_for_foo()
# task = loop.create_task(foo())
# remaining_work_not_depends_on_foo()
# loop.run_until_complete(task)

