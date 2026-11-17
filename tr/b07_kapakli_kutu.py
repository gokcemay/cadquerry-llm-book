import cadquery as cq

# --- Ölçüler (mm) ---
uzunluk = 80
genislik = 50
yukseklik = 30
kose_kavis = 6
et = 2
kapak_kalinlik = 3
dudak_yukseklik = 3
bosluk = 0.3           # kapak dudağı ile kutu içi arasında, her yanda bırakılan pay
ayak_cap = 8
ayak_yukseklik = 1.5
ayak_kenar = 12        # ayak merkezinin kenara uzaklığı
yazi = "VİDALAR"
yazi_boyu = 9
yazi_yukseklik = 0.6

# --- Kutu: dolu blok, köşeler yuvarlak, içi boşaltılmış ---
kutu = (
    cq.Workplane("XY")
    .box(uzunluk, genislik, yukseklik, centered=(True, True, False))
    .edges("|Z").fillet(kose_kavis)
    .faces(">Z").shell(-et)
)

# --- Tabana dört ayak ---
kutu = (
    kutu.faces("<Z").workplane()
    .rarray(uzunluk - 2 * ayak_kenar, genislik - 2 * ayak_kenar, 2, 2)
    .circle(ayak_cap / 2).extrude(ayak_yukseklik)
)

# --- Kapak: düz plaka ve kutunun içine giren dudak ---
ic_uzunluk = uzunluk - 2 * et - 2 * bosluk
ic_genislik = genislik - 2 * et - 2 * bosluk
ic_kavis = kose_kavis - et - bosluk

kapak = (
    cq.Workplane("XY")
    .box(uzunluk, genislik, kapak_kalinlik, centered=(True, True, False))
    .edges("|Z").fillet(kose_kavis)
)
dudak = (
    cq.Workplane("XY")
    .box(ic_uzunluk, ic_genislik, dudak_yukseklik, centered=(True, True, False))
    .edges("|Z").fillet(ic_kavis)
    .translate((0, 0, -dudak_yukseklik))
)
kapak = kapak.union(dudak)

# --- Kapağın üstüne kabartma yazı ---
kapak = (
    kapak.faces(">Z").workplane()
    .text(yazi, yazi_boyu, yazi_yukseklik, combine=True)
)

# --- Ölç ve kaydet ---
for ad, parca in (("kutu", kutu), ("kapak", kapak)):
    k = parca.val().BoundingBox()
    print(ad, k.xlen, k.ylen, k.zlen, parca.val().Volume(),
          len(parca.solids().vals()), parca.val().isValid())

cq.exporters.export(kutu, "kutu.step")
cq.exporters.export(kutu, "kutu.stl")
cq.exporters.export(kapak, "kapak.step")
cq.exporters.export(kapak, "kapak.stl")
