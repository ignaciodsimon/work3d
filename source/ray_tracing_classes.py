class ReceiverDefinition:
    def __init__(self):
        self._type = ReceiverType.Point
        self._location = [0.0, 0.0, 0.0]


class EnvironmentParameters:
    def __init__(self):
        self._soundSpeed = 343.0
        self._temperature = 20.0


class SourceDefinition:
    def __init__(self):
        self._type = SourceType.Point
        self._directivity = Directivity()
        self._location = [0.0, 0.0, 0.0]


class DirectivityType:
    Omni = 0


class Directivity:
    def __init__(self, type=None):
        if type is None:
            self._type = DirectivityType.Omni
        else:
            self._type = type

    def __call__(self, *args, **kwargs):
        if not len(args) == 2:
            raise Exception("The directivity class must be called with two arguments (the elevation and azimuth).")

        if self._type == DirectivityType.Omni:
            return 1.0
        else:
            _elevation = float(args[0])
            _azimuth = float(args[1])
            _directivity = 1.0
            print("The directivity for elevation: %.10f and azimuth %.10f is %.10f." % (_elevation, _azimuth, _directivity))
            return _directivity


class SourceType:
    Point = 0


class ReceiverType:
    Point = 0


class RayTracerParameters:
    def __init__(self):
        self._angularResolution = 1.0
        self._maxBouncesPerRay = 10
        self._cornerScattering = False
        self._parallelThreads = 4
        self._enableHighFrequencyAirAbsorption = True


class TracerEngineResults:
    def __init__(self):
        pass


class WorkDefinition():
    def __init__(self, rayTracerData):
        self._rayTracerData = rayTracerData
        self._enabledSources = []
        self._enabledReceivers = []
        self._angularRange = []
