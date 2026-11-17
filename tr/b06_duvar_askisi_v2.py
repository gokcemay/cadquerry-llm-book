import cadquery as cq

# --- Ölçüler (mm) ---
genislik = 30
sirt_yukseklik = 80
sirt_kalinlik = 5
kol_uzunluk = 40
kol_kalinlik = 8
uc_yukseklik = 18
uc_kalinlik = 6
vida_cap = 4.5
vida_alt = 35
vida_aralik = 30
ic_kavis_sirt = 6      # kol ile sırt plakası arasındaki iç köşe
ic_kavis_uc = 4        # kol ile uç arasındaki iç köşe
dis_kavis = 2          # ucun dış dikey kenarları
havsa_cap = 9          # vida başı için konik havşa çapı
havsa_aci = 90

# Eksenler: X sağa, Y duvardan odaya doğru, Z yukarı. Duvar Y = 0.

# --- Sırt plakası; odaya bakan yüzü kol eklenmeden önce etiketleniyor ---
sirt = (
    cq.Workplane("XY")
    .box(genislik, sirt_kalinlik, sirt_yukseklik, centered=(True, False, False))
    .faces(">Y").workplane().tag("on_yuz")
)

kol = (
    cq.Workplane("XY")
    .box(genislik, kol_uzunluk, kol_kalinlik, centered=(True, False, False))
    .translate((0, sirt_kalinlik, 0))
)

uc = (
    cq.Workplane("XY")
    .box(genislik, uc_kalinlik, uc_yukseklik, centered=(True, False, False))
    .translate((0, sirt_kalinlik + kol_uzunluk - uc_kalinlik, kol_kalinlik))
)

aski = sirt.union(kol).union(uc)

# --- İç köşe 1: kolun sırt plakasıyla birleştiği kenar (1 kenar) ---
kose_sirt = cq.selectors.BoxSelector(
    (-genislik, sirt_kalinlik - 1, kol_kalinlik - 1),
    (genislik, sirt_kalinlik + 1, kol_kalinlik + 1),
)
aski = aski.edges(kose_sirt).fillet(ic_kavis_sirt)

# --- İç köşe 2: kolun uçla birleştiği kenar (1 kenar) ---
uc_ic_y = sirt_kalinlik + kol_uzunluk - uc_kalinlik
kose_uc = cq.selectors.BoxSelector(
    (-genislik, uc_ic_y - 1, kol_kalinlik - 1),
    (genislik, uc_ic_y + 1, kol_kalinlik + 1),
)
aski = aski.edges(kose_uc).fillet(ic_kavis_uc)

# --- Ucun dış dikey kenarları (2 kenar) ---
aski = aski.edges("|Z and >Y").fillet(dis_kavis)

# --- Havşalı vida delikleri: odaya bakan yüzden duvara doğru ---
aski = (
    aski.workplaneFromTagged("on_yuz")
    .pushPoints([(0, vida_alt), (0, vida_alt + vida_aralik)])
    .cskHole(vida_cap, havsa_cap, havsa_aci)
)

# --- Ölç ve kaydet ---
kutu = aski.val().BoundingBox()
print(kutu.xlen, kutu.ylen, kutu.zlen)
print(aski.val().Volume())
print(len(aski.solids().vals()))

cq.exporters.export(aski, "duvar_askisi_v2.step")
cq.exporters.export(aski, "duvar_askisi_v2.stl")
