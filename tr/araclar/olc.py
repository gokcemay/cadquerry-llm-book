"""Bir CadQuery betiğini çalıştırır ve parçanın ölçüm raporunu yazar.

Kullanım:  python araclar/olc.py <betik.py> <degisken_adi>
"""
import collections
import contextlib
import io
import runpy
import sys

PLA_YOGUNLUK = 1.24     # g/cm3


def rapor(parca):
    govde = parca.val()
    k = govde.BoundingBox()
    print(f"dis olculer (mm): {k.xlen:.1f} x {k.ylen:.1f} x {k.zlen:.1f}")
    hacim = govde.Volume()
    kutle = hacim / 1000 * PLA_YOGUNLUK
    print(f"hacim: {hacim:.0f} mm3 | PLA kutle: {kutle:.1f} g")
    print(f"kati sayisi: {len(parca.solids().vals())} | "
          f"gecerli: {govde.isValid()}")

    turler = collections.Counter(yuz.geomType() for yuz in parca.faces().vals())
    print("yuz turleri:",
          ", ".join(f"{ad} {n}" for ad, n in sorted(turler.items())))

    # Tam daire kenarları: yarıçapa göre gruplanmış delik ve yuvarlak ağızlar
    daireler = collections.defaultdict(set)
    for kenar in parca.edges("%CIRCLE").vals():
        if kenar.IsClosed():
            m = kenar.Center()
            daireler[round(kenar.radius(), 2)].add(
                tuple(round(v, 1) + 0.0 for v in (m.x, m.y, m.z)))
    for yaricap, merkezler in sorted(daireler.items()):
        print(f"daire r = {yaricap}: {len(merkezler)} adet")
        for m in sorted(merkezler):
            print("   merkez", m)


if __name__ == "__main__":
    betik, degisken = sys.argv[1], sys.argv[2]
    # Betiğin kendi çıktısını sustur; yalnızca rapor yazılsın
    with contextlib.redirect_stdout(io.StringIO()):
        ad_uzayi = runpy.run_path(betik)
    rapor(ad_uzayi[degisken])
