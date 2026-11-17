import math
import cadquery as cq


def stand_yap(cihaz_genislik, cihaz_yukseklik, cihaz_kalinlik, aci=65):
    """Cihazın ölçülerinden masaüstü stand üretir."""

    # --- Sabitler: üretim ve kullanım kuralları ---
    et = 4                  # et kalınlığı
    bosluk = 1.5            # cihazın yuvaya rahat girmesi için pay
    on_pay = 10             # dudağın önünde kalan taban
    arka_pay = 15           # sırtlığın arkasında kalan taban

    # --- Türetilen ölçüler ---
    genislik = round(0.9 * cihaz_genislik)      # stand cihazdan biraz dar
    sirt_boyu = round(0.6 * cihaz_yukseklik)    # sırtlık cihazın yüzde 60'ı
    dudak_yukseklik = max(10, cihaz_kalinlik + 3)
    yuva = (cihaz_kalinlik + bosluk) / math.sin(math.radians(aci))
    dudak_x = on_pay
    sirt_x = dudak_x + et + yuva
    sirt_izdusum = sirt_boyu * math.cos(math.radians(aci))
    taban_derinlik = sirt_x + sirt_izdusum + arka_pay

    taban = cq.Workplane("XY").box(
        taban_derinlik, genislik, et, centered=(False, True, False)
    )
    sirt = (
        cq.Workplane("XY")
        .box(et, genislik, sirt_boyu, centered=(False, True, False))
        .rotate((0, 0, 0), (0, 1, 0), 90 - aci)
        .translate((sirt_x, 0, et))
    )
    dudak = (
        cq.Workplane("XY")
        .box(et, genislik, et + dudak_yukseklik, centered=(False, True, False))
        .translate((dudak_x, 0, 0))
    )
    return taban.union(sirt).union(dudak)


telefon_standi = stand_yap(75, 160, 9)
tablet_standi = stand_yap(180, 250, 8, aci=70)

for ad, stand in (("telefon", telefon_standi), ("tablet", tablet_standi)):
    k = stand.val().BoundingBox()
    print(ad, round(k.xlen, 1), round(k.ylen, 1), round(k.zlen, 1),
          len(stand.solids().vals()), stand.val().isValid())
    cq.exporters.export(stand, f"stand_{ad}.step")
