import cadquery as cq

# Eksenler: X masa kenarı boyunca, Y masanın içinden kenarına doğru,
# Z yukarı.
# Masanın üst yüzü Z = 0, masanın kenarı Y = 0.

# --- Girdiler (mm) ---
masa_kalinlik = 25
kablo_cap = 5
kablo_adet = 2

# --- Sabitler ---
genislik = 20          # klipsin masa kenarı boyunca eni
et = 3                 # et kalınlığı
cene_boyu = 30         # çenelerin masanın içine uzanması
sikma = 0.5            # çene aralığı masadan bu kadar dar
kanal_payi = 1.0       # kanal çapı kablodan bu kadar büyük
giris_daralma = 1.5    # giriş, kanal çapından bu kadar dar
blok_boyu = 15         # kablo bloğunun Y yönündeki boyu
kose_kavis = 2         # çenelerin iç köşelerindeki kavis
kenar_boslugu = kose_kavis     # sırt, masa kenarından bu kadar açıkta
giris_pahi = 1.5       # alt çenenin ucundaki pah

# --- Türetilen ölçüler ---
cene_araligi = masa_kalinlik - sikma
kanal_cap = kablo_cap + kanal_payi
giris_eni = kanal_cap - giris_daralma
blok_yukseklik = kanal_cap + 4
kanal_z = et + blok_yukseklik / 2
kanal_araligi = genislik / kablo_adet

# --- 1. adım: gövde (yandan görünüş profili uzatılır) ---
ust = et + blok_yukseklik
sirt_ic = kenar_boslugu            # sırtın masaya bakan yüzü
sirt_dis = kenar_boslugu + et      # sırtın dış yüzü
profil = [
    (-cene_boyu, 0), (sirt_ic, 0), (sirt_ic, -cene_araligi),
    (-cene_boyu, -cene_araligi), (-cene_boyu, -cene_araligi - et),
    (sirt_dis, -cene_araligi - et), (sirt_dis, ust),
    (sirt_dis - blok_boyu, ust), (sirt_dis - blok_boyu, et), (-cene_boyu, et),
]
klips = (
    cq.Workplane("YZ").polyline(profil).close()
    .extrude(genislik / 2, both=True)
)

# --- 2. adım: kablo kanalları ve üstten girişleri ---
merkezler = [((i + 0.5) * kanal_araligi - genislik / 2, kanal_z)
             for i in range(kablo_adet)]
# Sırtın dış yüzünde bir çalışma düzlemi
dis_yuz = cq.Workplane("XZ").workplane(offset=-sirt_dis)
kanallar = (
    dis_yuz.pushPoints(merkezler).circle(kanal_cap / 2).extrude(blok_boyu)
)
giris_yuk = ust - kanal_z + 1
girisler = (
    dis_yuz.pushPoints([(x, z + giris_yuk / 2) for x, z in merkezler])
    .rect(giris_eni, giris_yuk).extrude(blok_boyu)
)
klips = klips.cut(kanallar).cut(girisler)

# --- 3. adım: iç köşe kavisleri (2 kenar), çene ucunda pah (1 kenar) ---
ic_koseler = (
    cq.selectors.BoxSelector((-genislik, sirt_ic - 1, -1),
                             (genislik, sirt_ic + 1, 1))
    + cq.selectors.BoxSelector((-genislik, sirt_ic - 1, -cene_araligi - 1),
                               (genislik, sirt_ic + 1, -cene_araligi + 1))
)
klips = klips.edges(ic_koseler).fillet(kose_kavis)
cene_ucu = cq.selectors.BoxSelector(
    (-genislik, -cene_boyu - 1, -cene_araligi - 1),
    (genislik, -cene_boyu + 1, -cene_araligi + 1),
)
klips = klips.edges(cene_ucu).chamfer(giris_pahi)

# --- Ölç ve kaydet ---
k = klips.val().BoundingBox()
print("dis olculer:", round(k.xlen, 2), round(k.ylen, 2), round(k.zlen, 2))
print("hacim:", round(klips.val().Volume()))
print("kati sayisi:", len(klips.solids().vals()),
      "gecerli:", klips.val().isValid())
print("cene araligi:", cene_araligi, "kanal capi:", kanal_cap,
      "giris eni:", giris_eni)

cq.exporters.export(klips, "kablo_klipsi.step")
cq.exporters.export(klips, "kablo_klipsi.stl",
                    tolerance=0.05, angularTolerance=0.2)
