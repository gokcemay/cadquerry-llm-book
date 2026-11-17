"""Runs a CadQuery script and prints a measurement report for the part.

Usage:  python tools/measure.py <script.py> <variable_name>
"""
import collections
import contextlib
import io
import runpy
import sys

PLA_DENSITY = 1.24     # g/cm3


def report(part):
    shape = part.val()
    box = shape.BoundingBox()
    print(f"outer size (mm): {box.xlen:.1f} x {box.ylen:.1f} x {box.zlen:.1f}")
    volume = shape.Volume()
    mass = volume / 1000 * PLA_DENSITY
    print(f"volume: {volume:.0f} mm3 | PLA mass: {mass:.1f} g")
    print(f"solids: {len(part.solids().vals())} | "
          f"valid: {shape.isValid()}")

    kinds = collections.Counter(f.geomType() for f in part.faces().vals())
    print("face types:",
          ", ".join(f"{name} {n}" for name, n in sorted(kinds.items())))

    # Full circular edges, grouped by radius: holes and round openings
    circles = collections.defaultdict(set)
    for edge in part.edges("%CIRCLE").vals():
        if edge.IsClosed():
            c = edge.Center()
            circles[round(edge.radius(), 2)].add(
                tuple(round(v, 1) + 0.0 for v in (c.x, c.y, c.z)))
    for radius, centres in sorted(circles.items()):
        print(f"circle r = {radius}: {len(centres)} found")
        for c in sorted(centres):
            print("   centre", c)


if __name__ == "__main__":
    script, variable = sys.argv[1], sys.argv[2]
    # Silence the script's own output; print only the report
    with contextlib.redirect_stdout(io.StringIO()):
        namespace = runpy.run_path(script)
    report(namespace[variable])
