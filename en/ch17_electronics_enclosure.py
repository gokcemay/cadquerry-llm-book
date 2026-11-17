import sys

import cadquery as cq

sys.path.insert(0, "tools")
import print_orientation  # noqa: E402  (the support tool from Chapter 15)

# The axes are the board's axes: the lower-left corner of the board is X = 0, Y = 0.
# X runs along the board's length, Y along its width; Z is up. The bottom of the box is Z = 0.

# --- Input: the board's dimension drawing (mm) ---
# Connector: edge says which board edge it is on; position is the centre
# along that edge (X or Y); width and height are the visible size of the
# body from outside; bottom is the height of the body above the board's top face.
SENSOR_BOARD = dict(
    name="sensor_board",
    length=80, width=50, thickness=1.6,
    holes=[(4, 4), (76, 4), (4, 46), (76, 46)], hole_dia=3.2,
    under_clearance=5,     # longest leg under the board, solder
    top_height=15,         # tallest component on top of the board
    connectors=[
        dict(name="USB", edge="-X", position=15, width=9, height=3.5, bottom=0),
        dict(name="power", edge="-X", position=36, width=9, height=11, bottom=0),
        dict(name="terminal", edge="+Y", position=55, width=21, height=10,
             bottom=0),
    ],
)

RELAY_BOARD = dict(
    name="relay_board",
    length=62, width=38, thickness=1.6,
    holes=[(3.5, 3.5), (58.5, 3.5), (3.5, 34.5), (58.5, 34.5)],
    hole_dia=3.2,
    under_clearance=4,
    top_height=19,
    connectors=[
        dict(name="terminal", edge="+X", position=19, width=16, height=10,
             bottom=0),
        dict(name="pin", edge="-X", position=19, width=11, height=9, bottom=0),
    ],
)


def block(x0, x1, y0, y1, z0, z1):
    """A rectangular block with the given corners."""
    return (
        cq.Workplane("XY")
        .box(x1 - x0, y1 - y0, z1 - z0, centered=False)
        .translate((x0, y0, z0))
    )


def connector_block(board, k, z_board_top, margin=0.0, outside=0.0, inside=8.0):
    """A block standing in for a connector.

    margin: growth on every side. outside: extension beyond the board edge.
    """
    z0 = z_board_top + k["bottom"] - margin
    z1 = z_board_top + k["bottom"] + k["height"] + margin
    a, b = k["position"] - k["width"] / 2 - margin, k["position"] + k["width"] / 2 + margin
    L, W = board["length"], board["width"]
    if k["edge"] == "-X":
        return block(-outside, inside, a, b, z0, z1)
    if k["edge"] == "+X":
        return block(L - inside, L + outside, a, b, z0, z1)
    if k["edge"] == "-Y":
        return block(a, b, -outside, inside, z0, z1)
    if k["edge"] == "+Y":
        return block(a, b, W - inside, W + outside, z0, z1)
    raise ValueError(f"Unknown edge: {k['edge']}")


