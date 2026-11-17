"""Bükülmüş sac L braket ailesi: 3B model, açınım ve denetimler."""
import math

import cadquery as cq
import ezdxf
from cadquery.occ_impl.exporters.dxf import DxfDocument

# Eksenler: A kolu X boyunca yatar (Z = 0 ile kalınlık arası), B kolu Z
# boyunca yükselir (X = 0 ile kalınlık arası). Genişlik Y'de ortalıdır.
# A ve B, dış köşeden ölçülen kol boylarıdır.

# Atölye kuralları. Örnek değerlerdir; kendi atölyenizinkileri yazın.
KURALLAR = dict(
    k_faktoru=0.40,         # nötr eksenin yeri: 0 iç yüz, 0.5 kalınlık ortası
    bukum_delik_kat=2.0,    # delik kenarı - büküm başlangıcı >= kat x kalınlık
    kenar_delik_kat=1.5,    # delik merkezi - kolun ucu >= kat x çap
    yan_kenar_kat=1.5,      # delik merkezi - yan kenar >= kat x çap
    delik_aralik_kat=3.0,   # delik merkezleri arası >= kat x çap
    yogunluk=7.85 / 1000,   # çelik, g/mm3
)


def ad_uret(p):
    """Parametrelerden parça adı: BRK-A60-B40-G30-T2-D5.5-2x1"""
    return (f"BRK-A{p['kol_a']:g}-B{p['kol_b']:g}-G{p['genislik']:g}"
            f"-T{p['kalinlik']:g}-D{p['delik_cap']:g}"
            f"-{p['delik_a']}x{p['delik_b']}")


def delik_konumlari(kol, adet, p, kural=KURALLAR):
    """Delik merkezlerinin dış köşeden uzaklıkları. Sığmıyorsa ValueError."""
    t, r, d = p["kalinlik"], p["ic_yaricap"], p["delik_cap"]
    if adet == 0:
        return []
    bas = (r + t) + kural["bukum_delik_kat"] * t + d / 2
    son = kol - kural["kenar_delik_kat"] * d
    if son < bas:
        raise ValueError(
            f"{kol:g} mm'lik kola {d:g} mm delik sığmıyor "
            f"(uygun aralık {bas:.1f}-{son:.1f} mm)")
    if adet == 1:
        return [(bas + son) / 2]
    aralik = (son - bas) / (adet - 1)
    if aralik < kural["delik_aralik_kat"] * d:
        raise ValueError(
            f"{kol:g} mm'lik kola {adet} delik sığmıyor "
            f"(aralık {aralik:.1f} mm, "
            f"en az {kural['delik_aralik_kat'] * d:.1f})")
    return [bas + i * aralik for i in range(adet)]


def braket_yap(p, kural=KURALLAR):
    """3B braket ve hesaplanan ölçüler."""
    A, B, G = p["kol_a"], p["kol_b"], p["genislik"]
    t, r, d = p["kalinlik"], p["ic_yaricap"], p["delik_cap"]
    if G / 2 < kural["yan_kenar_kat"] * d:
        raise ValueError(f"{G:g} mm genişlik {d:g} mm delik için dar")
    xa = delik_konumlari(A, p["delik_a"], p, kural)
    zb = delik_konumlari(B, p["delik_b"], p, kural)

    rd = r + t      # dış yarıçap
    braket = (
        cq.Workplane("XZ")
        .moveTo(rd, 0).lineTo(A, 0).lineTo(A, t).lineTo(rd, t)
        .radiusArc((t, rd), r)           # iç büküm yayı
        .lineTo(t, B).lineTo(0, B).lineTo(0, rd)
        .radiusArc((rd, 0), -rd)         # dış büküm yayı
        .close()
        .extrude(G / 2, both=True)
    )
    if xa:
        braket = braket.cut(
            cq.Workplane("XY").pushPoints([(x, 0) for x in xa])
            .circle(d / 2).extrude(t))
    if zb:
        braket = braket.cut(
            cq.Workplane("YZ").pushPoints([(0, z) for z in zb])
            .circle(d / 2).extrude(t))
    return braket, dict(delik_a=xa, delik_b=zb)


def acinim(p, o, kural=KURALLAR):
    """Açınım ölçüleri. u ekseni A kolunun ucundan B kolunun ucuna gider."""
    A, B = p["kol_a"], p["kol_b"]
    t, r = p["kalinlik"], p["ic_yaricap"]
    bukme_payi = math.pi / 2 * (r + kural["k_faktoru"] * t)
    duz_a, duz_b = A - r - t, B - r - t
    boy = duz_a + bukme_payi + duz_b
    return dict(
        boy=boy, bukme_payi=bukme_payi,
        bukum_cizgisi=duz_a + bukme_payi / 2,
        delikler=[A - x for x in o["delik_a"]]
        + [boy - (B - z) for z in o["delik_b"]],
    )


