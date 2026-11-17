import math
import cadquery as cq

# --- Ölçüler (mm) ---
genislik = 70            # standın genişliği
taban_derinlik = 80      # tabanın önden arkaya uzunluğu
et = 4                   # et kalınlığı
aci = 65                 # telefonun yatayla yaptığı açı (derece)
sirt_boyu = 90           # sırtlığın uzunluğu
telefon_kalinlik = 9     # telefonun kalınlığı
dudak_yukseklik = 12     # öndeki dudağın taban üstündeki yüksekliği
bosluk = 1.5             # telefonun rahat oturması için pay
sirt_x = 30              # sırtlığın tabana oturduğu yer (önden ölçü)

# --- Taban: düz bir levha ---
taban = cq.Workplane("XY").box(
    taban_derinlik, genislik, et, centered=(False, True, False)
)

# --- Sırtlık: dik bir levha, arkaya doğru yatırılıyor ---
sirt = (
    cq.Workplane("XY")
    .box(et, genislik, sirt_boyu, centered=(False, True, False))
    .rotate((0, 0, 0), (0, 1, 0), 90 - aci)
    .translate((sirt_x, 0, et))
)

# --- Dudak: telefonun öne kaymasını engelleyen küçük duvar ---
yuva = (telefon_kalinlik + bosluk) / math.sin(math.radians(aci))
dudak_x = sirt_x - yuva - et
dudak = (
    cq.Workplane("XY")
    .box(et, genislik, et + dudak_yukseklik, centered=(False, True, False))
    .translate((dudak_x, 0, 0))
)

# --- Üç parçayı tek katıda birleştir ---
stand = taban.union(sirt).union(dudak)

# --- Şarj kablosu için dudakta yarık ---
yarik_genislik = 14
yarik = (
    cq.Workplane("XY")
    .box(et + 2, yarik_genislik, dudak_yukseklik + 1, centered=(False, True, False))
    .translate((dudak_x - 1, 0, et))
)
stand = stand.cut(yarik)

# --- Dosyaya yaz ---
cq.exporters.export(stand, "telefon_standi.stl")
cq.exporters.export(stand, "telefon_standi.step")
