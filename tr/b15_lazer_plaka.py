import cadquery as cq

# Bölüm 2'deki montaj plakasından lazer kesim çizimi (DXF) üretir.

# --- Girdiler (mm) ---
uzunluk = 100
genislik = 60
kalinlik = 5
kose_yaricap = 8
delik_cap = 4.5
delik_kenar = 10
pah = 1
kesim_payi = 0.2      # atölyeden öğrenin ya da deneme kesimiyle ölçün

# --- Plaka (Bölüm 2'deki kod) ---
plaka = (
    cq.Workplane("XY").rect(uzunluk, genislik).extrude(kalinlik)
    .edges("|Z").fillet(kose_yaricap)
    .faces(">Z").edges().chamfer(pah)
    .faces(">Z").workplane()
    .rect(uzunluk - 2 * delik_kenar, genislik - 2 * delik_kenar,
          forConstruction=True)
    .vertices().hole(delik_cap)
)

# --- Kesit: plakanın orta yüksekliğinden ---
# section() yüksekliği geçerli çalışma düzleminden ölçer. Bu plakada o
# düzlem pahlı üst yüzdür; bu yüzden kalınlığın yarısı kadar iniyoruz.
kesit = plaka.section(-kalinlik / 2).faces().val()


def otele(cevre, miktar):
    """Kapalı çevreyi büyütür (miktar > 0) ya da küçültür (miktar < 0).

    offset2D'nin işareti çevrenin dönüş yönüne bağlıdır. İki yönü de
    dener, içerdiği alanı ölçer ve isteneni seçer.
    """
    adaylar = [cevre.offset2D(m)[0] for m in (miktar, -miktar)]
    adaylar.sort(key=lambda c: cq.Face.makeFromWires(c).Area())
    return adaylar[1] if miktar > 0 else adaylar[0]


# Lazer, çizginin iki yanından kesim payının yarısını götürür:
# dış çevre o kadar büyütülür, delikler o kadar küçültülür.
dis = otele(kesit.outerWire(), kesim_payi / 2)
delikler = [otele(d, -kesim_payi / 2) for d in kesit.innerWires()]
cizim = cq.Workplane("XY").add([dis] + delikler)

# --- Denetle ---
k = dis.BoundingBox()
assert abs(k.xlen - (uzunluk + kesim_payi)) < 0.01, "Dış çevre yanlış"
assert abs(k.ylen - (genislik + kesim_payi)) < 0.01, "Dış çevre yanlış"
assert len(delikler) == 4, "Delik sayısı yanlış"
for d in delikler:
    cap = d.BoundingBox().xlen
    assert abs(cap - (delik_cap - kesim_payi)) < 0.01, "Delik çapı yanlış"
print("cizim:", round(k.xlen, 2), "x", round(k.ylen, 2),
      "| delik capi:", round(delikler[0].BoundingBox().xlen, 2))

cq.exporters.exportDXF(cizim, "montaj_plakasi_lazer.dxf")

# --- Dosyayı geri oku ---
geri = cq.importers.importDXF("montaj_plakasi_lazer.dxf")
g = geri.val().BoundingBox()
print("DXF:", round(g.xlen, 2), "x", round(g.ylen, 2),
      "| kapali cevre:", geri.wires().size())
