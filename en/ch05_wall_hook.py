import cadquery as cq

# --- Dimensions (mm) ---
width = 30             # width of the hook
back_height = 80       # height of the plate resting on the wall
back_thickness = 5
arm_length = 40        # length of the arm, from the wall into the room
arm_thickness = 8
tip_height = 18        # height of the tab at the end of the arm
tip_thickness = 6
screw_dia = 4.5
screw_low = 35         # height of the lower screw hole above the bottom
screw_spacing = 30     # distance between the two screw holes

# Axes: X to the right, Y from the wall into the room, Z up.
# The wall is the Y = 0 plane.

# --- Back plate: the upright slab against the wall ---
back = cq.Workplane("XY").box(
    width, back_thickness, back_height, centered=(True, False, False)
)

# --- Arm: extends from the bottom of the plate into the room ---
arm = (
    cq.Workplane("XY")
    .box(width, arm_length, arm_thickness, centered=(True, False, False))
    .translate((0, back_thickness, 0))
)

# --- Tip: the tab rising at the end of the arm ---
tip = (
    cq.Workplane("XY")
    .box(width, tip_thickness, tip_height, centered=(True, False, False))
    .translate((0, back_thickness + arm_length - tip_thickness, arm_thickness))
)

# --- Merge the three parts ---
hook = back.union(arm).union(tip)

# --- Screw holes: from the wall-facing side inwards ---
hook = (
    hook.faces("<Y").workplane()
    .pushPoints([(0, screw_low), (0, screw_low + screw_spacing)])
    .hole(screw_dia, depth=back_thickness)
)

cq.exporters.export(hook, "wall_hook.step")
cq.exporters.export(hook, "wall_hook.stl")
