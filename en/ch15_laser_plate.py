import cadquery as cq

# Produces a laser-cutting drawing (DXF) from the mounting plate of Chapter 2.

# --- Inputs (mm) ---
length = 100
width = 60
thickness = 5
corner_radius = 8
hole_dia = 4.5
hole_edge = 10
chamfer = 1
kerf = 0.2      # ask the workshop, or measure with a test cut

# --- Plate (the code from Chapter 2) ---
plate = (
    cq.Workplane("XY").rect(length, width).extrude(thickness)
    .edges("|Z").fillet(corner_radius)
    .faces(">Z").edges().chamfer(chamfer)
    .faces(">Z").workplane()
    .rect(length - 2 * hole_edge, width - 2 * hole_edge,
          forConstruction=True)
    .vertices().hole(hole_dia)
)

# --- Section: at mid-thickness of the plate ---
# section() measures the height from the current workplane. On this plate
# that plane is the chamfered top face, so we step down by half the thickness.
cross = plate.section(-thickness / 2).faces().val()


def offset(outline, amount):
    """Grows (amount > 0) or shrinks (amount < 0) a closed outline.

    The sign of offset2D depends on the winding direction of the outline.
    This tries both directions, measures the enclosed area and picks the
    one that was asked for.
    """
    candidates = [outline.offset2D(m)[0] for m in (amount, -amount)]
    candidates.sort(key=lambda c: cq.Face.makeFromWires(c).Area())
    return candidates[1] if amount > 0 else candidates[0]


# The laser removes half the kerf on either side of the line:
# the outer outline is grown by that much, the holes are shrunk.
outer = offset(cross.outerWire(), kerf / 2)
holes = [offset(h, -kerf / 2) for h in cross.innerWires()]
drawing = cq.Workplane("XY").add([outer] + holes)

# --- Check ---
b = outer.BoundingBox()
assert abs(b.xlen - (length + kerf)) < 0.01, "Outer outline is wrong"
assert abs(b.ylen - (width + kerf)) < 0.01, "Outer outline is wrong"
assert len(holes) == 4, "Wrong number of holes"
for h in holes:
    dia = h.BoundingBox().xlen
    assert abs(dia - (hole_dia - kerf)) < 0.01, "Wrong hole diameter"
print("drawing:", round(b.xlen, 2), "x", round(b.ylen, 2),
      "| hole dia:", round(holes[0].BoundingBox().xlen, 2))

cq.exporters.exportDXF(drawing, "mounting_plate_laser.dxf")

# --- Read the file back ---
back = cq.importers.importDXF("mounting_plate_laser.dxf")
g = back.val().BoundingBox()
print("DXF:", round(g.xlen, 2), "x", round(g.ylen, 2),
      "| closed outlines:", back.wires().size())
