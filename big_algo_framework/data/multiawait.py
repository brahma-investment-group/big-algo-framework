import contextlib
import asyncio


@contextlib.asynccontextmanager
async def multi_await():
    """A context manager to call multiple functions that return awaitables, iteratively

    This function manages calling functions iteratively to get awaitable objects from them.
    This code works with functions that return coroutines or tasks. This is useful when you
    want to do something like get results from multiple queues in a single loop.

    Functions returning awaitables need to be registered by calling m.add(fn).

    Getting results from those functions is done by calling "await m.get()". Two lists
    are returned. The first is a list of completed awaitables. The second is a list of exceptions
    raiesd. Each list has its values placed positionally, equivalent to the order in which m.add(fn)
    was called. Each list has None in the corresponding position if the function is not complete, or
    if the function actually returned the value None.

    Example code using instances of asyncio.Queue named "q1" and "q2":

    async with multi_await() as m:
      # Setup functions that get called each iteration
      m.add(q1.get)
      m.add(q2.get)

      while True: # keep calling the same two functions forever
        # check if the awaitable from either function has a result ready
        completed, failures = await m.get()

        result_from_queue1, result_from_queue2 = completed
        failure_from_queue1, failure_from_queue2 = failures
    """
    ma = MultiAwait()
    try:
        yield ma
    finally:
        await ma.cancel()


class MultiAwait(object):
    """This class implements all the logic to iteratively call functions which return awaitable objects.

       See the documentation of the multi_await() function in this package for recommended usage. If you
       create an instance of this manually, then call the .cancel() method when you are done with this object.
    """

    def __init__(self):
        self.tasks = []
        self.srcs = []
        self.completed = []

    def add(self, src):
        # Add to list of sources
        self.srcs.append(src)
        # Add to list of tasks that are 'complete', which need to be started again
        self.completed.append(len(self.srcs) - 1)
        # Add a blank slot for the task
        self.tasks.append(None)

    async def cancel(self):
        for t in self.tasks:
            if t is None:
                continue
            t.cancel()
            try:
                await t
            except asyncio.CancelledError as e:
                pass

        # [t.cancel() for t in self.tasks if t is not None]
        self.tasks = [None for _ in self.srcs]  # leave in a good state
        self.completed.clear()

    async def get(self):
        if len(self.srcs) == 0:
            raise RuntimeError('Attempted to await 0 coroutines')

        # Fill in any blank tasks
        for i in self.completed:
            src = self.srcs[i]
            coro_or_task = src()
            if isinstance(coro_or_task, asyncio.Task):
                task = coro_or_task
            else:
                task = asyncio.create_task(coro_or_task)
            self.tasks[i] = task
        self.completed.clear()

        try:
            done, pending = await asyncio.wait(self.tasks, return_when=asyncio.FIRST_COMPLETED)
        except asyncio.CancelledError as e:
            self.cancel()
            raise e

        results = []
        failures = []

        for i, task in enumerate(self.tasks):
            if task in done:
                # Record this task as done, so it is started again
                self.completed.append(i)

                self.tasks[i] = None
                task_result = None
                try:
                    task_result = task.result()
                except Exception as failure:
                    failures.append(failure)
                    results.append(None)
                else:
                    failures.append(None)
                    results.append(task_result)
            else:
                results.append(None)
                failures.append(None)

        return (results, failures,)