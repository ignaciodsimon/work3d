'''
    This module can load DAE files and extract the information of geometries,
    materials and effects. All data is maped to classes defined in the module
    "geometry_classes.py"

    Joe Simon 2018.
'''


import numpy as np
import xml.etree.ElementTree
from logger import *
from geometry_classes import *


class LibraryGeometries:
    def __init__(self):
        self._geometries = []
        self._asset = None
        self._log = Logger()
        self._formedTriangles = None
        self._formedLines = None
        self._visualScenes = []
        self._materials = []
        self._effects = []

    def __str__(self):
        _meshesString = ""
        for i in range(len(self._meshes)):
            _meshesString += "\n> Mesh %d:\n" % i + str(self._meshes[i])
        return _meshesString

        self.loadGeometryFromString()

    def loadGeometryFromString(self, string, stopAtException=True):
        _root = xml.etree.ElementTree.fromstring(_exampleXML)
        self._loadFromXML(_root, stopAtException)

    def loadGeometryFromFile(self, filename, stopAtException=True):
        try:
            self._log.log(LogLevel.Info, "Trying to load data from file '%s'." % filename)
            _root = xml.etree.ElementTree.parse(filename).getroot()
        except Exception as ex:
            self._log.log(LogLevel.Ex, "The file '%s' cannot be parsed as XML." % filename)
            self._log.log(LogLevel.Ex, "Exception message: %s" % str(ex))
            raise ex
            return False

        self._loadFromXML(_root, stopAtException)

    def _loadFromXML(self, _root, stopAtException=True):

        self._log.log(LogLevel.Info, "File open. Loading geometries ...")
        logDepth = 0

        # Load asset (general info)
        try:
            _asset = self._findAll(_root, "asset", logDepth + 1)[0]
            _contributor = self._findAll(_asset, "contributor", logDepth + 1)[0]
            self._asset = Asset()
            self._asset.authoringTool = self._findAll(_contributor, "authoring_tool", logDepth + 1)

            self._asset.created = self._findAll(_asset, "created", logDepth + 1)[0].text
            self._asset.modified = self._findAll(_asset, "modified", logDepth + 1)[0].text
            self._asset.created = self._findAll(_asset, "created", logDepth + 1)[0].text

            _unit = self._findAll(_asset, "unit", logDepth + 1)[0]
            self._asset.unitMeter = _unit.attrib.get('meter')
            self._asset.unitName = _unit.attrib.get('name')

        except Exception as ex:
            self._log.log(LogLevel.Err, "An exception ocurred while parsing the file header (asset).")
            self._log.log(LogLevel.Err, "Exception message: %s" % ex)
            if stopAtException:
                raise ex

        # Load the visual scenes
        try:
            _readVisualScenesLib = self._findAll(_root, "library_visual_scenes")
            self._log.log(LogLevel.Info, "Found %d visual scenes libraries." % len(_readVisualScenesLib))
            for _lib in _readVisualScenesLib:

                _visualScenes = self._findAll(_lib, "visual_scene")
                self._log.log(LogLevel.Info, "Found %d visual scene(s) in library." % len(_visualScenes))

                for _visualScene in _visualScenes:
                    _newVisualScene = VisualScene()
                    _newVisualScene._id = _visualScene.attrib.get('id')

                    _instanceGeometries = self._findAll(_visualScene, "instance_geometry", logDepth + 1)
                    _newVisualScene._instanceGeometries = [(self._parseInstanceGeometry(_inst, logDepth + 1)) for _inst in _instanceGeometries]
                    self._visualScenes.append(_newVisualScene)

        except Exception as ex:
            self._log.log(LogLevel.Err, "An exception ocurred while parsing the file (library_visual_scenes). Stopping.")
            self._log.log(LogLevel.Err, "Exception message: %s" % ex)
            if stopAtException:
                raise ex

        # Load the materials
        try:
            _readMaterialsLibrary = self._findAll(_root, "library_materials", logDepth + 1)
            for _lib in _readMaterialsLibrary:
                _materials = self._findAll(_lib, "material", logDepth + 1)

                for _material in _materials:
                    _newMaterial = Material()
                    _newMaterial._id = _material.attrib.get('id')
                    _newMaterial._name = _material.attrib.get('name')

                    _instanceEffects = self._findAll(_material, 'instance_effect', logDepth + 1)
                    if len(_instanceEffects) > 0:
                        _newMaterial._url = []
                        for _eff in _instanceEffects:
                            _newMaterial._url.append(_eff.attrib.get('url'))

                    self._materials.append(_newMaterial)

        except Exception as ex:
            self._log.log(LogLevel.Err, "An exception ocurred while parsing the file (library_materials). Stopping.")
            self._log.log(LogLevel.Err, "Exception message: %s" % ex)
            if stopAtException:
                raise ex

        # Load the effects
        try:
            _readEffectsLibrary = self._findAll(_root, "library_effects", logDepth + 1)
            self._log.log(LogLevel.Info, "Found %d effects libraries." % len(_readEffectsLibrary))

            for _lib in _readEffectsLibrary:
                self._log.log(LogLevel.Info, "  Found %d effects(s) in library." % len(_lib))
                _effects = self._findAll(_lib, "effect", logDepth + 1)
                for _effect in _effects:
                    _newEffect = Effect()
                    _newEffect._id = _effect.attrib.get('id')
                    _colors = self._findAll(_effect, "color", logDepth + 1)
                    if len(_colors) > 0:
                        _newEffect._color = self._parseNumbersArray(_colors[0].text, logDepth + 4, applyScaling=False)

                    self._log.log(LogLevel.Info, "    Found effect with ID '%s' and color '%s'." % (_newEffect._id, _newEffect._color))
                    self._effects.append(_newEffect)

        except Exception as ex:
            self._log.log(LogLevel.Err, "An exception ocurred while parsing the file (library_materials). Stopping.")
            self._log.log(LogLevel.Err, "Exception message: %s" % ex)
            if stopAtException:
                raise ex

        # Load geometries
        try:
            _readGeometries = self._findAll(_root, "geometry", logDepth + 1)
            self._log.log(LogLevel.Info, "Found %d geometries." % len(_readGeometries))
            for _geometry in _readGeometries:
                _newGeometry = Geometry()
                _newGeometry._id = _geometry.attrib.get('id')
                _meshes = self._findAll(_geometry, "mesh", logDepth + 1)
                self._log.log(LogLevel.Info, "Found %d mesh item(s)." % len(_meshes))
                _newGeometry._meshes = [self._parseMesh(_meshes[i], logDepth + 1) for i in range(len(_meshes))]
                self._geometries.append(_newGeometry)

            # Form triangles and lines
            self._formedTriangles = self.formTriangles()
            self._formedLines = self.formLines()

        except Exception as ex:
            self._log.log(LogLevel.Err, "An exception ocurred while parsing the file (library_geometries). Stopping.")
            self._log.log(LogLevel.Err, "Exception message: %s" % ex)
            if stopAtException:
                raise ex

        return True

    def _parseInstanceGeometry(self, inst, logDepth=0):
        self._log.log(LogLevel.Info, "%sParsing instance geometry." % (' ' * logDepth))
        _instance = InstanceGeometry()
        _instance._url = inst.attrib.get('url')

        _materials = self._findAll(inst, 'instance_material', logDepth + 1)
        self._log.log(LogLevel.Info, "%sFound %d material(s)." % (' ' * logDepth, len(_materials)))
        _instance._instanceMaterials = []
        for _material in _materials:
            _newMaterial = InstanceMaterial()
            _newMaterial._symbol = _material.attrib.get('symbol')
            _newMaterial._target = _material.attrib.get('target')
            self._log.log(LogLevel.Info, "%s  Material '%s' with target '%s'." % (' ' * logDepth, _newMaterial._symbol, _newMaterial._target))
            _instance._instanceMaterials.append(_newMaterial)
        return _instance

    def _parseMesh(self, mesh, logDepth=0):
        self._log.log(LogLevel.Info, "%sParsing mesh." % (' ' * logDepth))
        _mesh = Mesh()

        # Find all sources
        _sources = self._findAll(mesh, 'source', logDepth + 1)
        self._log.log(LogLevel.Info, "%sFound %d sources block(s)." % (' ' * logDepth, len(_sources)))
        _mesh._sources = [self._parseSource(_sources[i], logDepth + 1) for i in range(len(_sources))]

        # Find all vertices
        _vertices = self._findAll(mesh, 'vertices', logDepth + 1)
        self._log.log(LogLevel.Info, "%sFound %d vertices block(s)." % (' ' * logDepth, len(_vertices)))
        _mesh._vertices = [self._parseVertices(_vertices[i], logDepth + 1) for i in range(len(_vertices))]

        # Find all triangles
        _triangles = self._findAll(mesh, 'triangles', logDepth + 1)
        self._log.log(LogLevel.Info, "%sFound %d _triangles block(s)." % (' ' * logDepth, len(_triangles)))
        _mesh._triangles = [self._parseTriangles(_triangles[i], logDepth + 1) for i in range(len(_triangles))]

        _lines = self._findAll(mesh, 'lines', logDepth + 1)
        self._log.log(LogLevel.Info, "%sFound %d lines block(s)." % (' ' * logDepth, len(_lines)))
        _mesh._lines = [self._parseLines(_lines[i], logDepth + 1) for i in range(len(_lines))]

        return _mesh

    def _parseSource(self, source, logDepth=0):
        _source = Source()
        self._log.log(LogLevel.Info, "%sParsing source." % (' ' * logDepth))
        _source._id = source.attrib.get('id')
        self._log.log(LogLevel.Info, "%s  ID: '%s'" % (' ' * logDepth, _source._id))

        # Parse float array
        _floats = self._findAll(source, 'float_array')
        if len(_floats) == 0:
            self._log.log(LogLevel.Warn, "%s  No floats array found!" % (' ' * logDepth))
            _source._floatArray = []
        else:
            self._log.log(LogLevel.Info, "%s  Found associated floats array." % (' ' * logDepth))
            _source._floatArray = self._parseNumbersArray(_floats[0].text, logDepth + 1, applyScaling=True)

        # Parse technique common
        _techniqueCommonElement = self._findAll(source, 'technique_common')
        if not len(_techniqueCommonElement) == 1:
            raise Exception("More than one 'technique_common' found in a source block. I'm comfused.")
        _techniqueCommon = self._parseTechniqueCommon(_techniqueCommonElement[0], logDepth + 1)
        return _source

    def _parseTechniqueCommon(self, source, logDepth=0):
        # Find accessor with properties
        _accessors = self._findAll(source, 'accessor')
        if not len(_accessors) == 1:
            raise Exception("More than one 'accessor' found in a 'technique_common' block. I'm comfused.")

        self._log.log(LogLevel.Info, "%sParsing TechniqueCommon." % (' ' * logDepth))
        _tech = TechniqueCommon()
        _tech._accessor = Accessor()
        _tech._accessor._count = _accessors[0].attrib.get('count')
        _tech._accessor._source = _accessors[0].attrib.get('source')
        _tech._accessor._stride = _accessors[0].attrib.get('stride')

        # Find params
        _params = self._findAll(_accessors[0], 'param')
        _tech._accessor._param = [self._parseParam(_params[i], logDepth + 1) for i in range(len(_params))]
        return _tech

    def _parseParam(self, source, logDepth=0):
        self._log.log(LogLevel.Info, "%sParsing Param." % (' ' * logDepth))
        _param = Param()
        _param._name = source.attrib.get('name')
        _param._type = source.attrib.get('type')
        return _param

    def _parseVertices(self, source, logDepth=0):
        _vertices = Vertices()
        _inputs = self._findAll(source, 'input')
        self._log.log(LogLevel.Info, "%sFound %d inputs." % (' ' * logDepth, len(_inputs)))
        _vertices._inputs = [self._parseInput(_in, logDepth + 1) for _in in _inputs]
        _vertices._id = source.attrib.get('id')
        return _vertices

    def _parseInput(self, source, logDepth=0):
        self._log.log(LogLevel.Info, "%sParsing input." % (' ' * logDepth))
        _input = Input()
        _input._semantic = source.attrib.get('semantic')
        _input._source = source.attrib.get('source')
        _input._offset = source.attrib.get('offset')
        return _input

    def _parseTriangles(self, source, logDepth=0):
        self._log.log(LogLevel.Info, "%sParsing triangles." % (' ' * logDepth))
        _triangles = Triangles()
        _triangles._count = source.attrib.get('count')
        _triangles._material = source.attrib.get('material')

        _inputs = self._findAll(source, 'input', logDepth + 1)
        self._log.log(LogLevel.Info, "%sFound %d inputs." % (' ' * logDepth, len(_inputs)))
        _triangles._inputs = [self._parseInput(_in, logDepth + 1) for _in in _inputs]

        _ints = self._findAll(source, 'p')[0]
        self._log.log(LogLevel.Info, "%sFound p vector." % (' ' * logDepth))
        _triangles._p = self._parseNumbersArray(_ints.text, asInts=True, logDepth=logDepth + 1, applyScaling=False)

        return _triangles

    def _parseLines(self, source, logDepth=0):
        self._log.log(LogLevel.Info, "%sParsing lines." % (' ' * logDepth))
        _lines = Lines()
        _lines._count = source.attrib.get('count')

        _inputs = self._findAll(source, 'input', logDepth + 1)
        self._log.log(LogLevel.Info, "%sFound %d inputs." % (' ' * logDepth, len(_inputs)))
        _lines._inputs = [self._parseInput(_in, logDepth + 1) for _in in _inputs]

        _ints = self._findAll(source, 'p')[0]
        self._log.log(LogLevel.Info, "%sFound p vector." % (' ' * logDepth))
        _lines._p = self._parseNumbersArray(_ints.text, asInts=True, logDepth=logDepth + 1, applyScaling=False)

        return _lines

    def _findAll(self, root, name, logDepth=0):
        _found = []
        for _item in root.getiterator():
            if _item.tag.split('}')[-1] == name:
                _found.append(_item)
        return _found

    def _parseNumbersArray(self, text, logDepth=0, asInts=False, applyScaling=False):

        if not applyScaling:
            _scalingFactor = 1.0
        else:
            try:
                _scalingFactor = 1.0 * float(self._asset.unitMeter)
                self._log.log(LogLevel.Info, "%sApplying scaling factor of %f." % (' ' * logDepth, _scalingFactor))
            except Exception as ex:
                self._log.log(LogLevel.Err, "%sCould not parse '%s' into a float for the scaling factor." % (' ' * logDepth, self._asset.unitMeter))
                raise ex

        try:
            _split = text.split()
            if asInts:
                _parsed = [int(_scalingFactor * int(_split[i])) for i in range(len(_split))]
            else:
                _parsed = [_scalingFactor * float(_split[i]) for i in range(len(_split))]
        except Exception as ex:
            self._log.log(LogLevel.Err, "%sCould not parse '%s' into a float array." % (' ' * logDepth, text))
            raise ex

        if asInts:
            self._log.log(LogLevel.Info, "%sParsed %d integers." % (' ' * logDepth, len(_parsed)))
        else:
            self._log.log(LogLevel.Info, "%sParsed %d floats." % (' ' * logDepth, len(_parsed)))
        return _parsed

    def _findFloatArray(self, _source):
        for _floatArray in _source:
            if _floatArray.tag.split('}')[-1] == 'float_array':
                return _floatArray

    def formLines(self, logDepth=0):
        if len(self._geometries) == 0:
            self._log.log(LogLevel.Err, "%sThere are no geometries loaded." % (' ' * logDepth))
            return []

        _lines = []
        _impossibleLines = 0
        for _geometry in self._geometries:
            for i in range(len(_geometry._meshes)):
                # Find sources that correspond to vertices
                _inputID = None
                _verticesID = None
                for _input in _geometry._meshes[i]._vertices[0]._inputs:
                    if _input._semantic.lower() == "position":
                        _inputID = _input._source
                        _verticesID = _geometry._meshes[i]._vertices[0]._id
                        self._log.log(LogLevel.Info, "%sFound source-ID in vertices list: '%s'." % (' ' * logDepth, _inputID))
                        break
                if _inputID is None:
                    self._log.log(LogLevel.Err, "%sCannot find the source-ID in the vertices list." % (' ' * logDepth))
                    break

                # Find the source that matches the ID found
                _foundSource = None
                for _source in _geometry._meshes[i]._sources:
                    if _source._id == _inputID or ("#%s" % _source._id) == _inputID:
                        _foundSource = _source
                        self._log.log(LogLevel.Info, "%sFound source with ID: '%s'." % (' ' * logDepth, _inputID))
                        break
                if _foundSource is None:
                    self._log.log(LogLevel.Err, "%sCannot find the source with ID '%s'." % (' ' * logDepth, _inputID))
                    break

                # Find the triangles data
                _linesData = None
                for _linesList in _geometry._meshes[i]._lines:
                    for _input in _linesList._inputs:
                        if _input._source == _verticesID or ("#%s" % _verticesID) == _input._source:
                            _linesData = _linesList
                            self._log.log(LogLevel.Info, "%sFound lines with ID: '%s'." % (' ' * logDepth, _verticesID))
                            break
                if _linesData is None:
                    self._log.log(LogLevel.Err, "%sCannot find the triangles with ID '%s'." % (' ' * logDepth, _verticesID))
                    break

                try:
                    for i in range(int(len(_linesData._p) / 2)):
                        _lineIndexes = _linesData._p[i * 2 : (i * 2) + 2]

                        _p1 = [_foundSource._floatArray[(_lineIndexes[0] * 3) + 0],
                               _foundSource._floatArray[(_lineIndexes[0] * 3) + 1],
                               _foundSource._floatArray[(_lineIndexes[0] * 3) + 2], ]
                        _p2 = [_foundSource._floatArray[(_lineIndexes[1] * 3) + 0],
                               _foundSource._floatArray[(_lineIndexes[1] * 3) + 1],
                               _foundSource._floatArray[(_lineIndexes[1] * 3) + 2], ]

                        _newLine = Line()
                        _newLine.p1.x = _p1[0]
                        _newLine.p1.y = _p1[1]
                        _newLine.p1.z = _p1[2]
                        _newLine.p2.x = _p2[0]
                        _newLine.p2.y = _p2[1]
                        _newLine.p2.z = _p2[2]

                        _lines.append(_newLine)
                        self._log.log(LogLevel.Debug, "%s  Formed line %s." % (' ' * logDepth, str(_newLine)))

                except Exception as ex:
                    _impossibleLines += 1

        self._log.log(LogLevel.Info, "%s  Formed %d line(s) in total." % (' ' * logDepth, len(_lines)))
        if _impossibleLines > 0:
            self._log.log(LogLevel.Err, "%s  %d line(s) could not be formed!" % (' ' * logDepth, _impossibleLines))
        return _lines

    def formTriangles(self, logDepth=0):
        if len(self._geometries) == 0:
            self._log.log(LogLevel.Err, "%sThere are no geometries loaded." % (' ' * logDepth))
            return []

        _triangles = []
        _impossibleTriangles = 0
        for _geometry in self._geometries:
            for i in range(len(_geometry._meshes)):
                # Find sources that correspond to vertices
                _inputID = None
                _verticesID = None
                for _input in _geometry._meshes[i]._vertices[0]._inputs:
                    if _input._semantic.lower() == "position":
                        _inputID = _input._source
                        _verticesID = _geometry._meshes[i]._vertices[0]._id
                        self._log.log(LogLevel.Info, "%sFound source-ID in vertices list: '%s'." % (' ' * logDepth, _inputID))
                        break
                if _inputID is None:
                    self._log.log(LogLevel.Err, "%sCannot find the source-ID in the vertices list." % (' ' * logDepth))
                    break

                # Find the source that matches the ID found
                _foundSource = None
                for _source in _geometry._meshes[i]._sources:
                    if _source._id == _inputID or ("#%s" % _source._id) == _inputID:
                        _foundSource = _source
                        self._log.log(LogLevel.Info, "%sFound source with ID: '%s'." % (' ' * logDepth, _inputID))
                        break
                if _foundSource is None:
                    self._log.log(LogLevel.Err, "%sCannot find the source with ID '%s'." % (' ' * logDepth, _inputID))
                    break

                # Find the triangles data
                _trianglesData = None
                for _triangleList in _geometry._meshes[i]._triangles:
                    for _input in _triangleList._inputs:
                        if _input._source == _verticesID or ("#%s" % _verticesID) == _input._source:
                            _trianglesData = _triangleList
                            self._log.log(LogLevel.Info, "%sFound triangles with ID: '%s'." % (' ' * logDepth, _verticesID))
                            break
                if _trianglesData is None:
                    self._log.log(LogLevel.Err, "%sCannot find the triangles with ID '%s'." % (' ' * logDepth, _verticesID))
                    break

                try:
                    for i in range(int(len(_trianglesData._p) / 3)):
                        _triangleIndexes = _trianglesData._p[i * 3 : (i * 3) + 3]

                        _p1 = [_foundSource._floatArray[(_triangleIndexes[0] * 3) + 0],
                               _foundSource._floatArray[(_triangleIndexes[0] * 3) + 1],
                               _foundSource._floatArray[(_triangleIndexes[0] * 3) + 2], ]
                        _p2 = [_foundSource._floatArray[(_triangleIndexes[1] * 3) + 0],
                               _foundSource._floatArray[(_triangleIndexes[1] * 3) + 1],
                               _foundSource._floatArray[(_triangleIndexes[1] * 3) + 2], ]
                        _p3 = [_foundSource._floatArray[(_triangleIndexes[2] * 3) + 0],
                               _foundSource._floatArray[(_triangleIndexes[2] * 3) + 1],
                               _foundSource._floatArray[(_triangleIndexes[2] * 3) + 2], ]
                        _newTriangle = Triangle()
                        _newTriangle.p1.x = _p1[0]
                        _newTriangle.p1.y = _p1[1]
                        _newTriangle.p1.z = _p1[2]
                        _newTriangle.p2.x = _p2[0]
                        _newTriangle.p2.y = _p2[1]
                        _newTriangle.p2.z = _p2[2]
                        _newTriangle.p3.x = _p3[0]
                        _newTriangle.p3.y = _p3[1]
                        _newTriangle.p3.z = _p3[2]

                        # Find material and associated effect
                        _instanceGeometryID = _geometry._id
                        _foundMatAndColor = False
                        for _visualScene in self._visualScenes:
                            if _foundMatAndColor:
                                break
                            for _instanceGeometry in _visualScene._instanceGeometries:
                                if _foundMatAndColor:
                                    break
                                if "#%s" % (_instanceGeometryID) == _instanceGeometry._url:
                                    for _mat in _instanceGeometry._instanceMaterials:
                                        if _foundMatAndColor:
                                            break
                                        if _trianglesData._material == _mat._symbol:
                                            for _material in self._materials:
                                                if _foundMatAndColor:
                                                    break
                                                if "#%s" % (_material._id) == _mat._target:
                                                    for _effect in self._effects:
                                                        for _url in _material._url:
                                                            if _foundMatAndColor:
                                                                break
                                                            if "#%s" % (_effect._id) == _url:
                                                                _newTriangle._material = _material
                                                                _newTriangle._color = _effect._color
                                                                _foundMatAndColor = True
                                                                break

                        _triangles.append(_newTriangle)
                        self._log.log(LogLevel.Debug, "%s  Formed triangle %s." % (' ' * logDepth, str(_newTriangle)))
                except Exception as ex:
                    _impossibleTriangles += 1

        self._log.log(LogLevel.Info, "%s  Formed %d triangle(s) in total." % (' ' * logDepth, len(_triangles)))
        if _impossibleTriangles > 0:
            self._log.log(LogLevel.Err, "%s  %d triangle(s) could not be formed!" % (' ' * logDepth, _impossibleTriangles))
        return _triangles

    def displayGeometry(self, solid=True, logDepth=0, transparent=True):
        from mpl_toolkits.mplot3d import Axes3D
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
        import matplotlib.pyplot as plt

        fig = plt.figure()
        ax = Axes3D(fig)

        _somethingToShow = False
        if len(self._formedTriangles) > 0:

            # -- Plot the triangles
            for index, _triangle in enumerate(self._formedTriangles):
                _somethingToShow = True
                if solid:
                    _collection = Poly3DCollection([list(zip([_triangle.p1.x, _triangle.p2.x, _triangle.p3.x], \
                                                             [_triangle.p1.y, _triangle.p2.y, _triangle.p3.y], \
                                                             [_triangle.p1.z, _triangle.p2.z, _triangle.p3.z]))],
                                                   linewidths=0.1,
                                                   alpha=0.5 if transparent else 1.0)
                    _collection.set_facecolor(_triangle._color[0:3])
                    _collection.set_edgecolor(_triangle._color[0:3])
                    ax.add_collection3d(_collection, zs='z')
                else:
                    plt.plot([_triangle.p1.x, _triangle.p2.x, _triangle.p3.x, _triangle.p1.x],
                             [_triangle.p1.y, _triangle.p2.y, _triangle.p3.y, _triangle.p1.y],
                             [_triangle.p1.z, _triangle.p2.z, _triangle.p3.z, _triangle.p1.z], color=_triangle._color[0:3], linewidth=0.25)

            # -- Plot the contour lines
            for _line in self._formedLines:
                _somethingToShow = True
                plt.plot([_line.p1.x, _line.p2.x], \
                         [_line.p1.y, _line.p2.y], \
                         [_line.p1.z, _line.p2.z], color='k', linewidth=2.0)

        if _somethingToShow:
            plt.show()

    '''
    def displayGeometry2(self, logDepth=0):
        self._log.log(LogLevel.Info, "\n%sDisplaying geometry" % (' ' * logDepth))
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # Form triangles is needed
        if self._formedTriangles == None:
            self._formedTriangles = self.formTriangles()

        # Form lines if needed
        if self._formedLines == None:
            self._formedLines = self.formLines()

        self._log.log(LogLevel.Info, "%sDisplaying geometry with %d triangles" % (' ' * logDepth, len(self._formedTriangles)))
        if len(self._formedTriangles) > 0:
            for _line in self._formedLines:
                plt.plot([_line.p1.x, _line.p2.x],
                         [_line.p1.y, _line.p2.y],
                         [_line.p1.z, _line.p2.z], color='k', linewidth=1.5)
            for _triangle in self._formedTriangles:
                plt.plot([_triangle.p1.x, _triangle.p2.x, _triangle.p3.x, _triangle.p1.x],
                         [_triangle.p1.y, _triangle.p2.y, _triangle.p3.y, _triangle.p1.y],
                         [_triangle.p1.z, _triangle.p2.z, _triangle.p3.z, _triangle.p1.z], color=_triangle._color[0:3], linewidth=0.25)
                # print("Mat:", _triangle._material._name, _triangle._color)

            plt.grid(0)
            plt.show()

    # self._log.log(LogLevel.Info, "%sInfo on geometry:" % (' ' * logDepth))
    # self._log.log(LogLevel.Info, "%s" % (self))
    '''

