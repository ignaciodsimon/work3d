'''
    This file contains the classes used in the module "geometry.py", used to
    load DAE files with geometries, materials and effects.

    Joe Simon 2018.
'''


class Asset:
    def __init__(self):
        self.authoringTool = None
        self.created = None
        self.modified = None
        self.unitMeter = None
        self.unitName = None
        self.upAxis = None


class Point:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

    def __str__(self):
        return "[%f, %f, %f]" % (self.x, self.y, self.z)


class Triangle:
    def __init__(self):
        self.p1 = Point()
        self.p2 = Point()
        self.p3 = Point()
        self._material = None
        self._color = None

    def __str__(self):
        return "[%f, %f, %f; %f, %f, %f; %f, %f, %f] Mat: %s, Color: %s" % (self.p1.x, self.p1.y, self.p1.z, self.p2.x, self.p2.y, self.p2.z, self.p3.x, self.p3.y, self.p3.z, str(self._material), str(self._color))


class Line:
    def __init__(self):
        self.p1 = Point()
        self.p2 = Point()

    def __str__(self):
        return "[%f, %f, %f --> %f, %f, %f]" % (self.p1.x, self.p1.y, self.p1.z, self.p2.x, self.p2.y, self.p2.z)


class Lines:
    def __init__(self):
        self._count = None
        self._material = None
        self._inputs = []
        self._p = []


class Mesh:
    def __init__(self):
        self._sources = []
        self._vertices = []
        self._triangles = []
        self._lines = []

    def __str__(self):
        _string = "Sources: "
        for i in range(len(self._sources)):
            _string += "\n  %d: " % i + str(self._sources[i])

        _string += "\nVertices: "
        for i in range(len(self._vertices)):
            _string += "\n  %d: \n" % i + str(self._vertices[i])

        _string += "\nTriangles: "
        for i in range(len(self._triangles)):
            _string += "\n  %d: " % i + str(self._triangles[i])

        return _string


class Source:
    def __init__(self):
        self._id = None
        self._floatArray = []
        self._techniqueCommon = []

    def __str__(self):
        return "Float array: " + str(self._floatArray) + "\nTechnique common: " + str(self._techniqueCommon)


class TechniqueCommon:
    def __init__(self):
        self._accessor = []


class Accessor:
    def __init__(self):
        self._param = []
        self._count = 0
        self._source = None
        self._stride = None


class Param:
    def __init__(self):
        self._name = None
        self._type = None


class Vertices:
    def __init__(self):
        self._id = None
        self._inputs = []

    def __str__(self):
        _string = "Inputs:"
        for i in range(len(self._inputs)):
            _string += "\n  %d: " % i + str(self._inputs[i])
        return _string


class Input:
    def __init__(self):
        self._semantic = None
        self._source = None
        self._offset = None


class Triangles:
    def __init__(self):
        self._count = None
        self._material = None
        self._inputs = []
        self._p = []


class Geometry:
    def __init__(self, ):
        self._id = None
        self._meshes = []


class VisualScene:
    def __init__(self, ):
        self._id = None
        self._instanceGeometries = []


class InstanceMaterial:
    def __init__(self, ):
        self._symbol = None
        self._target = None


class InstanceGeometry:
    def __init__(self,):
        self._url = None
        self._instanceMaterials = []


class Material:
    def __init__(self,):
        self._id = None
        self._name = None
        self._url = None

    def __str__(self):
        return "[%s='%s']" % (self._id, self._name)


class Effect:
    def __init__(self,):
        self._id = None
        self._color = None
