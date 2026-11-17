"""Bent sheet-metal L bracket family: 3D model, flat pattern and checks."""
import math

import cadquery as cq
import ezdxf
from cadquery.occ_impl.exporters.dxf import DxfDocument

# Axes: arm A lies along X (between Z = 0 and the thickness), arm B rises
# along Z (between X = 0 and the thickness). The width is centred on Y.
# A and B are arm lengths measured from the outer corner.

# Workshop rules. These are example values; enter your own workshop's.
RULES = dict(
    k_factor=0.40,          # position of the neutral axis: 0 inner face, 0.5 mid-thickness
    bend_hole_mult=2.0,     # hole edge to start of bend >= mult x thickness
    end_hole_mult=1.5,      # hole centre to arm end >= mult x diameter
    side_edge_mult=1.5,     # hole centre to side edge >= mult x diameter
    hole_pitch_mult=3.0,    # hole centre to hole centre >= mult x diameter
    density=7.85 / 1000,    # steel, g/mm3
)


def make_name(p):
    """Part name from the parameters: BRK-A60-B40-W30-T2-D5.5-2x1"""
    return (f"BRK-A{p['arm_a']:g}-B{p['arm_b']:g}-W{p['width']:g}"
            f"-T{p['thickness']:g}-D{p['hole_dia']:g}"
            f"-{p['holes_a']}x{p['holes_b']}")


def hole_positions(arm, count, p, rules=RULES):
    """Distances of the hole centres from the outer corner. ValueError if they do not fit."""
    t, r, d = p["thickness"], p["inner_radius"], p["hole_dia"]
    if count == 0:
        return []
    start = (r + t) + rules["bend_hole_mult"] * t + d / 2
    end = arm - rules["end_hole_mult"] * d
    if end < start:
        raise ValueError(
            f"A {d:g} mm hole does not fit on a {arm:g} mm arm "
            f"(usable range {start:.1f}-{end:.1f} mm)")
    if count == 1:
        return [(start + end) / 2]
    pitch = (end - start) / (count - 1)
    if pitch < rules["hole_pitch_mult"] * d:
        raise ValueError(
            f"{count} holes do not fit on a {arm:g} mm arm "
            f"(pitch {pitch:.1f} mm, "
            f"at least {rules['hole_pitch_mult'] * d:.1f})")
    return [start + i * pitch for i in range(count)]


def make_bracket(p, rules=RULES):
    """The 3D bracket and the computed dimensions."""
    A, B, W = p["arm_a"], p["arm_b"], p["width"]
    t, r, d = p["thickness"], p["inner_radius"], p["hole_dia"]
    if W / 2 < rules["side_edge_mult"] * d:
        raise ValueError(f"A width of {W:g} mm is too narrow for a {d:g} mm hole")
    xa = hole_positions(A, p["holes_a"], p, rules)
    zb = hole_positions(B, p["holes_b"], p, rules)

    ro = r + t      # outer radius
    bracket = (
        cq.Workplane("XZ")
        .moveTo(ro, 0).lineTo(A, 0).lineTo(A, t).lineTo(ro, t)
        .radiusArc((t, ro), r)           # inner bend arc
        .lineTo(t, B).lineTo(0, B).lineTo(0, ro)
        .radiusArc((ro, 0), -ro)         # outer bend arc
        .close()
        .extrude(W / 2, both=True)
    )
    if xa:
        bracket = bracket.cut(
            cq.Workplane("XY").pushPoints([(x, 0) for x in xa])
            .circle(d / 2).extrude(t))
    if zb:
        bracket = bracket.cut(
            cq.Workplane("YZ").pushPoints([(0, z) for z in zb])
            .circle(d / 2).extrude(t))
    return bracket, dict(holes_a=xa, holes_b=zb)


def flat_pattern(p, o, rules=RULES):
    """Flat-pattern dimensions. The u axis runs from the end of arm A to the end of arm B."""
    A, B = p["arm_a"], p["arm_b"]
    t, r = p["thickness"], p["inner_radius"]
    bend_allowance = math.pi / 2 * (r + rules["k_factor"] * t)
    flat_a, flat_b = A - r - t, B - r - t
    length = flat_a + bend_allowance + flat_b
    return dict(
        length=length, bend_allowance=bend_allowance,
        bend_line=flat_a + bend_allowance / 2,
        holes=[A - x for x in o["holes_a"]]
        + [length - (B - z) for z in o["holes_b"]],
    )


