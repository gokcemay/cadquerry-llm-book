import sys

import cadquery as cq

sys.path.insert(0, "araclar")
import baski_yonu  # noqa: E402  (Bölüm 15'teki destek aracı)

# Eksenler kartın eksenleridir: kartın sol alt köşesi X = 0, Y = 0.
# X kartın uzunluğu, Y genişliği boyunca; Z yukarı. Kutunun altı Z = 0.

# --- Girdi: kartın ölçü çizimi (mm) ---
# Konnektör: kenar hangi kart kenarında; konum o kenar boyunca merkezin
# yeri (X ya da Y); en ve yukseklik gövdenin dışarıdan görünen ölçüsü;
# alt, gövdenin kart üst yüzünden yüksekliği.
SENSOR_KARTI = dict(
    ad="sensor_karti",
    uzunluk=80, genislik=50, kalinlik=1.6,
    delikler=[(4, 4), (76, 4), (4, 46), (76, 46)], delik_cap=3.2,
    alt_bosluk=5,          # kartın altındaki en uzun bacak, lehim
    ust_yukseklik=15,      # kartın üstündeki en yüksek eleman
    konnektorler=[
        dict(ad="USB", kenar="-X", konum=15, en=9, yukseklik=3.5, alt=0),
        dict(ad="guc", kenar="-X", konum=36, en=9, yukseklik=11, alt=0),
        dict(ad="klemens", kenar="+Y", konum=55, en=21, yukseklik=10,
             alt=0),
    ],
)

ROLE_KARTI = dict(
    ad="role_karti",
    uzunluk=62, genislik=38, kalinlik=1.6,
    delikler=[(3.5, 3.5), (58.5, 3.5), (3.5, 34.5), (58.5, 34.5)],
    delik_cap=3.2,
    alt_bosluk=4,
    ust_yukseklik=19,
    konnektorler=[
        dict(ad="klemens", kenar="+X", konum=19, en=16, yukseklik=10,
             alt=0),
        dict(ad="pin", kenar="-X", konum=19, en=11, yukseklik=9, alt=0),
    ],
)


def kutu_bloku(x0, x1, y0, y1, z0, z1):
    """Köşeleri verilen dikdörtgen blok."""
    return (
        cq.Workplane("XY")
        .box(x1 - x0, y1 - y0, z1 - z0, centered=False)
        .translate((x0, y0, z0))
    )


def konnektor_bloku(kart, k, z_kart_ust, pay=0.0, disari=0.0, iceri=8.0):
    """Konnektörün yerini tutan blok.

    pay: her yandan büyütme. disari: kart kenarından dışarı uzama.
    """
    z0 = z_kart_ust + k["alt"] - pay
    z1 = z_kart_ust + k["alt"] + k["yukseklik"] + pay
    a, b = k["konum"] - k["en"] / 2 - pay, k["konum"] + k["en"] / 2 + pay
    L, W = kart["uzunluk"], kart["genislik"]
    if k["kenar"] == "-X":
        return kutu_bloku(-disari, iceri, a, b, z0, z1)
    if k["kenar"] == "+X":
        return kutu_bloku(L - iceri, L + disari, a, b, z0, z1)
    if k["kenar"] == "-Y":
        return kutu_bloku(a, b, -disari, iceri, z0, z1)
    if k["kenar"] == "+Y":
        return kutu_bloku(a, b, W - iceri, W + disari, z0, z1)
    raise ValueError(f"Bilinmeyen kenar: {k['kenar']}")


