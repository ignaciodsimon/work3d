'''
    This module implements a class "Worker" that is used to encapsulate the
    process of realising individual tasks. The target function receives two
    parameters: 'tasks' and 'workerID'.

    Joe Simon 2018.
'''


from logger import *
import numpy
import multiprocessing as mp


class Worker:

    def __init__(self, workerId=0):
        self._log = getLogger() #Logger()
        self._tasks = None
        self._worker = None
        self._workerId = workerId


    def assignTasks(self, newTasks):
        self._tasks = newTasks


    def startWorking(self):
        if self._tasks is None:
            raise Exception("No tasks assigned to this worker!")

        self._pool = mp.Pool()
        self._worker = self._pool.apply_async(func=self._tasks._rayTracerData.tracerEngine,
                                              args=(self._tasks, self._workerId))


    def isDone(self):
        return self._worker.ready()


    def waitForWorker(self):
        self._pool.close()
        self._pool.join()


    def getWorkerResults(self):
        return self._worker.get()
