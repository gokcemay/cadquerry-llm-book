import cadquery as cq

# Axes: X along the width of the hanger, Y under the table from the edge
# inwards, Z up. The underside of the table is Z = 0; the hanger sits
# below this face.

# --- Inputs (mm) ---
band_width = 30        # opening where the headphone band rests

# --- Constants ---
span = 25
wall = 5
plate_length = 60
arm_length = 45        # from the underside of the plate to the top of the carrier
tab = 8                # height of the tab above the carrier
screw_dia = 4.5
csk_dia = 9
driver_dia = 8

# --- Derived dimensions ---
carrier_length = wall + band_width + wall
z_plate = -wall                    # underside of the plate
z_top = -wall - arm_length         # top face of the carrier
z_bottom = z_top - wall            # bottom face of the carrier
screw_y = [15, 45]                  # Y positions of the screw holes

# --- Body: side-view profile, extruded across the span ---
profile = [
    (0, 0), (plate_length, 0), (plate_length, z_plate), (wall, z_plate),
    (wall, z_top), (carrier_length - wall, z_top),
    (carrier_length - wall, z_top + tab), (carrier_length, z_top + tab),
    (carrier_length, z_bottom), (0, z_bottom),
]
hanger = cq.Workplane("YZ").polyline(profile).close().extrude(span / 2, both=True)

# --- Countersunk screw holes: from the underside of the plate upwards (2 holes) ---
# The uppermost of the downward-facing faces is the underside of the plate.
# On this face the local Y axis points the other way; positions get a minus sign.
hanger = (
    hanger.faces("-Z").faces(">Z").workplane()
    .pushPoints([(0, -y) for y in screw_y])
    .cskHole(screw_dia, csk_dia, 90)
)

# --- Measure ---
b = hanger.val().BoundingBox()
print("outer size:", b.xlen, b.ylen, b.zlen)
print("volume:", round(hanger.val().Volume()))
print("solids:", len(hanger.solids().vals()), "valid:", hanger.val().isValid())
print("cone faces:", hanger.faces("%CONE").size())

# Screwdriver access: a 100 mm empty cylinder must fit under each screw
for y in screw_y:
    driver = (
        cq.Workplane("XY").circle(driver_dia / 2).extrude(-100)
        .translate((0, y, z_plate))
    )
    common = hanger.intersect(driver)
    volume = common.val().Volume() if common.solids().size() else 0.0
    print("  screw y =", y, "screwdriver overlap:", round(volume, 1))

cq.exporters.export(hanger, "headphone_hanger.step")
cq.exporters.export(hanger, "headphone_hanger.stl",
                    tolerance=0.05, angularTolerance=0.2)
