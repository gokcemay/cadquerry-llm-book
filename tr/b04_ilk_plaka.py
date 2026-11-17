import cadquery as cq
from cadquery.vis import show

# --- Ölçüler (mm) ---
uzunluk = 60
genislik = 40
kalinlik = 5
delik_cap = 10

# --- Plaka ve delik ---
plaka = (
    cq.Workplane("XY")
    .box(uzunluk, genislik, kalinlik)
    .faces(">Z").workplane()
    .hole(delik_cap)
)

# --- Dosyaya yaz ve göster ---
cq.exporters.export(plaka, "ilk_plaka.stl")
cq.exporters.export(plaka, "ilk_plaka.step")
show(plaka)
