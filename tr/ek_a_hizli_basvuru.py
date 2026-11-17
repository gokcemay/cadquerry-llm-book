import cadquery as cq

# --- Çalışma düzlemi ve eskiz ---
p = cq.Workplane("XY")                  # XY: Z'ye uzatır. "XZ" eksi Y'ye!
p = p.workplane(offset=5)               # düzlemi 5 mm yukarı taşı
p = p.center(10, 0)                     # başlangıcı kaydır (kalıcıdır)
p = p.rect(40, 20)                      # ya da .circle(r), .polygon(6, d)
p = cq.Workplane("XY").polyline([(0, 0), (30, 0), (0, 20)]).close()

# --- Katı üretmek ---
kutu = cq.Workplane("XY").box(40, 30, 10)            # ortalanmış kutu
kose = cq.Workplane("XY").box(40, 30, 10, centered=False)
sil = cq.Workplane("XY").circle(8).extrude(20)       # uzatma
iki = cq.Workplane("XZ").rect(10, 4).extrude(15, both=True)   # iki yöne
don = (cq.Workplane("XZ").polyline([(5, 0), (9, 0), (9, 12), (5, 12)])
       .close().revolve(360, (0, 0, 0), (0, 1, 0)))  # döndürme

# --- Boole işlemleri ---
birlesim = kutu.union(sil)
fark = kutu.cut(sil)
ortak = kutu.intersect(sil)

# --- Seçiciler ---
ust = kutu.faces(">Z")                  # en üstteki yüz; "<Z" en alttaki
dik = kutu.edges("|Z")                  # Z'ye paralel kenarlar (4)
yan = kutu.faces("#Z")                  # normali Z'ye dik yüzler (4)
ikinci = kutu.faces(">Z[-2]")           # üstten ikinci
birlikte = kutu.edges("|Z and >Y")      # ve / or / not ile birleştirme
bolge = kutu.edges(cq.selectors.BoxSelector((15, -20, -6), (25, 20, 6)))

# --- Değiştirmek ---
kavisli = kutu.edges("|Z").fillet(3)                 # kavis
pahli = kutu.faces(">Z").edges().chamfer(1)          # pah
delikli = kutu.faces(">Z").workplane().hole(6)       # boydan boya delik
havsali = (kutu.faces(">Z").workplane()
           .pushPoints([(-10, 0), (10, 0)]).cskHole(4.5, 9, 90))
ici_bos = kutu.faces(">Z").shell(-2)                 # üstü açık kabuk
yazili = (kutu.faces(">Z").workplane()
          .text("AD", 8, 0.8, combine=True))         # combine şart

# --- Çoğaltmak ---
izgara = (kutu.faces(">Z").workplane()
          .rarray(12, 10, 3, 2).hole(3))             # 3 x 2 ızgara
dairesel = (cq.Workplane("XY").circle(20).extrude(4).faces(">Z").workplane()
            .polarArray(14, 0, 360, 6).hole(3))      # çember üzerinde 6
ayna = kose.mirror("YZ", union=True)                 # union şart

# --- Etiket ---
etiketli = kutu.faces(">Z").tag("ust").faces("<Z").workplane()
geri = etiketli.faces(tag="ust")                     # etiketli duruma dön

# --- Ölçmek ---
s = havsali.val()
k = s.BoundingBox()
print("dis olculer:", k.xlen, k.ylen, k.zlen)
print("hacim:", round(s.Volume()), "| gecerli:", s.isValid())
print("kati:", havsali.solids().size(),
      "| koni yuz:", havsali.faces("%CONE").size())
cakisma = kutu.intersect(sil)
print("cakisma hacmi:", round(cakisma.val().Volume(), 1))

# --- Montaj ---
montaj = cq.Assembly()
montaj.add(kutu, name="kutu", color=cq.Color(0.9, 0.8, 0.3))
montaj.add(sil, name="pim", loc=cq.Location((0, 0, 10)))

# --- Dışa aktarmak ---
cq.exporters.export(havsali, "parca.step")
cq.exporters.export(havsali, "parca.stl", tolerance=0.05,
                    angularTolerance=0.2)
cq.exporters.exportDXF(kutu.section(), "parca.dxf")   # kesitin yüksekliği!
montaj.export("montaj.step")
geri_okunan = cq.importers.importStep("parca.step")
