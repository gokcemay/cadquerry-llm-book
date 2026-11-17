import cadquery as cq

# Eksenler: X askının eni boyunca, Y masanın altında kenardan içeriye,
# Z yukarı. Masanın alt yüzü Z = 0; askı bu yüzün altında durur.

# --- Girdiler (mm) ---
bant_genislik = 30     # kulaklık bandının oturacağı açıklık

# --- Sabitler ---
en = 25
et = 5
plaka_boyu = 80
kol_boyu = 45          # plakanın altından taşıyıcının üstüne
tirnak = 8             # tırnağın taşıyıcı üstündeki yüksekliği
vida_cap = 4.5
havsa_cap = 9
tornavida_cap = 8

# --- Türetilen ölçüler ---
tasiyici_boyu = et + bant_genislik + et
z_plaka = -et                      # plakanın alt yüzü
z_ust = -et - kol_boyu             # taşıyıcının üst yüzü
z_alt = z_ust - et                 # taşıyıcının alt yüzü
vida_kenar = 10                    # son vidanın plaka ucuna uzaklığı
vida_aralik = 18
vida_y = [plaka_boyu - vida_kenar - vida_aralik, plaka_boyu - vida_kenar]

# --- Gövde: yandan görünüş profili, en boyunca uzatılır ---
profil = [
    (0, 0), (plaka_boyu, 0), (plaka_boyu, z_plaka), (et, z_plaka),
    (et, z_ust), (tasiyici_boyu - et, z_ust),
    (tasiyici_boyu - et, z_ust + tirnak), (tasiyici_boyu, z_ust + tirnak),
    (tasiyici_boyu, z_alt), (0, z_alt),
]
aski = cq.Workplane("YZ").polyline(profil).close().extrude(en / 2, both=True)

# --- İç köşe kavisleri (her biri 1 kenar) ---
def kose(y, z):
    return cq.selectors.BoxSelector((-en, y - 1, z - 1), (en, y + 1, z + 1))

aski = aski.edges(kose(et, z_plaka)).fillet(10)                 # plaka-kol
aski = aski.edges(kose(et, z_ust)).fillet(6)                    # kol-taşıyıcı
aski = aski.edges(kose(tasiyici_boyu - et, z_ust)).fillet(3)    # taşıyıcı-tırnak

# --- Havşalı vida delikleri: plakanın alt yüzünden yukarı (2 delik) ---
# Aşağı bakan yüzlerin en üsttekisi plakanın alt yüzüdür.
# Bu yüzde yerel Y ekseni ters yöne bakar; konumlar eksi işaretle verilir.
aski = (
    aski.faces("-Z").faces(">Z").workplane()
    .pushPoints([(0, -y) for y in vida_y])
    .cskHole(vida_cap, havsa_cap, 90)
)

# --- Ölç ---
k = aski.val().BoundingBox()
print("dis olculer:", k.xlen, k.ylen, k.zlen)
print("hacim:", round(aski.val().Volume()))
print("kati:", len(aski.solids().vals()), "gecerli:", aski.val().isValid())
print("koni yuz:", aski.faces("%CONE").size())

# Tornavida erişimi: her vidanın altında 100 mm'lik boş bir silindir olmalı
for y in vida_y:
    tornavida = (
        cq.Workplane("XY").circle(tornavida_cap / 2).extrude(-100)
        .translate((0, y, z_plaka))
    )
    ortak = aski.intersect(tornavida)
    hacim = ortak.val().Volume() if ortak.solids().size() else 0.0
    print("  vida y =", y, "tornavida cakismasi:", round(hacim, 1))

cq.exporters.export(aski, "kulaklik_askisi.step")
cq.exporters.export(aski, "kulaklik_askisi.stl",
                    tolerance=0.05, angularTolerance=0.2)
