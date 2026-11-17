import cadquery as cq

# Code produced by the first two of three attempts at describing the same part.
# The third is ch11_cable_clip.py.

# --- Attempt 1: "Make a cable holder that clips onto a table." ---
# The prompt has no dimensions; table 20 mm and cable 6 mm were assumed.
p1 = [(-25, 0), (0, 0), (0, -20), (-25, -20), (-25, -22.5), (2.5, -22.5),
      (2.5, 12), (-8, 12), (-8, 9.5), (0, 9.5), (0, 2.5), (-25, 2.5)]
attempt1 = cq.Workplane("YZ").polyline(p1).close().extrude(7.5, both=True)

# --- Attempt 2: dimensions given; orientation, squeeze, allowance and
#     manufacturing information missing ---
# Table 25 mm, two 5 mm cables, width 20 mm, wall 3 mm.
p2 = [(-20, 0), (0, 0), (0, -25), (-20, -25), (-20, -28), (3, -28),
      (3, 12), (-9, 12), (-9, 3), (-20, 3)]
attempt2 = cq.Workplane("YZ").polyline(p2).close().extrude(10, both=True)
holes = (
    cq.Workplane("XZ").workplane(offset=-3)
    .pushPoints([(-5, 7.5), (5, 7.5)]).circle(2.5).extrude(12)
)
attempt2 = attempt2.cut(holes)

for name, p in (("attempt1", attempt1), ("attempt2", attempt2)):
    b = p.val().BoundingBox()
    print(name, round(b.xlen, 1), round(b.ylen, 1), round(b.zlen, 1),
          round(p.val().Volume()), len(p.solids().vals()), p.val().isValid())
