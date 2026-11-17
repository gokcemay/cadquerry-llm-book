import cadquery as cq

# --- Ölçüler (mm): askı kodundakilerle aynı ---
sirt_kalinlik = 5
vida_alt = 35
vida_aralik = 30

# --- Parçalar ---
# Askı, daha önce kaydedilen STEP dosyasından okunuyor
aski = cq.importers.importStep("duvar_askisi_v2.step")

# Havşa başlı M4 x 20 vida: yarım kesit çizilip döndürülüyor (diş yok)
vida = (
    cq.Workplane("XY")
    .polyline([(0, 0), (4, 0), (2, -2), (2, -20), (0, -20)])
    .close().revolve()
)

# Duvarı temsil eden blok ve vida delikleri
duvar = (
    cq.Workplane("XY")
    .box(120, 20, 140, centered=(True, False, False))
    .translate((0, -20, -30))
    .faces(">Y").workplane()
    .pushPoints([(0, vida_alt), (0, vida_alt + vida_aralik)])
    .hole(4, depth=18)
)

# --- Montaj: her parça adı, konumu ve rengiyle ekleniyor ---
gri = cq.Color(0.25, 0.25, 0.28)
mavi = cq.Color(0.25, 0.45, 0.70)
bej = cq.Color(0.87, 0.82, 0.72)

montaj = (
    cq.Assembly(name="aski_montaji")
    .add(duvar, name="duvar", color=bej)
    .add(aski, name="aski", color=mavi)
    .add(vida, name="vida_alt", color=gri,
         loc=cq.Location((0, sirt_kalinlik, vida_alt)))
    .add(vida, name="vida_ust", color=gri,
         loc=cq.Location((0, sirt_kalinlik, vida_alt + vida_aralik)))
)

# --- Çakışma denetimi: vidalar askıya ve duvara giriyor mu? ---
for z in (vida_alt, vida_alt + vida_aralik):
    yerinde = vida.translate((0, sirt_kalinlik, z))
    for ad, parca in (("aski", aski), ("duvar", duvar)):
        ortak = parca.intersect(yerinde)
        hacim = ortak.val().Volume() if ortak.solids().size() else 0.0
        print("vida z =", z, ad, "cakisma:", round(hacim, 3))

montaj.export("aski_montaji.step")
