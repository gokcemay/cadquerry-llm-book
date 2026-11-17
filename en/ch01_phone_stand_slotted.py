import math
import cadquery as cq

# --- Dimensions (mm) ---
width = 70               # width of the stand
base_depth = 80          # front-to-back length of the base
wall = 4                 # wall thickness
angle = 65               # angle between the phone and the horizontal (deg)
back_length = 90         # length of the backrest
phone_thickness = 9      # thickness of the phone
lip_height = 12          # height of the front lip above the base
clearance = 1.5          # allowance so the phone sits comfortably
back_x = 30              # where the backrest meets the base (from the front)

# --- Base: a flat slab ---
base = cq.Workplane("XY").box(
    base_depth, width, wall, centered=(False, True, False)
)

# --- Backrest: an upright slab, tilted backwards ---
back = (
    cq.Workplane("XY")
    .box(wall, width, back_length, centered=(False, True, False))
    .rotate((0, 0, 0), (0, 1, 0), 90 - angle)
    .translate((back_x, 0, wall))
)

# --- Lip: a small wall that stops the phone sliding forward ---
slot = (phone_thickness + clearance) / math.sin(math.radians(angle))
lip_x = back_x - slot - wall
lip = (
    cq.Workplane("XY")
    .box(wall, width, wall + lip_height, centered=(False, True, False))
    .translate((lip_x, 0, 0))
)

# --- Merge the three parts into one solid ---
stand = base.union(back).union(lip)

# --- Notch in the lip for the charging cable ---
notch_width = 14
notch = (
    cq.Workplane("XY")
    .box(wall + 2, notch_width, lip_height + 1, centered=(False, True, False))
    .translate((lip_x - 1, 0, wall))
)
stand = stand.cut(notch)

# --- Write to file ---
cq.exporters.export(stand, "phone_stand.stl")
cq.exporters.export(stand, "phone_stand.step")
