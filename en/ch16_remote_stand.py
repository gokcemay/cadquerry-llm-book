import math
import sys

import cadquery as cq

sys.path.insert(0, "tools")
import print_orientation  # noqa: E402  (the support tool from Chapter 15)

# Axes: X along the width of the stand, Y front to back, Z up.
# The underside of the stand is Z = 0; the front face looks towards -Y.

# --- Inputs: remote controls (mm, grams) ---
# Width and thickness: the largest value over the lowest 45 mm of the remote.
remotes = [
    # (label, width, thickness, length, mass)
    ("TV", 45, 20, 180, 95),
    ("SAT", 52, 24, 210, 130),
    ("AC", 58, 18, 140, 80),
]

PLA_DENSITY = 1.24 / 1000    # g/mm3


def make_stand(remotes, allowance=1.0, wall=2.4, base=3, pocket_depth=45,
               plate_depth=70, text_size=7):
    """Remote-control stand. With plate_depth=0 there is no base plate."""
    pockets = [(w + allowance, t + allowance) for _, w, t, _, _ in remotes]
    body_width = sum(c[0] for c in pockets) + (len(pockets) + 1) * wall
    body_depth = max(c[1] for c in pockets) + 2 * wall
    height = base + pocket_depth

    # Body: a rectangular block on the bed, vertical edges rounded
    stand = (
        cq.Workplane("XY").rect(body_width, body_depth).extrude(height)
        .edges("|Z").fillet(3)
    )

    # Base plate: a slab extending front and back to resist tipping
    if plate_depth > body_depth:
        plate = (
            cq.Workplane("XY").rect(body_width, plate_depth).extrude(base)
            .edges("|Z").fillet(3)
        )
        stand = stand.union(plate)

    # Edges on the bed: chamfer, not fillet (1 closed outline)
    stand = stand.faces("<Z").edges().chamfer(0.6)

    # Pockets: from the top down, arranged left to right
    x = -body_width / 2 + wall
    centres = []
    for pocket_w, pocket_t in pockets:
        centre = x + pocket_w / 2
        pocket = (
            cq.Workplane("XY").workplane(offset=base)
            .center(centre, 0).rect(pocket_w, pocket_t).extrude(pocket_depth)
        )
        stand = stand.cut(pocket)
        centres.append(centre)
        x += pocket_w + wall

    # Embossed labels: on the front part of the plate, on the upward-facing side
    front_margin = (plate_depth - body_depth) / 2
    if text_size > 0 and front_margin >= text_size + 4:
        label_y = -(body_depth / 2 + front_margin / 2)
        for (label, *_), centre in zip(remotes, centres):
            text = (
                cq.Workplane("XY").workplane(offset=base)
                .center(centre, label_y)
                .text(label, text_size, 0.8, combine=False)
            )
            stand = stand.union(text)

    dims = dict(body_width=body_width, body_depth=body_depth,
                height=height, centres=centres, pockets=pockets,
                base=base, wall=wall, allowance=allowance,
                base_depth=max(plate_depth, body_depth))
    return stand, dims


def remote_model(remote, centre, base):
    """A block standing in for the remote: rests on the bottom of the pocket."""
    _, w, t, length, _ = remote
    return (
        cq.Workplane("XY").workplane(offset=base)
        .center(centre, 0).rect(w, t).extrude(length)
    )


def tipping_angle(stand, d, remotes, fill=0.5):
    """By how many degrees can the stand be tilted forward or back before it tips?

    The inside of the stand counts as half full (fill=0.5): a light stand is the bad case.
    """
    mass = stand.val().Volume() * PLA_DENSITY * fill
    moment = mass * cq.Shape.centerOfMass(stand.val()).z
    for _, _, _, length, m in remotes:
        mass += m
        moment += m * (d["base"] + length / 2)
    centre_of_mass_z = moment / mass
    return math.degrees(math.atan(d["base_depth"] / 2 / centre_of_mass_z))


def verify(remotes, min_angle=20, **settings):
    stand, d = make_stand(remotes, **settings)
    s = stand.val()

    # 1. A single, valid solid
    assert stand.solids().size() == 1, "Stand is not a single piece"
    assert s.isValid(), "Solid is not valid"

    # 2. Each remote enters its pocket without overlap; allowance/2 is left on each side
    for remote, centre, pocket in zip(remotes, d["centres"], d["pockets"]):
        model = remote_model(remote, centre, d["base"])
        common = stand.intersect(model)
        volume = common.val().Volume() if common.solids().size() else 0.0
        assert volume < 0.01, f"{remote[0]} overlaps the stand: {volume:.1f} mm3"
        assert abs(pocket[0] - remote[1] - d["allowance"]) < 0.01, "Pocket width is wrong"

    # 3. Outer size: height must not exceed half of the shortest remote
    b = s.BoundingBox()
    shortest = min(length for _, _, _, length, _ in remotes)
    assert b.zlen <= shortest / 2, "Stand covers the buttons of the shortest remote"

    # 4. Printing: no support needed in the designed orientation
    _, _, support = print_orientation.orientation_report(s)
    assert support < 1, f"Area needing support: {support:.0f} mm2"

    # 5. Tipping: the stand must tolerate at least this much tilt
    angle = tipping_angle(stand, d, remotes)
    assert angle >= min_angle, f"Tips easily: tipping angle {angle:.1f} degrees"

    mass = s.Volume() * PLA_DENSITY
    print(f"5 checks passed | {b.xlen:.1f} x {b.ylen:.1f} x {b.zlen:.1f} mm |",
          f"at most {mass:.0f} g | tipping angle {angle:.1f} degrees")
    return stand, d


if __name__ == "__main__":
    stand, d = verify(remotes)
    cq.exporters.export(stand, "remote_stand.step")
    cq.exporters.export(stand, "remote_stand.stl",
                        tolerance=0.05, angularTolerance=0.2)
