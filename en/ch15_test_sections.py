import cadquery as cq

# Separates only the parts of the headphone hanger (Chapter 12) that need testing.
# These small parts are printed and tried before the whole part is printed.

hanger = cq.importers.importStep("headphone_hanger.step")


def section(part, x, y, z):
    """The part of the shape inside the given ranges. Each range: (low, high)."""
    block = (
        cq.Workplane("XY")
        .box(x[1] - x[0], y[1] - y[0], z[1] - z[0], centered=False)
        .translate((x[0], y[0], z[0]))
    )
    return part.intersect(block)


# Screw section: the end of the plate carrying the two holes. For screw and countersink fit.
screw_section = section(hanger, (-12.5, 12.5), (44, 80), (-5, 0))

# Profile slice: a 3 mm slice from the edge. For the band opening and the tab.
profile_slice = section(hanger, (9.5, 12.5), (0, 80), (-55, 0))

# --- Measure ---
full = hanger.val().Volume()
for name, p in [("screw section", screw_section), ("profile slice", profile_slice)]:
    b = p.val().BoundingBox()
    v = p.val().Volume()
    print(f"{name}: {b.xlen:.1f} x {b.ylen:.1f} x {b.zlen:.1f} mm |",
          f"solids: {p.solids().size()} |",
          f"volume: {v:.0f} mm3 ({100 * v / full:.0f}%)")

cq.exporters.export(screw_section, "hanger_screw_section.stl",
                    tolerance=0.05, angularTolerance=0.2)
cq.exporters.export(profile_slice, "hanger_profile_slice.stl",
                    tolerance=0.05, angularTolerance=0.2)
