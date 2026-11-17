import cadquery as cq

# Aynı parça için üç tarif denemesinin ilk ikisinin ürettiği kodlar.
# Üçüncüsü b11_kablo_klipsi.py dosyasıdır.

# --- Deneme 1: "Masaya takılan bir kablo tutucu yap." ---
# Tarifte ölçü yok; masa 20 mm, kablo 6 mm varsayılmış.
p1 = [(-25, 0), (0, 0), (0, -20), (-25, -20), (-25, -22.5), (2.5, -22.5),
      (2.5, 12), (-8, 12), (-8, 9.5), (0, 9.5), (0, 2.5), (-25, 2.5)]
deneme1 = cq.Workplane("YZ").polyline(p1).close().extrude(7.5, both=True)

# --- Deneme 2: ölçüler var, yön, sıkma, pay ve üretim bilgisi yok ---
# Masa 25 mm, iki adet 5 mm kablo, genişlik 20 mm, et 3 mm.
p2 = [(-20, 0), (0, 0), (0, -25), (-20, -25), (-20, -28), (3, -28),
      (3, 12), (-9, 12), (-9, 3), (-20, 3)]
deneme2 = cq.Workplane("YZ").polyline(p2).close().extrude(10, both=True)
delikler = (
    cq.Workplane("XZ").workplane(offset=-3)
    .pushPoints([(-5, 7.5), (5, 7.5)]).circle(2.5).extrude(12)
)
deneme2 = deneme2.cut(delikler)

for ad, p in (("deneme1", deneme1), ("deneme2", deneme2)):
    k = p.val().BoundingBox()
    print(ad, round(k.xlen, 1), round(k.ylen, 1), round(k.zlen, 1),
          round(p.val().Volume()), len(p.solids().vals()), p.val().isValid())
