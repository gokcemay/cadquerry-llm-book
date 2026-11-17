import math
import cadquery as cq


def make_stand(device_width, device_height, device_thickness, angle=65):
    """Builds a desktop stand from the dimensions of the device."""

    # --- Constants: manufacturing and usage rules ---
    wall = 4                # wall thickness
    clearance = 1.5         # so the device slides into the slot easily
    front_margin = 10       # base left in front of the lip
    rear_margin = 15        # base left behind the backrest

    # --- Derived dimensions ---
    width = round(0.9 * device_width)           # a bit narrower than the device
    back_length = round(0.6 * device_height)    # backrest: 60 % of the device
    lip_height = max(10, device_thickness + 3)
    slot = (device_thickness + clearance) / math.sin(math.radians(angle))
    lip_x = front_margin
    back_x = lip_x + wall + slot
    back_projection = back_length * math.cos(math.radians(angle))
    base_depth = back_x + back_projection + rear_margin

    base = cq.Workplane("XY").box(
        base_depth, width, wall, centered=(False, True, False)
    )
    back = (
        cq.Workplane("XY")
        .box(wall, width, back_length, centered=(False, True, False))
        .rotate((0, 0, 0), (0, 1, 0), 90 - angle)
        .translate((back_x, 0, wall))
    )
    lip = (
        cq.Workplane("XY")
        .box(wall, width, wall + lip_height, centered=(False, True, False))
        .translate((lip_x, 0, 0))
    )
    return base.union(back).union(lip)


phone_stand = make_stand(75, 160, 9)
tablet_stand = make_stand(180, 250, 8, angle=70)

for name, stand in (("phone", phone_stand), ("tablet", tablet_stand)):
    b = stand.val().BoundingBox()
    print(name, round(b.xlen, 1), round(b.ylen, 1), round(b.zlen, 1),
          len(stand.solids().vals()), stand.val().isValid())
    cq.exporters.export(stand, f"stand_{name}.step")
