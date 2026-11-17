import cadquery as cq

# --- Dimensions (mm) ---
length = 100
width = 60
thickness = 5
corner_radius = 8     # radius of the corner rounding
hole_dia = 4.5        # diameter of the screw hole
hole_edge = 10        # distance from hole centre to the edge
chamfer = 1

plate = (
    cq.Workplane("XY")
    .rect(length, width)                     # sketch: a rectangle
    .extrude(thickness)                      # extrude: give the sketch thickness
    .edges("|Z").fillet(corner_radius)       # fillet: round the four vertical edges
    .faces(">Z").edges().chamfer(chamfer)    # chamfer: break the top edges
    .faces(">Z").workplane()                 # move to the top face
    .rect(length - 2 * hole_edge, width - 2 * hole_edge,
          forConstruction=True)              # construction rectangle
    .vertices().hole(hole_dia)               # holes: at its four corners
)

cq.exporters.export(plate, "mounting_plate.step")
cq.exporters.export(plate, "mounting_plate.stl")
