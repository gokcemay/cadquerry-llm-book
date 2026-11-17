import cadquery as cq

# Yazıcının geçme payını bulmak için küçük bir deneme parçası:
# aynı pimin, giderek bollaşan beş yuvaya ne kadar rahat girdiğine bakılır.

# --- Ölçüler (mm) ---
pim_eni = 5.0
paylar = [0.0, 0.1, 0.2, 0.3, 0.4]     # her yuvanın pime göre bolluğu
yuva_araligi = 11
kalinlik = 6
yuva_derinligi = 10

uzunluk = yuva_araligi * len(paylar) + 6
genislik = yuva_derinligi + 8

mastar = cq.Workplane("XY").box(uzunluk, genislik, kalinlik,
                                centered=(False, False, False))
for i, pay in enumerate(paylar):
    x = 3 + yuva_araligi * i + yuva_araligi / 2
    yuva = (
        cq.Workplane("XY")
        .box(pim_eni + pay, yuva_derinligi, kalinlik, centered=(True, False, False))
        .translate((x, genislik - yuva_derinligi, 0))
    )
    mastar = mastar.cut(yuva)
    # Yuvanın önüne payı gösteren çentikler: 0,1 mm başına bir çentik
    for j in range(round(pay * 10)):
        centik = (
            cq.Workplane("XY").box(1, 1.5, 0.6, centered=(True, False, False))
            .translate((x - 3 + 1.5 * j, 1, kalinlik - 0.6))
        )
        mastar = mastar.cut(centik)

pim = cq.Workplane("XY").box(pim_eni, 25, kalinlik, centered=(True, False, False))

for ad, p in (("mastar", mastar), ("pim", pim)):
    k = p.val().BoundingBox()
    print(ad, round(k.xlen, 1), round(k.ylen, 1), round(k.zlen, 1),
          len(p.solids().vals()), p.val().isValid())

cq.exporters.export(mastar, "bosluk_mastari.stl")
cq.exporters.export(pim, "bosluk_pimi.stl")
