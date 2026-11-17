"""tablo.csv'deki her satırdan bir braket üretir, denetler ve paketler.

Kullanım: python toplu_uret.py tablo.csv teslim
"""
import csv
import os
import shutil
import sys
import time

import cadquery as cq

import braket as b
import foy

TAMSAYI = ("delik_a", "delik_b")


def satir_oku(satir):
    return {k: (int(v) if k in TAMSAYI else float(v))
            for k, v in satir.items()}


def uret(p, klasor):
    """Tek bir braket: model, açınım, denetim, dosyalar. Özet satırı döner."""
    ad = b.ad_uret(p)
    braket, o = b.braket_yap(p)                 # kural ihlali: ValueError
    a = b.acinim(p, o)
    hedef = os.path.join(klasor, ad)
    os.makedirs(hedef, exist_ok=True)
    govde = os.path.join(hedef, ad)
    b.acinim_dxf(p, a, govde + "_acinim.dxf")
    # Denetim başarısızsa AssertionError
    hacim = b.denetle(p, braket, o, a, govde + "_acinim.dxf")
    kutle = hacim * b.KURALLAR["yogunluk"]
    cq.exporters.export(braket, govde + ".step")
    foy.foy_ciz(p, ad, a, kutle, b.KURALLAR, govde + "_foy")
    return dict(ad=ad, durum="tamam", kutle_g=round(kutle, 1),
                acinim_boyu=round(a["boy"], 2),
                bukum_cizgisi=round(a["bukum_cizgisi"], 2), aciklama="")


def toplu_uret(tablo, klasor):
    shutil.rmtree(klasor, ignore_errors=True)
    os.makedirs(klasor)
    ozet, gorulen = [], set()
    with open(tablo, encoding="utf-8") as f:
        satirlar = [satir_oku(s) for s in csv.DictReader(f)]
    for no, p in enumerate(satirlar, start=2):      # 1. satır başlıktır
        ad = b.ad_uret(p)
        bos = dict(ad=ad, kutle_g="", acinim_boyu="", bukum_cizgisi="")
        if ad in gorulen:
            ozet.append(dict(bos, durum="yinelenen",
                             aciklama=f"satır {no}: aynı parça daha önce var"))
            continue
        gorulen.add(ad)
        try:
            ozet.append(uret(p, klasor))
        except ValueError as hata:
            shutil.rmtree(os.path.join(klasor, ad), ignore_errors=True)
            ozet.append(dict(bos, durum="kural",
                             aciklama=f"satır {no}: {hata}"))
        except AssertionError as hata:
            shutil.rmtree(os.path.join(klasor, ad), ignore_errors=True)
            ozet.append(dict(bos, durum="denetim",
                             aciklama=f"satır {no}: {hata}"))

    with open(os.path.join(klasor, "ozet.csv"), "w", newline="",
              encoding="utf-8") as f:
        yazici = csv.DictWriter(f, fieldnames=list(ozet[0]))
        yazici.writeheader()
        yazici.writerows(ozet)

    k = b.KURALLAR
    with open(os.path.join(klasor, "BENIOKU.txt"), "w", encoding="utf-8") as f:
        f.write(
            "L braket ailesi - teslim paketi\n"
            f"Tarih: {time.strftime('%Y-%m-%d')}\n\n"
            "Her parça klasöründe: STEP (bükülmüş hâli), açınım DXF "
            "(KESIM ve BUKUM katmanları),\nölçü föyü (PDF ve PNG).\n\n"
            f"Malzeme: çelik sac. Büküm: 90 derece, iç yarıçap = kalınlık.\n"
            f"Açınım k faktörü {k['k_faktoru']:g} ile hesaplandı; kendi "
            "tezgâhınızın değeri farklıysa bildirin.\n"
            "Ölçüler mm. Belirtilmeyen toleranslar atölye standardıdır.\n"
            "ozet.csv: üretilen ve üretilemeyen satırların listesi.\n"
            "tablo.csv: bu paketin üretildiği girdi tablosu.\n")
    # Paketin neyden üretildiği belli olsun: girdi tablosu da içine girer
    shutil.copy(tablo, os.path.join(klasor, "tablo.csv"))
    shutil.make_archive(klasor, "zip", klasor)
    return ozet


if __name__ == "__main__":
    basla = time.time()
    ozet = toplu_uret(sys.argv[1], sys.argv[2])
    for durum in ("tamam", "kural", "denetim", "yinelenen"):
        print(f"{durum}: {sum(1 for s in ozet if s['durum'] == durum)}")
    for s in ozet:
        if s["durum"] != "tamam":
            print(" ", s["ad"], "->", s["aciklama"])
    print(f"sure: {time.time() - basla:.0f} s")