def kutu_yap(kart, et=2.0, taban_kal=2.0, kapak_kal=2.0, kart_payi=0.5,
             pencere_payi=0.5, gecme_payi=0.2, dudak=4.0, dudak_et=1.6,
             kule_cap=7.0, vida_delik=2.5, ust_bosluk=1.0,
             centik_en=12.0):
    """Karttan kutu üretir: (taban, kapak, ölçüler)."""
    L, W = kart["uzunluk"], kart["genislik"]
    z_kart_alt = taban_kal + kart["alt_bosluk"]
    z_kart_ust = z_kart_alt + kart["kalinlik"]
    z_ust = z_kart_ust + kart["ust_yukseklik"] + ust_bosluk   # duvar üstü
    ic = (-kart_payi, L + kart_payi, -kart_payi, W + kart_payi)
    dis = (ic[0] - et, ic[1] + et, ic[2] - et, ic[3] + et)

    # Pencereler dudağın altında kalmalı; yoksa kapak konnektöre biner
    for k in kart["konnektorler"]:
        ust = z_kart_ust + k["alt"] + k["yukseklik"] + pencere_payi
        if ust > z_ust - dudak:
            raise ValueError(f"{k['ad']} penceresi kapak dudağına değiyor")

    # --- Taban: dış blok, iç boşluk ---
    taban = (
        kutu_bloku(dis[0], dis[1], dis[2], dis[3], 0, z_ust)
        .edges("|Z").fillet(3)
        .faces("<Z").edges().chamfer(0.6)
    )
    bosluk = kutu_bloku(ic[0], ic[1], ic[2], ic[3], taban_kal, z_ust)
    taban = taban.cut(bosluk)

    # --- Vida kuleleri: her montaj deliğinin altında ---
    kuleler = (
        cq.Workplane("XY").workplane(offset=taban_kal)
        .pushPoints(kart["delikler"]).circle(kule_cap / 2)
        .extrude(kart["alt_bosluk"])
    )
    delikler = (
        cq.Workplane("XY").workplane(offset=taban_kal)
        .pushPoints(kart["delikler"]).circle(vida_delik / 2)
        .extrude(kart["alt_bosluk"])
    )
    taban = taban.union(kuleler).cut(delikler)

    # --- Konnektör pencereleri: duvarı boydan boya keser ---
    for k in kart["konnektorler"]:
        pencere = konnektor_bloku(kart, k, z_kart_ust, pay=pencere_payi,
                                  disari=kart_payi + et + 1, iceri=1)
        taban = taban.cut(pencere)

    # --- Tırnak çentiği: kapağı açmak için ön duvarın üst kenarında ---
    centik = kutu_bloku(L / 2 - centik_en / 2, L / 2 + centik_en / 2,
                        dis[2] - 1, ic[2], z_ust - 1.5, z_ust)
    taban = taban.cut(centik)

    # --- Kapak: levha + duvarların içine giren dudak ---
    kapak = (
        kutu_bloku(dis[0], dis[1], dis[2], dis[3], z_ust, z_ust + kapak_kal)
        .edges("|Z").fillet(3)
        .faces(">Z").edges().chamfer(0.6)
    )
    g = gecme_payi
    dudak_dis = kutu_bloku(ic[0] + g, ic[1] - g, ic[2] + g, ic[3] - g,
                           z_ust - dudak, z_ust)
    d = g + dudak_et
    dudak_ic = kutu_bloku(ic[0] + d, ic[1] - d, ic[2] + d, ic[3] - d,
                          z_ust - dudak, z_ust)
    kapak = kapak.union(dudak_dis.cut(dudak_ic))

    # --- Havalandırma: kapakta, kartın üstünde yarıklar ---
    yarik_boy = W * 0.5
    adet = max(int((L * 0.6) // 5), 1)
    yariklar = (
        cq.Workplane("XY").workplane(offset=z_ust)
        .center(L / 2, W / 2).rarray(5, 1, adet, 1)
        .rect(2, yarik_boy).extrude(kapak_kal)
    )
    kapak = kapak.cut(yariklar)

    o = dict(z_kart_alt=z_kart_alt, z_kart_ust=z_kart_ust, z_ust=z_ust,
             et=et, kart_payi=kart_payi, pencere_payi=pencere_payi,
             gecme_payi=gecme_payi, vida_delik=vida_delik, yarik=adet,
             on_dis=dis[2], on_ic=ic[2])
    return taban, kapak, o


def kart_modeli(kart, o, disari=5.0):
    """Kartın yerini tutan model: levha, eleman hacmi, konnektörler.

    Konnektörler kart kenarından dışarı uzatılır; pencere yanlış yerdeyse
    uzantı duvara çarpar.
    """
    L, W = kart["uzunluk"], kart["genislik"]
    model = kutu_bloku(0, L, 0, W, o["z_kart_alt"], o["z_kart_ust"])
    # Elemanların kaplayabileceği hacim: kenarlardan 2 mm içeride
    model = model.union(kutu_bloku(
        2, L - 2, 2, W - 2,
        o["z_kart_ust"], o["z_kart_ust"] + kart["ust_yukseklik"]))
    for k in kart["konnektorler"]:
        model = model.union(
            konnektor_bloku(kart, k, o["z_kart_ust"], disari=disari))
    # Montaj delikleri
    delik = (
        cq.Workplane("XY").pushPoints(kart["delikler"])
        .circle(kart["delik_cap"] / 2).extrude(o["z_ust"] + 5)
    )
    return model.cut(delik)


def ortak_hacim(a, b):
    ortak = a.intersect(b)
    return ortak.val().Volume() if ortak.solids().size() else 0.0


def denetle(kart, **ayar):
    taban, kapak, o = kutu_yap(kart, **ayar)
    model = kart_modeli(kart, o)

    # 1. İki parça da tek ve geçerli katı
    for ad, p in (("taban", taban), ("kapak", kapak)):
        assert p.solids().size() == 1, f"{ad} tek parça değil"
        assert p.val().isValid(), f"{ad} geçerli değil"

    # 2. Kart, konnektör uzantılarıyla birlikte tabana çarpmadan oturur
    v = ortak_hacim(taban, model)
    assert v < 0.01, f"Kart tabanla çakışıyor: {v:.1f} mm3"

    # 3. Kart kulelere oturur: 0,1 mm aşağı itilince her kuleye değer
    for x, y in kart["delikler"]:
        kule_ustu = kutu_bloku(x - 4, x + 4, y - 4, y + 4,
                               o["z_kart_alt"] - 0.1, o["z_kart_alt"])
        assert ortak_hacim(taban, kule_ustu) > 1, \
            f"({x}, {y}) altında kule yok"

    # 4. Vidalar: her delikten inen 2,4 mm'lik pim hiçbir şeye çarpmaz
    for x, y in kart["delikler"]:
        pim = (
            cq.Workplane("XY").workplane(offset=o["z_kart_alt"] - 4)
            .center(x, y).circle(1.2).extrude(4 + kart["kalinlik"])
        )
        v = ortak_hacim(taban, pim) + ortak_hacim(model, pim)
        assert v < 0.01, f"({x}, {y}) vidası yolunda engel var: {v:.2f} mm3"

    # 5. Kapak kapanır: tabana ve karta çarpmaz
    assert ortak_hacim(taban, kapak) < 0.01, "Kapak tabanla çakışıyor"
    assert ortak_hacim(model, kapak) < 0.01, "Kapak karta değiyor"

    # 6. Geçme payı: kapak yana paydan az itilince çarpmaz, fazla itilince
    #    çarpar
    g = o["gecme_payi"]
    assert ortak_hacim(taban, kapak.translate((g - 0.05, 0, 0))) < 0.01, \
        "Geçme payı beklenenden dar"
    assert ortak_hacim(taban, kapak.translate((g + 0.05, 0, 0))) > 0.01, \
        "Geçme payı beklenenden bol"

    # 7. Baskı: tabanda yalnızca pencere üstleri köprüdür; kapak baş aşağı
    #    desteksiz basılır
    kopru = sum((k["en"] + 2 * o["pencere_payi"]) * o["et"]
                for k in kart["konnektorler"])
    _, _, destek = baski_yonu.yon_raporu(taban.val())
    assert abs(destek - kopru) < 1, \
        f"Tabanda beklenmeyen destek: {destek:.0f} mm2 (köprü {kopru:.0f})"
    ters = baski_yonu.cevir(kapak.val(), "-Z yukari (bas asagi)")
    _, _, destek = baski_yonu.yon_raporu(ters)
    assert destek < 1, f"Kapak destek istiyor: {destek:.0f} mm2"

    # 8. Kapak açılabilir: çentikten giren düz bir uç tabana çarpmaz ve
    #    kapak levhasının altına ulaşır
    L = kart["uzunluk"]
    uc = kutu_bloku(L / 2 - 4, L / 2 + 4, o["on_dis"] - 5, o["on_ic"],
                    o["z_ust"] - 1.2, o["z_ust"] - 0.2)
    assert ortak_hacim(taban, uc) < 0.01, \
        "Çentik kapalı: uç tabana çarpıyor"
    ustu = kutu_bloku(L / 2 - 4, L / 2 + 4, o["on_dis"], o["on_ic"],
                      o["z_ust"], o["z_ust"] + 0.5)
    assert ortak_hacim(kapak, ustu) > 1, "Çentiğin üstünde kapak yok"

    t, k = taban.val().BoundingBox(), kapak.val().BoundingBox()
    en_uzun = max(kn["en"] + 2 * o["pencere_payi"]
                  for kn in kart["konnektorler"])
    print(f"{kart['ad']}: 8 denetim gecti | dis olculer "
          f"{t.xlen:.1f} x {t.ylen:.1f} x {k.zmax:.1f} mm | "
          f"en uzun kopru {en_uzun:.0f} mm | {o['yarik']} yarik")
    return taban, kapak, o


if __name__ == "__main__":
    for kart in (SENSOR_KARTI, ROLE_KARTI):
        taban, kapak, o = denetle(kart)
        cq.exporters.export(taban, f"{kart['ad']}_taban.step")
        cq.exporters.export(kapak, f"{kart['ad']}_kapak.step")
