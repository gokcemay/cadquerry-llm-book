"""Bir parçayı altı yöne çevirip her yön için baskı yüksekliğini,
tablaya değen alanı ve destek isteyen yüzey alanını raporlar.

Kullanım: python araclar/baski_yonu.py <betik.py> <degisken_adi>
"""
import math
import runpy
import sys

import cadquery as cq

ESIK = 45          # derece; düşeyden bundan fazla yatan yüzey destek ister
ESIK_PAYI = 1     # derece; üçgenleme hatası için pay
HASSASIYET = 0.05  # üçgenleme hassasiyeti (mm)

# Hangi eksen yukarı bakacak? (dönme ekseni, açı)
YONLER = {
    "+Z yukari (tasarlandigi gibi)": ((1, 0, 0), 0),
    "-Z yukari (bas asagi)": ((1, 0, 0), 180),
    "+X yukari": ((0, 1, 0), -90),
    "-X yukari": ((0, 1, 0), 90),
    "+Y yukari": ((1, 0, 0), 90),
    "-Y yukari": ((1, 0, 0), -90),
}


def cevir(sekil, yon):
    eksen, aci = YONLER[yon]
    return sekil.rotate((0, 0, 0), eksen, aci)


def ucgenler(sekil):
    """Üçgenler (alan, normalin Z bileşeni, merkezin Z'si), en alt ve en üst Z."""
    noktalar, uclu = sekil.tessellate(HASSASIYET, 0.1)
    liste = []
    for a, b, c in uclu:
        p, q, r = noktalar[a], noktalar[b], noktalar[c]
        n = (q - p).cross(r - p)
        if n.Length > 1e-9:
            liste.append((n.Length / 2, n.z / n.Length, (p.z + q.z + r.z) / 3))
    zler = [p.z for p in noktalar]
    return liste, min(zler), max(zler)


def yon_raporu(sekil):
    """Yükseklik (mm), tabla teması (mm2), destek isteyen alan (mm2)."""
    liste, alt, ust = ucgenler(sekil)
    # Eşiğin 1 derece ötesine kadar olan yüzeyler desteksiz sayılır:
    # 45 derecelik pah ve koniler üçgenlenince tam 45 derecede kalmaz.
    sinir = -math.sin(math.radians(ESIK + ESIK_PAYI))
    tabla = destek = 0.0
    for alan, nz, z in liste:
        if nz < -0.999 and z - alt < 0.01:
            tabla += alan          # tablaya oturan yüz
        elif nz < sinir:
            destek += alan         # havada kalan, aşağı bakan yüz
    return ust - alt, tabla, destek


if __name__ == "__main__":
    betik, ad = sys.argv[1], sys.argv[2]
    parca = runpy.run_path(betik)[ad]
    sekil = parca.val() if isinstance(parca, cq.Workplane) else parca
    print(f"{'yon':32s}{'yukseklik':>10s}{'tabla':>9s}{'destek':>9s}")
    for yon in YONLER:
        h, tabla, destek = yon_raporu(cevir(sekil, yon))
        print(f"{yon:32s}{h:10.1f}{tabla:9.0f}{destek:9.0f}")
