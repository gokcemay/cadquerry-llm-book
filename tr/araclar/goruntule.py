"""Bir CadQuery betiğindeki parçanın dört görünüşünü tek bir resme kaydeder.

Kullanım:  python araclar/goruntule.py <betik.py> <degisken_adi> <cikti.png>
"""
import contextlib
import io
import runpy
import sys

from cadquery.vis import show
from PIL import Image, ImageChops, ImageDraw

GORUNUSLER = [
    ("yandan (-X yonunden)", (-1, 0, 0.001)),
    ("onden (-Y yonunden)", (0, -1, 0.001)),
    ("alttan", (0, -0.001, -1)),
    ("egik", (1.0, -1.2, 0.8)),
]


def cek(parca, yon, dosya):
    k = parca.val().BoundingBox()
    m = (k.center.x, k.center.y, k.center.z)
    r = max(k.xlen, k.ylen, k.zlen) * 2.2
    konum = tuple(m[i] + 3 * yon[i] * r for i in range(3))
    show(parca, screenshot=dosya, interact=False, width=1200, height=900,
         position=konum, focus=m, viewup=(0, 0, 1), roll=0, elevation=0,
         azimuth=0, gradient=False, trihedron=False, zoom=2.6)
    resim = Image.open(dosya).convert("RGB")
    beyaz = Image.new("RGB", resim.size, (255, 255, 255))
    sinir = ImageChops.difference(resim, beyaz).getbbox()
    return resim.crop(sinir)


if __name__ == "__main__":
    betik, degisken, cikti = sys.argv[1], sys.argv[2], sys.argv[3]
    with contextlib.redirect_stdout(io.StringIO()):
        parca = runpy.run_path(betik)[degisken]

    resimler = [(ad, cek(parca, yon, f"/tmp/_g{i}.png"))
                for i, (ad, yon) in enumerate(GORUNUSLER)]
    en = max(r.width for _, r in resimler) + 40
    boy = max(r.height for _, r in resimler) + 70
    sayfa = Image.new("RGB", (2 * en, 2 * boy), "white")
    kalem = ImageDraw.Draw(sayfa)
    for i, (ad, r) in enumerate(resimler):
        x, y = (i % 2) * en, (i // 2) * boy
        sayfa.paste(r, (x + (en - r.width) // 2,
                        y + 50 + (boy - 70 - r.height) // 2))
        kalem.text((x + 20, y + 15), ad, fill=(40, 40, 40))
    sayfa.save(cikti)
    print("kaydedildi:", cikti)
