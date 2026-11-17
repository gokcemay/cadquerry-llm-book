import cadquery as cq
from cadquery.vis import show

kup = cq.Workplane("XY").box(20, 20, 20)

show(kup)
