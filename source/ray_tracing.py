import numpy
from geometry import *
from logger import *
from multithread_workers import *
import time
import os
from ray_tracing_classes import *


class RayTracer:

    def __init__(self):
        self._sources = []
        self._environmentGeometry = None
        self._environmentParameters = None
        self._receivers = []
        self._log = getLogger() #Logger()
        self._rayTracerParameters = None
        self._outputFilename = None


    def addSource(self, newSource):
        if not isinstance(newSource, SourceDefinition):
            raise Exception("A new source for the ray-tracer must be of type SourceDefinition!")
        self._sources.append(newSource)


    def addEnvironmentGeometry(self, newEnvironmentGeometry):
        if not isinstance(newEnvironmentGeometry, LibraryGeometries):
            raise Exception("A new environment geometry for the ray-tracer must be of type LibraryGeometries!")
        if not self._environmentGeometry is None:
            self._log.log(LogLevel.Warn, "Discarding previously loaded environment geometry!")
        self._environmentGeometry = newEnvironmentGeometry


    def addEnvironmentParameters(self, newEnvironmentParameters):
        if not isinstance(newEnvironmentParameters, EnvironmentParameters):
            raise Exception("A new environment parameters for the ray-tracer must be of type EnvironmentParameters!")
        if not self._environmentParameters is None:
            self._log.log(LogLevel.Warn, "Discarding previously loaded environment parameters!")
        self._environmentParameters = newEnvironmentParameters


    def addReceiver(self, newReceiverDefinition):
        if not isinstance(newReceiverDefinition, ReceiverDefinition):
            raise Exception("A new receiver for the ray-tracer must be of type ReceiverDefinition!")
        self._receivers.append(newReceiverDefinition)


    def executeTracing(self):
        # Check that all needed data is available
        if self._environmentGeometry is None:
            raise Exception("Cannot execute a ray-tracing without an environment geometry definition!")
        if len(self._sources) == 0:
            raise Exception("Cannot execute a ray-tracing without any source(s) definition!")
        if len(self._receivers) == 0:
            raise Exception("Cannot execute a ray-tracing without any receiver(s) definition!")
        if self._environmentParameters is None:
            self._environmentParameters = EnvironmentParameters()
            self._log.log(LogLevel.Warn, "No environment parameters set. Using default values!")
        if self._rayTracerParameters is None:
            self._rayTracerParameters = RayTracerParameters()
            self._log.log(LogLevel.Warn, "No ray-tracer parameters set. Using default values!")
        self._log.log(LogLevel.Info, "All data ready.\nRay-tracing simulation started.")
        if self._outputFilename is None:
            self._log.log(LogLevel.Warn, "No output filename set! The results will not be saved!")

        # --- Conduct ray-tracing

        # Divide the total work in multiple packages for the workers
        if not self._rayTracerParameters._parallelThreads >= 1:
            raise Exception("The parameter 'parallelThreads' must be set to 1 (single thread) or higher.")
        self._log.log(LogLevel.Info, "Dividing work in parts for %d worker(s)." % self._rayTracerParameters._parallelThreads)
        _work = self._divideWorkInParts()

        # Create workers
        self._log.log(LogLevel.Info, "Creating %d worker(s)." % self._rayTracerParameters._parallelThreads)
        _workers = [Worker(workerId=i) for i in range(self._rayTracerParameters._parallelThreads)]

        # Assign tasks to workers
        self._log.log(LogLevel.Info, "Assigning tasks to %d worker(s)." % self._rayTracerParameters._parallelThreads)
        for i in range(self._rayTracerParameters._parallelThreads):
            _workers[i].assignTasks(_work[i])

        # Start workers
        self._log.log(LogLevel.Info, "Starting %d worker(s)." % self._rayTracerParameters._parallelThreads)
        for i in range(self._rayTracerParameters._parallelThreads):
            _workers[i].startWorking()

        # Wait for workers to finish
        time.sleep(1.0)
        self._log.log(LogLevel.Info, "Waiting for all worker(s) to finish.")
        _unfinishedWorkers = [i for i in range(self._rayTracerParameters._parallelThreads)]
        while(not len(_unfinishedWorkers) == 0):
            for i in _unfinishedWorkers:
                if _workers[i].isDone():
                    self._log.log(LogLevel.Info, "Worker with ID %d (%d total) finished." % (i, self._rayTracerParameters._parallelThreads))
                    _unfinishedWorkers.remove(i)
            if not len(_unfinishedWorkers) == 0:
                time.sleep(0.20)

        # Gather results
        self._log.log(LogLevel.Info, "Gathering results.")
        _results = [_workers[i].getWorkerResults() for i in range(self._rayTracerParameters._parallelThreads)]

        # Return results
        self._log.log(LogLevel.Info, "Ray-tracing simulation completed.")
        return self._joinTracerEngineResults(_results)


    def _joinTracerEngineResults(self, individualResultsArray):
        # TODO: complete this
        print(individualResultsArray)
        return individualResultsArray


    def _divideWorkInParts(self):
        _dividedWork = [WorkDefinition(rayTracerData=self) for i in range(self._rayTracerParameters._parallelThreads)]

        # If there are multiple sources, give each worker some
        if len(self._sources) > 1:
            # TODO: complete this
            pass

        # If there are multiple receivers, give each worker some
        elif len(self._receivers) > 1:
            # TODO: complete this
            pass

        # If there's a single source and a single receiver, give each worker a fraction of the total angular range
        else:
            # TODO: complete this
            pass

        return _dividedWork


    def tracerEngine(self, tasks, workerId):
        # TODO: complete this. This is the part that actually does the tracing,
        # from a source to a receiver on a given environment
        _workerStr = "[Worker %d]:" % workerId

        # print("%s > Started (PID: %d)." % (_workerStr, os.getpid()))
        self._log.log(LogLevel.Info, "%s > Started (PID: %d)." % (_workerStr, os.getpid()))

        rayTracerData = tasks._rayTracerData
        enabledSources = tasks._enabledSources
        enabledReceivers = tasks._enabledReceivers
        angularRange = tasks._angularRange

        self._log.log(LogLevel.Info, "%s   Data: " % _workerStr + str(rayTracerData))
        self._log.log(LogLevel.Info, "%s   Enabled sources: " % _workerStr + str(enabledSources))
        self._log.log(LogLevel.Info, "%s   Enabled receivers: " % _workerStr + str(enabledReceivers))
        self._log.log(LogLevel.Info, "%s   Angular range: " % _workerStr + str(angularRange))

        _workerResults = TracerEngineResults()

        # for i in range(1000):
        #     for j in range(2):
        #         a = numpy.fft.fft([k for k in range(1000)])
        #         if len(a) == 0:
        #             print("it's zero")

        _t = 10.0 * numpy.random.random()
        # print("Waiting %.1f s" % _t)
        # sys.stdout.flush()
        time.sleep(_t)
        # time.sleep(2.0)

        self._log.log(LogLevel.Info, "%s < Finished (PID: %d)." % (_workerStr, os.getpid()))
        return _workerResults

