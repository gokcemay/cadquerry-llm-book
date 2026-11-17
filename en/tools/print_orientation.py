"""Rotates a part to each of the six orientations and reports, per
orientation, the print height, the contact area with the bed and the
surface area that needs support.

Usage: python tools/print_orientation.py <script.py> <variable_name>
"""
import math
import runpy
import sys

import cadquery as cq

THRESHOLD = 45        # degrees; surfaces leaning more than this need support
THRESHOLD_MARGIN = 1  # degrees; margin for tessellation error
TOLERANCE = 0.05      # tessellation tolerance (mm)

# Which axis points up? (rotation axis, angle)
ORIENTATIONS = {
    "+Z up (as designed)": ((1, 0, 0), 0),
    "-Z up (upside down)": ((1, 0, 0), 180),
    "+X up": ((0, 1, 0), -90),
    "-X up": ((0, 1, 0), 90),
    "+Y up": ((1, 0, 0), 90),
    "-Y up": ((1, 0, 0), -90),
}


def rotate(shape, orientation):
    axis, angle = ORIENTATIONS[orientation]
    return shape.rotate((0, 0, 0), axis, angle)


def triangles(shape):
    """Triangles (area, normal Z component, centre Z), lowest and highest Z."""
    points, tris = shape.tessellate(TOLERANCE, 0.1)
    result = []
    for a, b, c in tris:
        p, q, r = points[a], points[b], points[c]
        n = (q - p).cross(r - p)
        if n.Length > 1e-9:
            result.append((n.Length / 2, n.z / n.Length, (p.z + q.z + r.z) / 3))
    zs = [p.z for p in points]
    return result, min(zs), max(zs)


def orientation_report(shape):
    """Height (mm), bed contact (mm2), area needing support (mm2)."""
    tris, low, high = triangles(shape)
    # Surfaces up to 1 degree beyond the threshold count as self-supporting:
    # 45-degree chamfers and cones do not stay at exactly 45 after meshing.
    limit = -math.sin(math.radians(THRESHOLD + THRESHOLD_MARGIN))
    bed = support = 0.0
    for area, nz, z in tris:
        if nz < -0.999 and z - low < 0.01:
            bed += area          # face resting on the bed
        elif nz < limit:
            support += area      # downward-facing face in mid-air
    return high - low, bed, support


if __name__ == "__main__":
    script, name = sys.argv[1], sys.argv[2]
    part = runpy.run_path(script)[name]
    shape = part.val() if isinstance(part, cq.Workplane) else part
    print(f"{'orientation':32s}{'height':>10s}{'bed':>9s}{'support':>9s}")
    for orientation in ORIENTATIONS:
        h, bed, support = orientation_report(rotate(shape, orientation))
        print(f"{orientation:32s}{h:10.1f}{bed:9.0f}{support:9.0f}")