def flat_pattern_dxf(p, a, filename):
    """Writes the flat pattern as a two-layer DXF: CUT and BEND."""
    W, d = p["width"], p["hole_dia"]
    # Careful: center() moves the origin of the workplane and the DXF is
    # written relative to that origin. The rectangle is positioned with moveTo.
    cut = cq.Workplane("XY").moveTo(a["length"] / 2, 0).rect(a["length"], W)
    if a["holes"]:
        cut = cut.add(
            cq.Workplane("XY").pushPoints([(u, 0) for u in a["holes"]])
            .circle(d / 2))
    u = a["bend_line"]
    bend = cq.Workplane("XY").moveTo(u, -W / 2).lineTo(u, W / 2)
    dxf = DxfDocument()
    dxf.add_layer("CUT", color=7)
    dxf.add_layer("BEND", color=1)
    dxf.add_shape(cut, "CUT")
    dxf.add_shape(bend, "BEND")
    dxf.document.saveas(filename)


def cylinders(shape):
    """Cylindrical faces: (face, radius, axis direction)."""
    result = []
    for f in shape.Faces():
        if f.geomType() == "CYLINDER":
            c = f._geomAdaptor().Cylinder()
            e = c.Axis().Direction()
            result.append((f, c.Radius(), (e.X(), e.Y(), e.Z())))
    return result


def verify(p, bracket, o, a, dxf_file, rules=RULES):
    """Seven checks. Returns the volume (mm3) if they pass."""
    A, B, W = p["arm_a"], p["arm_b"], p["width"]
    t, r, d = p["thickness"], p["inner_radius"], p["hole_dia"]
    s = bracket.val()

    # 1. A single, valid solid
    assert bracket.solids().size() == 1 and s.isValid(), "Solid is invalid"

    # 2. Outer dimensions as in the table
    box = s.BoundingBox()
    for name, measured, wanted in (("A", box.xlen, A), ("W", box.ylen, W),
                                   ("B", box.zlen, B)):
        assert abs(measured - wanted) < 0.01, \
            f"{name}: {measured:.2f} != {wanted}"

    # 3. Hole count: axis along Z means arm A, axis along X means arm B
    cyl = cylinders(s)
    holes_a = [f for f, rr, e in cyl if abs(e[2]) > 0.99]
    holes_b = [f for f, rr, e in cyl if abs(e[0]) > 0.99]
    assert len(holes_a) == p["holes_a"], "Wrong hole count on arm A"
    assert len(holes_b) == p["holes_b"], "Wrong hole count on arm B"

    # 4. Every hole is far enough from the bend: face-to-face distance is measured
    inner_bend = [f for f, rr, e in cyl
                  if abs(e[1]) > 0.99 and abs(rr - r) < 0.01][0]
    minimum = rules["bend_hole_mult"] * t
    for f in holes_a + holes_b:
        m = f.distance(inner_bend)
        assert m >= minimum - 0.01, f"Hole is {m:.2f} mm from the bend (minimum {minimum})"

    # 5. Volume conservation: the 3D volume must equal that of a plate
    #    unfolded at mid-thickness (a check independent of the k-factor)
    mid_length = (A - r - t) + (B - r - t) + math.pi / 2 * (r + t / 2)
    hole_volume = (p["holes_a"] + p["holes_b"]) * math.pi * d * d / 4 * t
    expected = mid_length * W * t - hole_volume
    assert abs(s.Volume() - expected) / expected < 0.001, \
        f"Volume {s.Volume():.0f}, expected {expected:.0f}"

    # 6. The flat-pattern file is read back: layers and dimensions
    msp = ezdxf.readfile(dxf_file).modelspace()
    cut = [e for e in msp if e.dxf.layer == "CUT"]
    bend = [e for e in msp if e.dxf.layer == "BEND"]
    circles = [e for e in cut if e.dxftype() == "CIRCLE"]
    assert len(circles) == p["holes_a"] + p["holes_b"], "DXF hole count"
    assert len(bend) == 1, "The DXF must have exactly one bend line"
    assert abs(bend[0].dxf.start.x - a["bend_line"]) < 0.01, \
        "Bend line is in the wrong place in the DXF"
    back = cq.importers.importDXF(dxf_file, include=["CUT"])
    g = back.val().BoundingBox()
    assert abs(g.xmin) < 0.01, "The part does not start at the origin in the DXF"
    assert abs(g.xlen - a["length"]) < 0.01, "DXF flat-pattern length is wrong"
    assert abs(g.ylen - W) < 0.01, "DXF width is wrong"

    # 7. The distance from a hole to the arm end does not change in bending: distances
    #    measured on the 3D model must equal those read from the DXF
    to_end_3d = sorted([box.xmax - f.Center().x for f in holes_a]
                       + [g.xlen - (box.zmax - f.Center().z) for f in holes_b])
    to_end_dxf = sorted(e.dxf.center.x for e in circles)
    for u3, ud in zip(to_end_3d, to_end_dxf):
        assert abs(u3 - ud) < 0.01, \
            f"Hole has shifted in the flat pattern: 3D {u3:.2f}, DXF {ud:.2f}"
    return s.Volume()
