import cadquery as cq


def make_box(length, width, height, text="",
             wall=2, corner_radius=6, clearance=0.3, foot_dia=8):
    """Builds a lidded box; returns (box, lid)."""

    # --- Are the dimensions consistent with each other? ---
    if corner_radius <= wall + clearance:
        raise ValueError(
            "Corner radius must exceed wall thickness plus clearance.")
    if min(length, width) <= 2 * corner_radius:
        raise ValueError(
            "The box's short side must exceed twice the corner radius.")
    if height <= 2 * wall:
        raise ValueError(
            "The box must be taller than twice the wall thickness.")
    if min(length, width) < 2 * corner_radius + 2 * foot_dia + 2:
        raise ValueError(
            "The box is too narrow to fit four feet side by side.")

    # --- Details kept fixed ---
    lid_thickness = 3
    lip_height = 3
    foot_height = 1.5

    # --- Dimensions derived from the inputs ---
    foot_edge = corner_radius + foot_dia / 2   # foot centre to the edge
    inner_length = length - 2 * wall - 2 * clearance
    inner_width = width - 2 * wall - 2 * clearance
    inner_radius = corner_radius - wall - clearance
    text_size = width / 5              # text grows with the box

    box = (
        cq.Workplane("XY")
        .box(length, width, height, centered=(True, True, False))
        .edges("|Z").fillet(corner_radius)
        .faces(">Z").shell(-wall)
        .faces("<Z").workplane()
        .rarray(length - 2 * foot_edge, width - 2 * foot_edge, 2, 2)
        .circle(foot_dia / 2).extrude(foot_height)
    )

    lid = (
        cq.Workplane("XY")
        .box(length, width, lid_thickness, centered=(True, True, False))
        .edges("|Z").fillet(corner_radius)
    )
    lip = (
        cq.Workplane("XY")
        .box(inner_length, inner_width, lip_height, centered=(True, True, False))
        .edges("|Z").fillet(inner_radius)
        .translate((0, 0, -lip_height))
    )
    lid = lid.union(lip)
    if text:
        lid = (
            lid.faces(">Z").workplane()
            .text(text, text_size, 0.6, combine=True)
        )

    return box, lid


# --- Part family: name, length, width, height, lid text ---
sizes = [
    ("small", 60, 40, 20, "M3"),
    ("medium", 80, 50, 30, "M4"),
    ("large", 120, 80, 40, "M5"),
]

for name, length, width, height, text in sizes:
    box, lid = make_box(length, width, height, text)
    in_place = lid.translate((0, 0, height))
    overlap = box.intersect(in_place).val().Volume()
    print(name, box.val().isValid(), lid.val().isValid(),
          len(box.solids().vals()), len(lid.solids().vals()),
          round(overlap, 3))
    cq.exporters.export(box, f"box_{name}.step")
    cq.exporters.export(lid, f"lid_{name}.step")
