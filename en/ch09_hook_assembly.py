import cadquery as cq

# --- Dimensions (mm): same as in the hook code ---
back_thickness = 5
screw_low = 35
screw_spacing = 30

# --- Parts ---
# The hook is read from the STEP file saved earlier
hook = cq.importers.importStep("wall_hook_v2.step")

# Countersunk M4 x 20 screw: a half profile is drawn and revolved (no thread)
screw = (
    cq.Workplane("XY")
    .polyline([(0, 0), (4, 0), (2, -2), (2, -20), (0, -20)])
    .close().revolve()
)

# A block standing for the wall, with screw holes
wall = (
    cq.Workplane("XY")
    .box(120, 20, 140, centered=(True, False, False))
    .translate((0, -20, -30))
    .faces(">Y").workplane()
    .pushPoints([(0, screw_low), (0, screw_low + screw_spacing)])
    .hole(4, depth=18)
)

# --- Assembly: each part is added with a name, a location and a colour ---
grey = cq.Color(0.25, 0.25, 0.28)
blue = cq.Color(0.25, 0.45, 0.70)
beige = cq.Color(0.87, 0.82, 0.72)

assembly = (
    cq.Assembly(name="hook_assembly")
    .add(wall, name="wall", color=beige)
    .add(hook, name="hook", color=blue)
    .add(screw, name="screw_low", color=grey,
         loc=cq.Location((0, back_thickness, screw_low)))
    .add(screw, name="screw_high", color=grey,
         loc=cq.Location((0, back_thickness, screw_low + screw_spacing)))
)

# --- Interference check: do the screws enter the hook and the wall? ---
for z in (screw_low, screw_low + screw_spacing):
    in_place = screw.translate((0, back_thickness, z))
    for name, part in (("hook", hook), ("wall", wall)):
        common = part.intersect(in_place)
        volume = common.val().Volume() if common.solids().size() else 0.0
        print("screw z =", z, name, "overlap:", round(volume, 3))

assembly.export("hook_assembly.step")
