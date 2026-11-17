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

# --- Countersunk screw holes ---
# On the bottom face the local Y axis points the other way; positions get a minus sign
hanger = (
    hanger.faces("<Z").workplane()
    .pushPoints([(0, -y) for y in screw_y])
    .cskHole(screw_dia, csk_dia, 90)
)

# --- Measure ---
b = hanger.val().BoundingBox()
print("outer size:", b.xlen, b.ylen, b.zlen)
print("volume:", round(hanger.val().Volume()))
print("solids:", len(hanger.solids().vals()), "valid:", hanger.val().isValid())
print("cone faces:", hanger.faces("%CONE").size(),
      "cylinder faces:", hanger.faces("%CYLINDER").size())
for face in hanger.faces("%CYLINDER").vals():
    c = face.Center()
    print("  hole centre:", round(c.x, 1), round(c.y, 1), round(c.z, 1))
