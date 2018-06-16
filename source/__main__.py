import matplotlib.pyplot as plot
from geometry import *
from ray_tracing import *
from logger import *

# ROOM_GEOMETRY_FILENAME = 'house.dae'
# ROOM_GEOMETRY_FILENAME = 'house.dae'
# ROOM_GEOMETRY_FILENAME = 'very+simple+house.dae'
# ROOM_GEOMETRY_FILENAME = 'Simple_House.dae'
# ROOM_GEOMETRY_FILENAME = 'Simple+house.dae'
# ROOM_GEOMETRY_FILENAME = 'design.dae'
# ROOM_GEOMETRY_FILENAME = 'boxy_box.dae'
# ROOM_GEOMETRY_FILENAME = 'another_test.dae'
ROOM_GEOMETRY_FILENAME = 'examples/boxy_box_materials_colors.dae'

if __name__ == "__main__":

    _log = Logger()
    _log.start()

    _roomGeometry = LibraryGeometries()
    _roomGeometry.loadGeometryFromFile(ROOM_GEOMETRY_FILENAME)
    # _roomGeometry.displayGeometry(solid=False)

    # _log.close()
    # quit()

    _tracer = RayTracer()
    _tracer.addEnvironmentGeometry(_roomGeometry)

    _source = SourceDefinition()
    _source._location = [1.0, 1.0, 1.0]
    _tracer.addSource(_source)

    _source2 = SourceDefinition()
    _source2._location = [0.5, 0.5, 0.5]
    _tracer.addSource(_source2)

    _receiver = ReceiverDefinition()
    _receiver._location = [3.0, 3.0, 1.0]
    _tracer.addReceiver(_receiver)

    _receiver2 = ReceiverDefinition()
    _receiver2._location = [4.0, 4.0, 1.2]
    _tracer.addReceiver(_receiver2)

    _tracer.executeTracing()
    _log.stop()











