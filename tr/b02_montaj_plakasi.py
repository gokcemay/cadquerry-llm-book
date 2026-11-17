import cadquery as cq

# --- Ölçüler (mm) ---
uzunluk = 100
genislik = 60
kalinlik = 5
kose_yaricap = 8      # köşe kavisinin yarıçapı
delik_cap = 4.5       # vida deliğinin çapı
delik_kenar = 10      # delik merkezinin kenara uzaklığı
pah = 1

plaka = (
    cq.Workplane("XY")
    .rect(uzunluk, genislik)                 # eskiz: bir dikdörtgen
    .extrude(kalinlik)                       # uzatma: eskize kalınlık ver
    .edges("|Z").fillet(kose_yaricap)        # kavis: dört dik kenarı yuvarlat
    .faces(">Z").edges().chamfer(pah)        # pah: üst yüzün kenarlarını kır
    .faces(">Z").workplane()                 # üst yüze geç
    .rect(uzunluk - 2 * delik_kenar, genislik - 2 * delik_kenar,
          forConstruction=True)              # yardımcı dikdörtgen
    .vertices().hole(delik_cap)              # delik: dört köşe noktasına
)

cq.exporters.export(plaka, "montaj_plakasi.step")
cq.exporters.export(plaka, "montaj_plakasi.stl")
