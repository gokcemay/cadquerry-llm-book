import math
import cadquery as cq

PLA_YOGUNLUK = 1.24        # g/cm3


def stand_yap(cihaz_genislik, cihaz_yukseklik, cihaz_kalinlik, aci=65,
              bosluk=1.5):
    """Bölüm 8'deki stand; türetilen ölçüleri de döndürür."""
    et = 4
    on_pay = 10
    arka_pay = 15

    o = {"et": et, "aci": aci}
    o["genislik"] = round(0.9 * cihaz_genislik)
    o["sirt_boyu"] = round(0.6 * cihaz_yukseklik)
    o["dudak_yukseklik"] = max(10, cihaz_kalinlik + 3)
    o["yuva"] = (cihaz_kalinlik + bosluk) / math.sin(math.radians(aci))
    o["dudak_x"] = on_pay
    o["sirt_x"] = o["dudak_x"] + et + o["yuva"]
    izdusum = o["sirt_boyu"] * math.cos(math.radians(aci))
    o["taban_derinlik"] = o["sirt_x"] + izdusum + arka_pay

    taban = cq.Workplane("XY").box(
        o["taban_derinlik"], o["genislik"], et, centered=(False, True, False)
    )
    sirt = (
        cq.Workplane("XY")
        .box(et, o["genislik"], o["sirt_boyu"], centered=(False, True, False))
        .rotate((0, 0, 0), (0, 1, 0), 90 - aci)
        .translate((o["sirt_x"], 0, et))
    )
    dudak = (
        cq.Workplane("XY")
        .box(et, o["genislik"], et + o["dudak_yukseklik"],
             centered=(False, True, False))
        .translate((o["dudak_x"], 0, 0))
    )
    return taban.union(sirt).union(dudak), o


def cihaz_modeli(o, genislik, yukseklik, kalinlik):
    """Cihazı, sırtlığa yaslanmış ve tabana basmış hâlde modelleyen blok."""
    return (
        cq.Workplane("XY")
        .box(kalinlik, genislik, yukseklik, centered=(False, True, False))
        .translate((-kalinlik, 0, 0))
        .rotate((0, 0, 0), (0, 1, 0), 90 - o["aci"])
        .translate((o["sirt_x"], 0, o["et"]))
    )


def ortak_hacim(a, b):
    ortak = a.intersect(b)
    return ortak.val().Volume() if ortak.solids().size() else 0.0


def denetle(ad, cihaz, cihaz_kutle, **ayar):
    """Standı üretir; tarifteki her madde için bir denetim çalıştırır."""
    genislik, yukseklik, kalinlik = cihaz
    stand, o = stand_yap(genislik, yukseklik, kalinlik, **ayar)
    govde = stand.val()

    # 1. Tek ve geçerli bir katı mı?
    assert len(stand.solids().vals()) == 1, "Stand tek katı değil."
    assert govde.isValid(), "Stand geometrisi geçerli değil."

    # 2. Dış ölçüler beklenen değerlerde mi?
    k = govde.BoundingBox()
    assert abs(k.ylen - o["genislik"]) < 0.01, "Genişlik tutmuyor."
    assert abs(k.xlen - o["taban_derinlik"]) < 0.01, "Derinlik tutmuyor."

    # 3. Cihaz yuvaya çakışmadan oturuyor mu?
    cihaz_blok = cihaz_modeli(o, genislik, yukseklik, kalinlik)
    cakisma = ortak_hacim(stand, cihaz_blok)
    assert cakisma < 0.01, f"Cihaz standla çakışıyor: {cakisma:.1f} mm3"

    # 4. Dudak cihazın önünde mi?
    cihaz_kutu = cihaz_blok.val().BoundingBox()
    assert o["dudak_x"] + o["et"] <= cihaz_kutu.xmin + 0.01, \
        "Dudak cihazın içinde kalıyor."

    # 5. Devrilme: ortak ağırlık merkezi tabanın üstünde mi?
    stand_kutle = govde.Volume() / 1000 * PLA_YOGUNLUK
    m_stand = cq.Shape.centerOfMass(govde)
    m_cihaz = cq.Shape.centerOfMass(cihaz_blok.val())
    toplam = stand_kutle + cihaz_kutle
    merkez_x = (stand_kutle * m_stand.x + cihaz_kutle * m_cihaz.x) / toplam
    arka_pay = o["taban_derinlik"] - merkez_x
    en_yakin = min(merkez_x, arka_pay)
    assert en_yakin >= 10, \
        f"Devrilme riski: ağırlık merkezi kenara {en_yakin:.1f} mm"

    print(f"{ad}: 5 denetim gecti | stand {stand_kutle:.0f} g | "
          f"arka pay {arka_pay:.1f} mm")
    return stand, cihaz_blok, o


if __name__ == "__main__":
    telefon = denetle("telefon", (75, 160, 9), cihaz_kutle=180)
    tablet = denetle("tablet", (180, 250, 8), cihaz_kutle=480, aci=70)
    cq.exporters.export(telefon[0], "stand_telefon.step")
    cq.exporters.export(tablet[0], "stand_tablet.step")
