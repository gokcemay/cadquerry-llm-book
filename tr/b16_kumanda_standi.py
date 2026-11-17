import math
import sys

import cadquery as cq

sys.path.insert(0, "araclar")
import baski_yonu  # noqa: E402  (Bölüm 15'teki destek aracı)

# Eksenler: X standın eni boyunca, Y önden arkaya, Z yukarı.
# Standın alt yüzü Z = 0; ön yüz -Y yönüne bakar.

# --- Girdiler: kumandalar (mm, gram) ---
# Genişlik ve kalınlık: kumandanın alt 45 mm'sindeki en büyük değer.
kumandalar = [
    # (etiket, genişlik, kalınlık, boy, kütle)
    ("TV", 45, 20, 180, 95),
    ("UYDU", 52, 24, 210, 130),
    ("KLİMA", 58, 18, 140, 80),
]

PLA_YOGUNLUK = 1.24 / 1000    # g/mm3


def stand_yap(kumandalar, pay=1.0, et=2.4, taban=3, cep_derinlik=45,
              tabla_derinlik=70, yazi_boyu=7):
    """Kumanda standı. tabla_derinlik=0 verilirse taban tablası olmaz."""
    cepler = [(g + pay, k + pay) for _, g, k, _, _ in kumandalar]
    govde_en = sum(c[0] for c in cepler) + (len(cepler) + 1) * et
    govde_derinlik = max(c[1] for c in cepler) + 2 * et
    yukseklik = taban + cep_derinlik

    # Gövde: tabana oturan dikdörtgen blok, dik kenarları kavisli
    stand = (
        cq.Workplane("XY").rect(govde_en, govde_derinlik).extrude(yukseklik)
        .edges("|Z").fillet(3)
    )

    # Taban tablası: devrilmeye karşı öne ve arkaya taşan levha
    if tabla_derinlik > govde_derinlik:
        tabla = (
            cq.Workplane("XY").rect(govde_en, tabla_derinlik).extrude(taban)
            .edges("|Z").fillet(3)
        )
        stand = stand.union(tabla)

    # Tablaya oturan kenarlar: kavis değil pah (1 kapalı çevre)
    stand = stand.faces("<Z").edges().chamfer(0.6)

    # Cepler: üstten aşağı, soldan sağa dizili
    x = -govde_en / 2 + et
    merkezler = []
    for cep_en, cep_kal in cepler:
        merkez = x + cep_en / 2
        cep = (
            cq.Workplane("XY").workplane(offset=taban)
            .center(merkez, 0).rect(cep_en, cep_kal).extrude(cep_derinlik)
        )
        stand = stand.cut(cep)
        merkezler.append(merkez)
        x += cep_en + et

    # Kabartma etiketler: tablanın öne taşan kısmında, yukarı bakan yüzde
    on_pay = (tabla_derinlik - govde_derinlik) / 2
    if yazi_boyu > 0 and on_pay >= yazi_boyu + 4:
        y_yazi = -(govde_derinlik / 2 + on_pay / 2)
        for (etiket, *_), merkez in zip(kumandalar, merkezler):
            yazi = (
                cq.Workplane("XY").workplane(offset=taban)
                .center(merkez, y_yazi)
                .text(etiket, yazi_boyu, 0.8, combine=False)
            )
            stand = stand.union(yazi)

    olculer = dict(govde_en=govde_en, govde_derinlik=govde_derinlik,
                   yukseklik=yukseklik, merkezler=merkezler, cepler=cepler,
                   taban=taban, et=et, pay=pay,
                   taban_derinlik=max(tabla_derinlik, govde_derinlik))
    return stand, olculer


def kumanda_modeli(kumanda, merkez, taban):
    """Kumandanın yerine geçen blok: cebin tabanına oturur."""
    _, g, k, boy, _ = kumanda
    return (
        cq.Workplane("XY").workplane(offset=taban)
        .center(merkez, 0).rect(g, k).extrude(boy)
    )


def devrilme_acisi(stand, o, kumandalar, dolgu=0.5):
    """Stand, öne ya da arkaya kaç derece eğilince devrilir?

    Standın içi yarı dolu sayılır (dolgu=0.5): hafif stand, kötü durum.
    """
    kutle = stand.val().Volume() * PLA_YOGUNLUK * dolgu
    moment = kutle * cq.Shape.centerOfMass(stand.val()).z
    for _, _, _, boy, m in kumandalar:
        kutle += m
        moment += m * (o["taban"] + boy / 2)
    agirlik_merkezi_z = moment / kutle
    return math.degrees(math.atan(o["taban_derinlik"] / 2 / agirlik_merkezi_z))


def denetle(kumandalar, en_az_aci=20, **ayar):
    stand, o = stand_yap(kumandalar, **ayar)
    s = stand.val()

    # 1. Tek ve geçerli katı
    assert stand.solids().size() == 1, "Stand tek parça değil"
    assert s.isValid(), "Katı geçerli değil"

    # 2. Her kumanda cebine çakışmadan girer; her yanda pay/2 boşluk kalır
    for kumanda, merkez, cep in zip(kumandalar, o["merkezler"], o["cepler"]):
        model = kumanda_modeli(kumanda, merkez, o["taban"])
        ortak = stand.intersect(model)
        hacim = ortak.val().Volume() if ortak.solids().size() else 0.0
        assert hacim < 0.01, f"{kumanda[0]} standla çakışıyor: {hacim:.1f} mm3"
        assert abs(cep[0] - kumanda[1] - o["pay"]) < 0.01, "Cep eni yanlış"

    # 3. Dış ölçüler: yükseklik kumandaların en kısasının yarısını geçmesin
    k = s.BoundingBox()
    en_kisa = min(boy for _, _, _, boy, _ in kumandalar)
    assert k.zlen <= en_kisa / 2, "Stand, en kısa kumandanın tuşlarını örtüyor"

    # 4. Baskı: tasarlandığı yönde destek gerekmesin
    _, _, destek = baski_yonu.yon_raporu(s)
    assert destek < 1, f"Destek isteyen alan var: {destek:.0f} mm2"

    # 5. Devrilme: stand en az bu açıya kadar eğilebilmeli
    aci = devrilme_acisi(stand, o, kumandalar)
    assert aci >= en_az_aci, f"Kolay devrilir: devrilme açısı {aci:.1f} derece"

    kutle = s.Volume() * PLA_YOGUNLUK
    print(f"5 denetim gecti | {k.xlen:.1f} x {k.ylen:.1f} x {k.zlen:.1f} mm |",
          f"en cok {kutle:.0f} g | devrilme acisi {aci:.1f} derece")
    return stand, o


if __name__ == "__main__":
    stand, o = denetle(kumandalar)
    cq.exporters.export(stand, "kumanda_standi.step")
    cq.exporters.export(stand, "kumanda_standi.stl",
                        tolerance=0.05, angularTolerance=0.2)
