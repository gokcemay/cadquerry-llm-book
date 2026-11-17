import cadquery as cq

# A small test piece for finding your printer's fit allowance:
# the same pin is tried in five slots of increasing looseness.

# --- Dimensions (mm) ---
pin_width = 5.0
allowances = [0.0, 0.1, 0.2, 0.3, 0.4]     # looseness of each slot relative to the pin
slot_pitch = 11
thickness = 6
slot_depth = 10

length = slot_pitch * len(allowances) + 6
width = slot_depth + 8

gauge = cq.Workplane("XY").box(length, width, thickness,
                               centered=(False, False, False))
for i, allowance in enumerate(allowances):
    x = 3 + slot_pitch * i + slot_pitch / 2
    slot = (
        cq.Workplane("XY")
        .box(pin_width + allowance, slot_depth, thickness, centered=(True, False, False))
        .translate((x, width - slot_depth, 0))
    )
    gauge = gauge.cut(slot)
    # Notches in front of the slot show the allowance: one notch per 0.1 mm
    for j in range(round(allowance * 10)):
        notch = (
            cq.Workplane("XY").box(1, 1.5, 0.6, centered=(True, False, False))
            .translate((x - 3 + 1.5 * j, 1, thickness - 0.6))
        )
        gauge = gauge.cut(notch)

pin = cq.Workplane("XY").box(pin_width, 25, thickness, centered=(True, False, False))

for name, p in (("gauge", gauge), ("pin", pin)):
    b = p.val().BoundingBox()
    print(name, round(b.xlen, 1), round(b.ylen, 1), round(b.zlen, 1),
          len(p.solids().vals()), p.val().isValid())

cq.exporters.export(gauge, "clearance_gauge.stl")
cq.exporters.export(pin, "clearance_pin.stl")
