import cadquery as cq

# Three reasonable readings of the same ambiguous prompt:
# "Make an angle bracket-style connector with two holes."


def angle_bracket(horizontal, vertical, width, wall):
    """L-shaped bracket: horizontal arm along X, vertical arm along Z."""
    base = cq.Workplane("XY").box(horizontal, width, wall, centered=(False, True, False))
    upright = cq.Workplane("XY").box(wall, width, vertical, centered=(False, True, False))
    return base.union(upright)


# Reading A: equal arms, one hole in each arm
a = angle_bracket(40, 40, 20, 3)
a = a.faces("<Z").workplane().pushPoints([(23, 0)]).hole(4.5, depth=3)
a = a.faces("<X").workplane().pushPoints([(0, 23)]).hole(4.5, depth=3)

# Reading B: equal arms, both holes in the vertical arm
b = angle_bracket(40, 40, 20, 3)
b = b.faces("<X").workplane().pushPoints([(0, 15), (0, 30)]).hole(4.5, depth=3)

# Reading C: bigger and thicker, filleted inner corner, both holes in the horizontal arm
c = angle_bracket(60, 30, 25, 5)
c = c.edges(cq.selectors.BoxSelector((4, -20, 4), (6, 20, 6))).fillet(6)
c = c.faces("<Z").workplane().pushPoints([(25, 0), (48, 0)]).hole(5.5, depth=5)

for name, p in (("A", a), ("B", b), ("C", c)):
    box = p.val().BoundingBox()
    print(name, box.xlen, box.ylen, box.zlen, round(p.val().Volume()),
          len(p.solids().vals()), p.val().isValid())
