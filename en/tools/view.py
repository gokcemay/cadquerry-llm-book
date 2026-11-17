"""Saves four views of the part in a CadQuery script into a single image.

Usage:  python tools/view.py <script.py> <variable_name> <output.png>
"""
import contextlib
import io
import runpy
import sys

from cadquery.vis import show
from PIL import Image, ImageChops, ImageDraw

VIEWS = [
    ("side (from -X)", (-1, 0, 0.001)),
    ("front (from -Y)", (0, -1, 0.001)),
    ("bottom", (0, -0.001, -1)),
    ("oblique", (1.0, -1.2, 0.8)),
]


def capture(part, direction, filename):
    box = part.val().BoundingBox()
    c = (box.center.x, box.center.y, box.center.z)
    r = max(box.xlen, box.ylen, box.zlen) * 2.2
    position = tuple(c[i] + 3 * direction[i] * r for i in range(3))
    show(part, screenshot=filename, interact=False, width=1200, height=900,
         position=position, focus=c, viewup=(0, 0, 1), roll=0, elevation=0,
         azimuth=0, gradient=False, trihedron=False, zoom=2.6)
    image = Image.open(filename).convert("RGB")
    white = Image.new("RGB", image.size, (255, 255, 255))
    bounds = ImageChops.difference(image, white).getbbox()
    return image.crop(bounds)


if __name__ == "__main__":
    script, variable, output = sys.argv[1], sys.argv[2], sys.argv[3]
    with contextlib.redirect_stdout(io.StringIO()):
        part = runpy.run_path(script)[variable]

    images = [(name, capture(part, d, f"/tmp/_v{i}.png"))
              for i, (name, d) in enumerate(VIEWS)]
    w = max(im.width for _, im in images) + 40
    h = max(im.height for _, im in images) + 70
    sheet = Image.new("RGB", (2 * w, 2 * h), "white")
    pen = ImageDraw.Draw(sheet)
    for i, (name, im) in enumerate(images):
        x, y = (i % 2) * w, (i // 2) * h
        sheet.paste(im, (x + (w - im.width) // 2,
                         y + 50 + (h - 70 - im.height) // 2))
        pen.text((x + 20, y + 15), name, fill=(40, 40, 40))
    sheet.save(output)
    print("saved:", output)
