import cadquery as cq

block = (
    cq.Workplane("XY")
    .box(40, 30, 10)                      # 40 x 30 x 10 mm block
    .edges("|Z").fillet(3)                # 3 mm fillet on the four vertical edges
    .faces(">Z").workplane().hole(8)      # 8 mm hole from the top face
)

cq.exporters.export(block, "block.step")
