import cadquery as cq

# --- Dimensions (mm) ---
width = 30
back_height = 80
back_thickness = 5
arm_length = 40
arm_thickness = 8
tip_height = 18
tip_thickness = 6
screw_dia = 4.5
screw_low = 35
screw_spacing = 30
inner_fillet_back = 6   # inner corner between the arm and the back plate
inner_fillet_tip = 4    # inner corner between the arm and the tip
outer_fillet = 2        # outer vertical edges of the tip
csk_dia = 9             # conical countersink diameter for the screw head
csk_angle = 90

# Axes: X to the right, Y from the wall into the room. The wall is Y = 0.

# --- Back plate; the room-facing face is tagged before the arm is added ---
back = (
    cq.Workplane("XY")
    .box(width, back_thickness, back_height, centered=(True, False, False))
    .faces(">Y").workplane().tag("front_face")
)

arm = (
    cq.Workplane("XY")
    .box(width, arm_length, arm_thickness, centered=(True, False, False))
    .translate((0, back_thickness, 0))
)

tip = (
    cq.Workplane("XY")
    .box(width, tip_thickness, tip_height, centered=(True, False, False))
    .translate((0, back_thickness + arm_length - tip_thickness, arm_thickness))
)

hook = back.union(arm).union(tip)

# --- Inner corner 1: where the arm meets the back plate (1 edge) ---
corner_back = cq.selectors.BoxSelector(
    (-width, back_thickness - 1, arm_thickness - 1),
    (width, back_thickness + 1, arm_thickness + 1),
)
hook = hook.edges(corner_back).fillet(inner_fillet_back)

# --- Inner corner 2: where the arm meets the tip (1 edge) ---
tip_inner_y = back_thickness + arm_length - tip_thickness
corner_tip = cq.selectors.BoxSelector(
    (-width, tip_inner_y - 1, arm_thickness - 1),
    (width, tip_inner_y + 1, arm_thickness + 1),
)
hook = hook.edges(corner_tip).fillet(inner_fillet_tip)

# --- Outer vertical edges of the tip (2 edges) ---
hook = hook.edges("|Z and >Y").fillet(outer_fillet)

# --- Countersunk screw holes: from the room-facing side towards the wall ---
hook = (
    hook.workplaneFromTagged("front_face")
    .pushPoints([(0, screw_low), (0, screw_low + screw_spacing)])
    .cskHole(screw_dia, csk_dia, csk_angle)
)

# --- Measure and save ---
box = hook.val().BoundingBox()
print(box.xlen, box.ylen, box.zlen)
print(hook.val().Volume())
print(len(hook.solids().vals()))

cq.exporters.export(hook, "wall_hook_v2.step")
cq.exporters.export(hook, "wall_hook_v2.stl")
