import cadquery as cq

# --- Ölçüler (mm) ---
genislik = 30          # askının genişliği
sirt_yukseklik = 80    # duvara yaslanan plakanın yüksekliği
sirt_kalinlik = 5
kol_uzunluk = 40       # kolun duvardan odaya doğru uzunluğu
kol_kalinlik = 8
uc_yukseklik = 18      # kolun ucundaki tırnağın yüksekliği
uc_kalinlik = 6
vida_cap = 4.5
vida_alt = 35          # alt vida deliğinin tabandan yüksekliği
vida_aralik = 30       # iki vida deliği arası

# Eksenler: X sağa, Y duvardan odaya doğru, Z yukarı.
# Duvar, Y = 0 düzlemidir.

# --- Sırt plakası: duvara yaslanan dik levha ---
sirt = cq.Workplane("XY").box(
    genislik, sirt_kalinlik, sirt_yukseklik, centered=(True, False, False)
)

# --- Kol: plakanın altından odaya doğru uzanan parça ---
kol = (
    cq.Workplane("XY")
    .box(genislik, kol_uzunluk, kol_kalinlik, centered=(True, False, False))
    .translate((0, sirt_kalinlik, 0))
)

# --- Uç: kolun ucunda yukarı kalkan tırnak ---
uc = (
    cq.Workplane("XY")
    .box(genislik, uc_kalinlik, uc_yukseklik, centered=(True, False, False))
    .translate((0, sirt_kalinlik + kol_uzunluk - uc_kalinlik, kol_kalinlik))
)

# --- Üç parçayı birleştir ---
aski = sirt.union(kol).union(uc)

# --- Vida delikleri: duvara bakan yüzden içeri doğru ---
aski = (
    aski.faces("<Y").workplane()
    .pushPoints([(0, vida_alt), (0, vida_alt + vida_aralik)])
    .hole(vida_cap, depth=sirt_kalinlik)
)

cq.exporters.export(aski, "duvar_askisi.step")
cq.exporters.export(aski, "duvar_askisi.stl")
