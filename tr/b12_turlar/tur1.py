import cadquery as cq

# Eksenler: X askının eni boyunca, Y masanın altında kenardan içeriye,
# Z yukarı. Masanın alt yüzü Z = 0; askı bu yüzün altında durur.

# --- Girdiler (mm) ---
bant_genislik = 30     # kulaklık bandının oturacağı açıklık

# --- Sabitler ---
en = 25
et = 5
plaka_boyu = 60
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
vida_y = [15, 45]                  # vida deliklerinin Y konumları

# --- Gövde: yandan görünüş profili, en boyunca uzatılır ---
profil = [
    (0, 0), (plaka_boyu, 0), (plaka_boyu, z_plaka), (et, z_plaka),
    (et, z_ust), (tasiyici_boyu - et, z_ust),
    (tasiyici_boyu - et, z_ust + tirnak), (tasiyici_boyu, z_ust + tirnak),
    (tasiyici_boyu, z_alt), (0, z_alt),
]
aski = cq.Workplane("YZ").polyline(profil).close().extrude(en / 2, both=True)

# --- Havşalı vida delikleri ---
aski = (
    aski.faces("<Z").workplane()
    .pushPoints([(0, y) for y in vida_y])
    .countersinkHole(vida_cap, havsa_cap, 90)
)

# --- Ölç ---
k = aski.val().BoundingBox()
print("dis olculer:", k.xlen, k.ylen, k.zlen)
print("hacim:", round(aski.val().Volume()))
print("kati:", len(aski.solids().vals()), "gecerli:", aski.val().isValid())
