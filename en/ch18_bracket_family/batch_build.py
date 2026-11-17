"""Builds, checks and packages one bracket for every row of table.csv.

Usage: python batch_build.py table.csv delivery
"""
import csv
import os
import shutil
import sys
import time

import cadquery as cq

import bracket as b
import sheet

INTEGERS = ("holes_a", "holes_b")


def read_row(row):
    return {k: (int(v) if k in INTEGERS else float(v))
            for k, v in row.items()}


def build(p, folder):
    """A single bracket: model, flat pattern, checks, files. Returns a summary row."""
    name = b.make_name(p)
    bracket, o = b.make_bracket(p)              # rule violation: ValueError
    a = b.flat_pattern(p, o)
    target = os.path.join(folder, name)
    os.makedirs(target, exist_ok=True)
    stem = os.path.join(target, name)
    b.flat_pattern_dxf(p, a, stem + "_flat.dxf")
    # If a check fails: AssertionError
    volume = b.verify(p, bracket, o, a, stem + "_flat.dxf")
    mass = volume * b.RULES["density"]
    cq.exporters.export(bracket, stem + ".step")
    sheet.draw_sheet(p, name, a, mass, b.RULES, stem + "_sheet")
    return dict(name=name, status="ok", mass_g=round(mass, 1),
                flat_length=round(a["length"], 2),
                bend_line=round(a["bend_line"], 2), note="")


def batch_build(table, folder):
    shutil.rmtree(folder, ignore_errors=True)
    os.makedirs(folder)
    summary, seen = [], set()
    with open(table, encoding="utf-8") as f:
        rows = [read_row(r) for r in csv.DictReader(f)]
    for no, p in enumerate(rows, start=2):      # row 1 is the header
        name = b.make_name(p)
        empty = dict(name=name, mass_g="", flat_length="", bend_line="")
        if name in seen:
            summary.append(dict(empty, status="duplicate",
                                note=f"row {no}: the same part already exists"))
            continue
        seen.add(name)
        try:
            summary.append(build(p, folder))
        except ValueError as err:
            shutil.rmtree(os.path.join(folder, name), ignore_errors=True)
            summary.append(dict(empty, status="rule",
                                note=f"row {no}: {err}"))
        except AssertionError as err:
            shutil.rmtree(os.path.join(folder, name), ignore_errors=True)
            summary.append(dict(empty, status="check",
                                note=f"row {no}: {err}"))

    with open(os.path.join(folder, "summary.csv"), "w", newline="",
              encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)

    k = b.RULES
    with open(os.path.join(folder, "README.txt"), "w", encoding="utf-8") as f:
        f.write(
            "L bracket family - delivery package\n"
            f"Date: {time.strftime('%Y-%m-%d')}\n\n"
            "Each part folder contains: STEP (bent shape), flat-pattern DXF "
            "(CUT and BEND layers),\ndimension sheet (PDF and PNG).\n\n"
            "Material: steel sheet. Bend: 90 degrees, inner radius = thickness.\n"
            f"The flat pattern was computed with k-factor {k['k_factor']:g}; tell us "
            "if your own press brake uses a different value.\n"
            "Dimensions in mm. Unspecified tolerances follow workshop standard.\n"
            "summary.csv: list of the rows that were and were not produced.\n"
            "table.csv: the input table this package was produced from.\n")
    # So that it is clear what the package was built from, the input table goes in too
    shutil.copy(table, os.path.join(folder, "table.csv"))
    shutil.make_archive(folder, "zip", folder)
    return summary


if __name__ == "__main__":
    start = time.time()
    summary = batch_build(sys.argv[1], sys.argv[2])
    for status in ("ok", "rule", "check", "duplicate"):
        print(f"{status}: {sum(1 for s in summary if s['status'] == status)}")
    for s in summary:
        if s["status"] != "ok":
            print(" ", s["name"], "->", s["note"])
    print(f"time: {time.time() - start:.0f} s")
