import cadquery as cq


def kutu_yap(uzunluk, genislik, yukseklik, yazi="",
             et=2, kose_kavis=6, bosluk=0.3, ayak_cap=8):
    """Kapaklı kutu üretir; (kutu, kapak) döndürür."""

    # --- Ölçüler birbiriyle tutarlı mı? ---
    if kose_kavis <= et + bosluk:
        raise ValueError(
            "Köşe kavisi, et kalınlığı ile boşluğun toplamından büyük olmalı.")
    if min(uzunluk, genislik) <= 2 * kose_kavis:
        raise ValueError(
            "Kutunun kısa kenarı, köşe kavisinin iki katından büyük olmalı.")
    if yukseklik <= 2 * et:
        raise ValueError(
            "Kutu, et kalınlığının iki katından yüksek olmalı.")
    if min(uzunluk, genislik) < 2 * kose_kavis + 2 * ayak_cap + 2:
        raise ValueError(
            "Kutu, dört ayağın yan yana sığması için çok dar.")

    # --- Sabit tutulan ayrıntılar ---
    kapak_kalinlik = 3
    dudak_yukseklik = 3
    ayak_yukseklik = 1.5

    # --- Girdilerden türetilen ölçüler ---
    ayak_kenar = kose_kavis + ayak_cap / 2    # ayak merkezinin kenara uzaklığı
    ic_uzunluk = uzunluk - 2 * et - 2 * bosluk
    ic_genislik = genislik - 2 * et - 2 * bosluk
    ic_kavis = kose_kavis - et - bosluk
    yazi_boyu = genislik / 5           # yazı kutuyla birlikte büyür

    kutu = (
        cq.Workplane("XY")
        .box(uzunluk, genislik, yukseklik, centered=(True, True, False))
        .edges("|Z").fillet(kose_kavis)
        .faces(">Z").shell(-et)
        .faces("<Z").workplane()
        .rarray(uzunluk - 2 * ayak_kenar, genislik - 2 * ayak_kenar, 2, 2)
        .circle(ayak_cap / 2).extrude(ayak_yukseklik)
    )

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
    if yazi:
        kapak = (
            kapak.faces(">Z").workplane()
            .text(yazi, yazi_boyu, 0.6, combine=True)
        )

    return kutu, kapak


# --- Parça ailesi: ad, uzunluk, genişlik, yükseklik, kapak yazısı ---
boylar = [
    ("kucuk", 60, 40, 20, "M3"),
    ("orta", 80, 50, 30, "M4"),
    ("buyuk", 120, 80, 40, "M5"),
]

for ad, uzunluk, genislik, yukseklik, yazi in boylar:
    kutu, kapak = kutu_yap(uzunluk, genislik, yukseklik, yazi)
    yerinde = kapak.translate((0, 0, yukseklik))
    cakisma = kutu.intersect(yerinde).val().Volume()
    print(ad, kutu.val().isValid(), kapak.val().isValid(),
          len(kutu.solids().vals()), len(kapak.solids().vals()),
          round(cakisma, 3))
    cq.exporters.export(kutu, f"kutu_{ad}.step")
    cq.exporters.export(kapak, f"kapak_{ad}.step")
