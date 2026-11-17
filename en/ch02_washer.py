import cadquery as cq

# A washer: 40 mm outer diameter, 16 mm hole, 6 mm thick
washer = cq.Workplane("XY").circle(20).circle(8).extrude(6)

# The same solid, meshed at two different resolutions
cq.exporters.export(washer, "washer_coarse.stl",
                    tolerance=1.5, angularTolerance=0.6)
cq.exporters.export(washer, "washer_fine.stl",
                    tolerance=0.01, angularTolerance=0.1)
