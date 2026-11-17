import cadquery as cq
from cadquery.vis import show

# --- Dimensions (mm) ---
length = 60
width = 40
thickness = 5
hole_dia = 10

# --- Plate and hole ---
plate = (
    cq.Workplane("XY")
    .box(length, width, thickness)
    .faces(">Z").workplane()
    .hole(hole_dia)
)

# --- Write to file and display ---
cq.exporters.export(plate, "first_plate.stl")
cq.exporters.export(plate, "first_plate.step")
show(plate)
