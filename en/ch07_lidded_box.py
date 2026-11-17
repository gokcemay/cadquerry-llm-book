import cadquery as cq

# --- Dimensions (mm) ---
length = 80
width = 50
height = 30
corner_radius = 6
wall = 2
lid_thickness = 3
lip_height = 3
clearance = 0.3        # allowance left on each side between lid lip and box interior
foot_dia = 8
foot_height = 1.5
foot_edge = 12         # distance from foot centre to the edge
text = "SCREWS"
text_size = 9
text_height = 0.6

# --- Box: solid block, rounded corners, hollowed out ---
box = (
    cq.Workplane("XY")
    .box(length, width, height, centered=(True, True, False))
    .edges("|Z").fillet(corner_radius)
    .faces(">Z").shell(-wall)
)

# --- Four feet on the bottom ---
box = (
    box.faces("<Z").workplane()
    .rarray(length - 2 * foot_edge, width - 2 * foot_edge, 2, 2)
    .circle(foot_dia / 2).extrude(foot_height)
)

# --- Lid: flat plate and a lip that fits inside the box ---
inner_length = length - 2 * wall - 2 * clearance
inner_width = width - 2 * wall - 2 * clearance
inner_radius = corner_radius - wall - clearance

lid = (
    cq.Workplane("XY")
    .box(length, width, lid_thickness, centered=(True, True, False))
    .edges("|Z").fillet(corner_radius)
)
lip = (
    cq.Workplane("XY")
    .box(inner_length, inner_width, lip_height, centered=(True, True, False))
    .edges("|Z").fillet(inner_radius)
    .translate((0, 0, -lip_height))
)
lid = lid.union(lip)

# --- Embossed text on top of the lid ---
lid = (
    lid.faces(">Z").workplane()
    .text(text, text_size, text_height, combine=True)
)

# --- Measure and save ---
for name, part in (("box", box), ("lid", lid)):
    b = part.val().BoundingBox()
    print(name, b.xlen, b.ylen, b.zlen, part.val().Volume(),
          len(part.solids().vals()), part.val().isValid())

cq.exporters.export(box, "box.step")
cq.exporters.export(box, "box.stl")
cq.exporters.export(lid, "lid.step")
cq.exporters.export(lid, "lid.stl")
