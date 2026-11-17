import cadquery as cq

# Kulaklık askısını seçilen baskı yönüne çevirir ve tablaya oturtur.
# Dilimleme programı dosyayı doğru yönde açar.

aski = cq.importers.importStep("kulaklik_askisi.step")

# X ekseni yukarı gelecek biçimde çevir: profil tablaya yatar
yatik = aski.rotate((0, 0, 0), (0, 1, 0), -90)

# Tablaya oturt: en alt nokta Z = 0
alt = yatik.val().BoundingBox().zmin
yatik = yatik.translate((0, 0, -alt))

k = yatik.val().BoundingBox()
print("baski olculeri:", round(k.xlen, 1), round(k.ylen, 1), round(k.zlen, 1))
print("en alt nokta:", round(k.zmin, 3))

cq.exporters.export(yatik, "kulaklik_askisi_baski.stl",
                    tolerance=0.05, angularTolerance=0.2)
