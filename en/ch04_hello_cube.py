import cadquery as cq
from cadquery.vis import show

cube = cq.Workplane("XY").box(20, 20, 20)

show(cube)