if __name__ == "__main__":

    _exampleXML = '<?xml version="1.0" encoding="UTF-8" standalone="no" ?><COLLADA xmlns="http://www.collada.org/2005/11/COLLADASchema" version="1.4.1">\
        <asset><contributor><authoring_tool>SketchUp 17.2.2555</authoring_tool></contributor><created>2018-06-14T12:46:32Z</created><modified>\
        2018-06-14T12:46:32Z</modified><unit meter="0.0254" name="inch" /><up_axis>Z_UP</up_axis></asset><library_cameras><camera id="ID1"\
        name="skp_camera_Last_Saved_SketchUp_View"><optics><technique_common><perspective><yfov>38.45713</yfov><aspect_ratio>0</aspect_ratio>\
        <znear>1</znear><zfar>1000</zfar></perspective></technique_common></optics></camera></library_cameras><library_visual_scenes>\
        <visual_scene id="ID2"><node name="SketchUp"><instance_geometry url="#ID3"><bind_material><technique_common><instance_material\
        symbol="Material2" target="#ID4"><bind_vertex_input semantic="UVSET0" input_semantic="TEXCOORD" input_set="0" /></instance_material>\
        <instance_material symbol="Material3" target="#ID9"><bind_vertex_input semantic="UVSET0" input_semantic="TEXCOORD" input_set="0" />\
        </instance_material></technique_common></bind_material></instance_geometry><instance_geometry url="#ID13"><bind_material><technique_common>\
        <instance_material symbol="Material2" target="#ID14"><bind_vertex_input semantic="UVSET0" input_semantic="TEXCOORD" input_set="0" />\
        </instance_material><instance_material symbol="Material3" target="#ID9"><bind_vertex_input semantic="UVSET0" input_semantic="TEXCOORD"\
        input_set="0" /></instance_material></technique_common></bind_material></instance_geometry><instance_geometry url="#ID21"><bind_material>\
        <technique_common><instance_material symbol="Material2" target="#ID22"><bind_vertex_input semantic="UVSET0" input_semantic="TEXCOORD"\
        input_set="0" /></instance_material><instance_material symbol="Material3" target="#ID9"><bind_vertex_input semantic="UVSET0"\
        input_semantic="TEXCOORD" input_set="0" /></instance_material></technique_common></bind_material></instance_geometry><instance_geometry\
        url="#ID29"><bind_material><technique_common><instance_material symbol="Material2" target="#ID30"><bind_vertex_input semantic="UVSET0"\
        input_semantic="TEXCOORD" input_set="0" /></instance_material><instance_material symbol="Material3" target="#ID9"><bind_vertex_input\
        semantic="UVSET0" input_semantic="TEXCOORD" input_set="0" /></instance_material></technique_common></bind_material></instance_geometry>\
        <node name="skp_camera_Last_Saved_SketchUp_View"><matrix>-0.6745777 0.3374377 -0.6565675 -353.9968 -0.7382039 -0.3083537 0.5999775 445.4157\
        2.775558e-17 0.889412 0.4571063 317.3609 0 0 0 1</matrix><instance_camera url="#ID1" /></node></node></visual_scene></library_visual_scenes>\
        <library_geometries><geometry id="ID3"><mesh><source id="ID6"><float_array id="ID11" count="42">0 196.8504 98.4252 78.74016 196.8504 0 0\
        196.8504 0 78.74016 196.8504 98.4252 0 196.8504 0 0 196.8504 98.4252 78.74016 196.8504 98.4252 78.74016 196.8504 0 0 196.8504 98.4252 0 0\
        0 0 0 98.4252 0 196.8504 0 0 0 98.4252 0 0 0</float_array><technique_common><accessor count="14" source="#ID11" stride="3"><param name="X"\
        type="float" /><param name="Y" type="float" /><param name="Z" type="float" /></accessor></technique_common></source><source id="ID7">\
        <float_array id="ID12" count="42">-0 1 -0 -0 1 -0 -0 1 -0 -0 1 -0 0 0 0 0 0 0 0 0 0 0 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 0 0 0 0 0 0</float_array>\
        <technique_common><accessor count="14" source="#ID12" stride="3"><param name="X" type="float" /><param name="Y" type="float" /><param name="Z"\
        type="float" /></accessor></technique_common></source><vertices id="ID8"><input semantic="POSITION" source="#ID6" /><input semantic="NORMAL"\
        source="#ID7" /></vertices><triangles count="4" material="Material2"><input offset="0" semantic="VERTEX" source="#ID8" />\
        <p>0 1 2 1 0 3 8 9 10 9 8 11</p></triangles><lines count="7" material="Material3"><input offset="0" semantic="VERTEX" source="#ID8" />\
        <p>4 5 6 5 7 6 7 4 5 12 4 13 13 12</p></lines></mesh></geometry><geometry id="ID13"><mesh><source id="ID16"><float_array id="ID19"\
        count="24">78.74016 0 98.4252 0 0 0 78.74016 0 0 0 0 98.4252 78.74016 0 0 78.74016 0 98.4252 0 0 98.4252 0 0 0</float_array><technique_common>\
        <accessor count="8" source="#ID19" stride="3"><param name="X" type="float" /><param name="Y" type="float" /><param name="Z" type="float" />\
        </accessor></technique_common></source><source id="ID17"><float_array id="ID20" count="24">0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 0 0 0 0 0 0 0 0 0 0 0</float_array>\
        <technique_common><accessor count="8" source="#ID20" stride="3"><param name="X" type="float" /><param name="Y" type="float" /><param name="Z"\
        type="float" /></accessor></technique_common></source><vertices id="ID18"><input semantic="POSITION" source="#ID16" /><input semantic="NORMAL"\
        source="#ID17" /></vertices><triangles count="2" material="Material2"><input offset="0" semantic="VERTEX" source="#ID18" /><p>0 1 2 1 0 3</p>\
        </triangles><lines count="4" material="Material3"><input offset="0" semantic="VERTEX" source="#ID18" /><p>4 5 6 5 7 6 7 4</p></lines></mesh>\
        </geometry><geometry id="ID21"><mesh><source id="ID24"><float_array id="ID27" count="42">78.74016 196.8504 0 78.74016 0 98.4252 78.74016 0 0\
        78.74016 196.8504 98.4252 78.74016 0 0 78.74016 196.8504 0 78.74016 196.8504 98.4252 78.74016 0 98.4252 78.74016 0 98.4252 0 196.8504 98.4252 0\
        0 98.4252 78.74016 196.8504 98.4252 0 0 98.4252 0 196.8504 98.4252</float_array><technique_common><accessor count="14" source="#ID27" stride="3">\
        <param name="X" type="float" /><param name="Y" type="float" /><param name="Z" type="float" /></accessor></technique_common></source><source id="ID25">\
        <float_array id="ID28" count="42">1 -0 -0 1 -0 -0 1 -0 -0 1 -0 -0 0 0 0 0 0 0 0 0 0 0 0 0 -0 -0 1 -0 -0 1 -0 -0 1 -0 -0 1 0 0 0 0 0 0</float_array>\
        <technique_common><accessor count="14" source="#ID28" stride="3"><param name="X" type="float" /><param name="Y" type="float" /><param name="Z"\
        type="float" /></accessor></technique_common></source><vertices id="ID26"><input semantic="POSITION" source="#ID24" /><input semantic="NORMAL"\
        source="#ID25" /></vertices><triangles count="4" material="Material2"><input offset="0" semantic="VERTEX" source="#ID26" /><p>0 1 2 1 0 3 8 9 10\
        9 8 11</p></triangles><lines count="7" material="Material3"><input offset="0" semantic="VERTEX" source="#ID26" /><p>4 5 5 6 7 6 4 7 12 7 6 13 13\
        12</p></lines></mesh></geometry><geometry id="ID29"><mesh><source id="ID32"><float_array id="ID35" count="24">78.74016 196.8504 0 0 0 0 0 196.8504\
        0 78.74016 0 0 78.74016 196.8504 0 0 196.8504 0 78.74016 0 0 0 0 0</float_array><technique_common><accessor count="8" source="#ID35" stride="3">\
        <param name="X" type="float" /><param name="Y" type="float" /><param name="Z" type="float" /></accessor></technique_common></source><source id="ID33">\
        <float_array id="ID36" count="24">0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 0 0 0 0 0 0 0 0 0 0</float_array><technique_common><accessor count="8" source="#ID36"\
        stride="3"><param name="X" type="float" /><param name="Y" type="float" /><param name="Z" type="float" /></accessor></technique_common></source><vertices\
        id="ID34"><input semantic="POSITION" source="#ID32" /><input semantic="NORMAL" source="#ID33" /></vertices><triangles count="2" material="Material2">\
        <input offset="0" semantic="VERTEX" source="#ID34" /><p>0 1 2 1 0 3</p></triangles><lines count="4" material="Material3"><input offset="0" semantic="VERTEX"\
        source="#ID34" /><p>4 5 6 4 7 6 5 7</p></lines></mesh></geometry></library_geometries><library_materials><material id="ID4" name="Color_G03"><instance_effect\
        url="#ID5" /></material><material id="ID9" name="edge_color000255"><instance_effect url="#ID10" /></material><material id="ID14" name="Color_E04"><instance_effect\
        url="#ID15" /></material><material id="ID22" name="Color_A05"><instance_effect url="#ID23" /></material><material id="ID30" name="Color_H03"><instance_effect\
        url="#ID31" /></material></library_materials><library_effects><effect id="ID5"><profile_COMMON><technique sid="COMMON"><lambert><diffuse><color>0.3960784\
        1 0.3960784 1</color></diffuse></lambert></technique></profile_COMMON></effect><effect id="ID10"><profile_COMMON><technique sid="COMMON"><constant><transparent\
        opaque="A_ONE"><color>0 0 0 1</color></transparent><transparency><float>1</float></transparency></constant></technique></profile_COMMON></effect><effect id="ID15">\
        <profile_COMMON><technique sid="COMMON"><lambert><diffuse><color>1 1 0.1960784 1</color></diffuse></lambert></technique></profile_COMMON></effect><effect id="ID23">\
        <profile_COMMON><technique sid="COMMON"><lambert><diffuse><color>1 0 0 1</color></diffuse></lambert></technique></profile_COMMON></effect><effect id="ID31">\
        <profile_COMMON><technique sid="COMMON"><lambert><diffuse><color>0.3960784 1 1 1</color></diffuse></lambert></technique></profile_COMMON></effect></library_effects>\
        <scene><instance_visual_scene url="#ID2" /></scene></COLLADA>'

    _roomGeometry = LibraryGeometries()
    _roomGeometry.loadGeometryFromString(_exampleXML)
    _roomGeometry.displayGeometry(solid=True)