def make_enclosure(board, wall=2.0, base_thickness=2.0, lid_thickness=2.0,
                   board_allowance=0.5, window_allowance=0.5, fit_allowance=0.2,
                   lip=4.0, lip_wall=1.6, tower_dia=7.0, screw_hole=2.5,
                   top_gap=1.0, notch_width=12.0):
    """Builds an enclosure from a board: (base, lid, dimensions)."""
    L, W = board["length"], board["width"]
    z_board_bottom = base_thickness + board["under_clearance"]
    z_board_top = z_board_bottom + board["thickness"]
    z_top = z_board_top + board["top_height"] + top_gap   # top of the walls
    inner = (-board_allowance, L + board_allowance, -board_allowance, W + board_allowance)
    outer = (inner[0] - wall, inner[1] + wall, inner[2] - wall, inner[3] + wall)

    # Windows must stay below the lip; otherwise the lid lands on a connector
    for k in board["connectors"]:
        top = z_board_top + k["bottom"] + k["height"] + window_allowance
        if top > z_top - lip:
            raise ValueError(f"The {k['name']} window touches the lid lip")

    # --- Base: outer block, inner cavity ---
    base = (
        block(outer[0], outer[1], outer[2], outer[3], 0, z_top)
        .edges("|Z").fillet(3)
        .faces("<Z").edges().chamfer(0.6)
    )
    cavity = block(inner[0], inner[1], inner[2], inner[3], base_thickness, z_top)
    base = base.cut(cavity)

    # --- Screw towers: under each mounting hole ---
    towers = (
        cq.Workplane("XY").workplane(offset=base_thickness)
        .pushPoints(board["holes"]).circle(tower_dia / 2)
        .extrude(board["under_clearance"])
    )
    holes = (
        cq.Workplane("XY").workplane(offset=base_thickness)
        .pushPoints(board["holes"]).circle(screw_hole / 2)
        .extrude(board["under_clearance"])
    )
    base = base.union(towers).cut(holes)

    # --- Connector windows: cut through the wall ---
    for k in board["connectors"]:
        window = connector_block(board, k, z_board_top, margin=window_allowance,
                                 outside=board_allowance + wall + 1, inside=1)
        base = base.cut(window)

    # --- Thumb notch: in the top edge of the front wall, for opening the lid ---
    notch = block(L / 2 - notch_width / 2, L / 2 + notch_width / 2,
                  outer[2] - 1, inner[2], z_top - 1.5, z_top)
    base = base.cut(notch)

    # --- Lid: plate + a lip that goes inside the walls ---
    lid = (
        block(outer[0], outer[1], outer[2], outer[3], z_top, z_top + lid_thickness)
        .edges("|Z").fillet(3)
        .faces(">Z").edges().chamfer(0.6)
    )
    g = fit_allowance
    lip_outer = block(inner[0] + g, inner[1] - g, inner[2] + g, inner[3] - g,
                      z_top - lip, z_top)
    d = g + lip_wall
    lip_inner = block(inner[0] + d, inner[1] - d, inner[2] + d, inner[3] - d,
                      z_top - lip, z_top)
    lid = lid.union(lip_outer.cut(lip_inner))

    # --- Ventilation: slots in the lid, above the board ---
    slot_length = W * 0.5
    count = max(int((L * 0.6) // 5), 1)
    slots = (
        cq.Workplane("XY").workplane(offset=z_top)
        .center(L / 2, W / 2).rarray(5, 1, count, 1)
        .rect(2, slot_length).extrude(lid_thickness)
    )
    lid = lid.cut(slots)

    d = dict(z_board_bottom=z_board_bottom, z_board_top=z_board_top, z_top=z_top,
             wall=wall, board_allowance=board_allowance, window_allowance=window_allowance,
             fit_allowance=fit_allowance, screw_hole=screw_hole, slots=count,
             front_outer=outer[2], front_inner=inner[2])
    return base, lid, d


def board_model(board, d, outside=5.0):
    """A model standing in for the board: plate, component volume, connectors.

    Connectors are extended beyond the board edge; if a window is in the
    wrong place the extension hits the wall.
    """
    L, W = board["length"], board["width"]
    model = block(0, L, 0, W, d["z_board_bottom"], d["z_board_top"])
    # Volume that components may occupy: 2 mm in from the edges
    model = model.union(block(
        2, L - 2, 2, W - 2,
        d["z_board_top"], d["z_board_top"] + board["top_height"]))
    for k in board["connectors"]:
        model = model.union(
            connector_block(board, k, d["z_board_top"], outside=outside))
    # Mounting holes
    hole = (
        cq.Workplane("XY").pushPoints(board["holes"])
        .circle(board["hole_dia"] / 2).extrude(d["z_top"] + 5)
    )
    return model.cut(hole)


def common_volume(a, b):
    common = a.intersect(b)
    return common.val().Volume() if common.solids().size() else 0.0


def verify(board, **settings):
    base, lid, d = make_enclosure(board, **settings)
    model = board_model(board, d)

    # 1. Both parts are a single, valid solid
    for name, p in (("base", base), ("lid", lid)):
        assert p.solids().size() == 1, f"{name} is not a single piece"
        assert p.val().isValid(), f"{name} is not valid"

    # 2. The board, with its connector extensions, sits in the base without a collision
    v = common_volume(base, model)
    assert v < 0.01, f"Board overlaps the base: {v:.1f} mm3"

    # 3. The board rests on the towers: pushed 0.1 mm down, it touches each tower
    for x, y in board["holes"]:
        tower_top = block(x - 4, x + 4, y - 4, y + 4,
                          d["z_board_bottom"] - 0.1, d["z_board_bottom"])
        assert common_volume(base, tower_top) > 1, \
            f"No tower under ({x}, {y})"

    # 4. Screws: a 2.4 mm pin going down through each hole hits nothing
    for x, y in board["holes"]:
        pin = (
            cq.Workplane("XY").workplane(offset=d["z_board_bottom"] - 4)
            .center(x, y).circle(1.2).extrude(4 + board["thickness"])
        )
        v = common_volume(base, pin) + common_volume(model, pin)
        assert v < 0.01, f"Obstruction in the way of the screw at ({x}, {y}): {v:.2f} mm3"

    # 5. The lid closes: it hits neither the base nor the board
    assert common_volume(base, lid) < 0.01, "Lid overlaps the base"
    assert common_volume(model, lid) < 0.01, "Lid touches the board"

    # 6. Fit allowance: pushed sideways by less than the allowance there is no
    #    collision; pushed by more there is
    g = d["fit_allowance"]
    assert common_volume(base, lid.translate((g - 0.05, 0, 0))) < 0.01, \
        "Fit allowance is tighter than expected"
    assert common_volume(base, lid.translate((g + 0.05, 0, 0))) > 0.01, \
        "Fit allowance is looser than expected"

    # 7. Printing: the only bridges in the base are the tops of the windows;
    #    the lid prints upside down without support
    bridge = sum((k["width"] + 2 * d["window_allowance"]) * d["wall"]
                 for k in board["connectors"])
    _, _, support = print_orientation.orientation_report(base.val())
    assert abs(support - bridge) < 1, \
        f"Unexpected support in the base: {support:.0f} mm2 (bridge {bridge:.0f})"
    flipped = print_orientation.rotate(lid.val(), "-Z up (upside down)")
    _, _, support = print_orientation.orientation_report(flipped)
    assert support < 1, f"Lid needs support: {support:.0f} mm2"

    # 8. The lid can be opened: a flat blade entering through the notch hits
    #    nothing in the base and reaches under the lid plate
    L = board["length"]
    blade = block(L / 2 - 4, L / 2 + 4, d["front_outer"] - 5, d["front_inner"],
                  d["z_top"] - 1.2, d["z_top"] - 0.2)
    assert common_volume(base, blade) < 0.01, \
        "Notch is closed: the blade hits the base"
    above = block(L / 2 - 4, L / 2 + 4, d["front_outer"], d["front_inner"],
                  d["z_top"], d["z_top"] + 0.5)
    assert common_volume(lid, above) > 1, "No lid above the notch"

    t, k = base.val().BoundingBox(), lid.val().BoundingBox()
    longest = max(kn["width"] + 2 * d["window_allowance"]
                  for kn in board["connectors"])
    print(f"{board['name']}: 8 checks passed | outer size "
          f"{t.xlen:.1f} x {t.ylen:.1f} x {k.zmax:.1f} mm | "
          f"longest bridge {longest:.0f} mm | {d['slots']} slots")
    return base, lid, d


if __name__ == "__main__":
    for board in (SENSOR_BOARD, RELAY_BOARD):
        base, lid, d = verify(board)
        cq.exporters.export(base, f"{board['name']}_base.step")
        cq.exporters.export(lid, f"{board['name']}_lid.step")