def acinim_dxf(p, a, dosya):
    """Açınımı iki katmanlı DXF olarak yazar: KESIM ve BUKUM."""
    G, d = p["genislik"], p["delik_cap"]
    # Dikkat: center() çalışma düzleminin başlangıcını kaydırır ve DXF
    # o başlangıca göre yazılır. Dikdörtgen moveTo ile konumlanıyor.
    kesim = cq.Workplane("XY").moveTo(a["boy"] / 2, 0).rect(a["boy"], G)
    if a["delikler"]:
        kesim = kesim.add(
            cq.Workplane("XY").pushPoints([(u, 0) for u in a["delikler"]])
            .circle(d / 2))
    u = a["bukum_cizgisi"]
    bukum = cq.Workplane("XY").moveTo(u, -G / 2).lineTo(u, G / 2)
    dxf = DxfDocument()
    dxf.add_layer("KESIM", color=7)
    dxf.add_layer("BUKUM", color=1)
    dxf.add_shape(kesim, "KESIM")
    dxf.add_shape(bukum, "BUKUM")
    dxf.document.saveas(dosya)


def silindirler(sekil):
    """Silindir yüzler: (yüz, yarıçap, eksen yönü)."""
    liste = []
    for f in sekil.Faces():
        if f.geomType() == "CYLINDER":
            c = f._geomAdaptor().Cylinder()
            e = c.Axis().Direction()
            liste.append((f, c.Radius(), (e.X(), e.Y(), e.Z())))
    return liste


def denetle(p, braket, o, a, dxf_dosya, kural=KURALLAR):
    """Yedi denetim. Geçerse hacim (mm3) döner."""
    A, B, G = p["kol_a"], p["kol_b"], p["genislik"]
    t, r, d = p["kalinlik"], p["ic_yaricap"], p["delik_cap"]
    s = braket.val()

    # 1. Tek ve geçerli katı
    assert braket.solids().size() == 1 and s.isValid(), "Katı geçersiz"

    # 2. Dış ölçüler tablodaki gibi
    k = s.BoundingBox()
    for ad, olculen, istenen in (("A", k.xlen, A), ("G", k.ylen, G),
                                 ("B", k.zlen, B)):
        assert abs(olculen - istenen) < 0.01, \
            f"{ad}: {olculen:.2f} != {istenen}"

    # 3. Delik sayısı: ekseni Z olanlar A kolunda, X olanlar B kolunda
    sil = silindirler(s)
    delik_a = [f for f, rr, e in sil if abs(e[2]) > 0.99]
    delik_b = [f for f, rr, e in sil if abs(e[0]) > 0.99]
    assert len(delik_a) == p["delik_a"], "A kolunda delik sayısı yanlış"
    assert len(delik_b) == p["delik_b"], "B kolunda delik sayısı yanlış"

    # 4. Her delik büküme yeterince uzak: yüzler arası mesafe ölçülür
    ic_bukum = [f for f, rr, e in sil
                if abs(e[1]) > 0.99 and abs(rr - r) < 0.01][0]
    en_az = kural["bukum_delik_kat"] * t
    for f in delik_a + delik_b:
        m = f.distance(ic_bukum)
        assert m >= en_az - 0.01, f"Delik büküme {m:.2f} mm (en az {en_az})"

    # 5. Hacim korunumu: 3B hacim, kalınlık ortasından açılmış levhanın
    #    hacmine eşit olmalı (k faktöründen bağımsız bir sağlama)
    orta_boy = (A - r - t) + (B - r - t) + math.pi / 2 * (r + t / 2)
    delik_hacmi = (p["delik_a"] + p["delik_b"]) * math.pi * d * d / 4 * t
    beklenen = orta_boy * G * t - delik_hacmi
    assert abs(s.Volume() - beklenen) / beklenen < 0.001, \
        f"Hacim {s.Volume():.0f}, beklenen {beklenen:.0f}"

    # 6. Açınım dosyası geri okunur: katmanlar ve ölçüler
    msp = ezdxf.readfile(dxf_dosya).modelspace()
    kesim = [e for e in msp if e.dxf.layer == "KESIM"]
    bukum = [e for e in msp if e.dxf.layer == "BUKUM"]
    daire = [e for e in kesim if e.dxftype() == "CIRCLE"]
    assert len(daire) == p["delik_a"] + p["delik_b"], "DXF delik sayısı"
    assert len(bukum) == 1, "DXF'te büküm çizgisi tek olmalı"
    assert abs(bukum[0].dxf.start.x - a["bukum_cizgisi"]) < 0.01, \
        "DXF'te büküm çizgisi yanlış yerde"
    geri = cq.importers.importDXF(dxf_dosya, include=["KESIM"])
    g = geri.val().BoundingBox()
    assert abs(g.xmin) < 0.01, "DXF'te parça başlangıç noktasında değil"
    assert abs(g.xlen - a["boy"]) < 0.01, "DXF açınım boyu yanlış"
    assert abs(g.ylen - G) < 0.01, "DXF genişliği yanlış"

    # 7. Deliklerin kol ucuna uzaklığı bükümde değişmez: 3B modelden ölçülen
    #    uzaklıklar, DXF'ten okunan uzaklıklarla aynı olmalı
    uca_3b = sorted([k.xmax - f.Center().x for f in delik_a]
                    + [g.xlen - (k.zmax - f.Center().z) for f in delik_b])
    uca_dxf = sorted(e.dxf.center.x for e in daire)
    for u3, ud in zip(uca_3b, uca_dxf):
        assert abs(u3 - ud) < 0.01, \
            f"Delik açınımda kaymış: 3B {u3:.2f}, DXF {ud:.2f}"
    return s.Volume()
