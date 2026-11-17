# Tarif Et, Tasarla / Describe It, Design It

**TR:** *Tarif Et, Tasarla: LLM ve CadQuery ile Parametrik CAD* kitabının kod deposu.
**EN:** Code repository of the book *Describe It, Design It: Parametric CAD with LLMs and CadQuery*.

Author / Yazar: Gökçe Mehmet Ay · License / Lisans: MIT

---

## Türkçe

Kitaptaki her kod listesi bu depoda çalıştırılabilir bir dosya olarak durur. İki sürüm vardır:

| Klasör | İçerik |
|---|---|
| `tr/` | Kitabın Türkçe kodu: Türkçe değişken adları, yorumlar ve hata mesajları |
| `en/` | Aynı kodun İngilizce çevirisi: değişken adları, yorumlar, mesajlar ve dosya adları |

İki sürüm aynı geometriyi üretir. Çevirideki tek fark, kapak üzerindeki yazıların dilidir
(`VİDALAR` → `SCREWS`, `UYDU` → `SAT`, `KLİMA` → `AC`); bu yüzden Bölüm 7'deki kapağın hacmi
yaklaşık 5 mm³ farklı çıkar.

### Kurulum

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Kod, CadQuery 2.8.0 ve Python 3.13 ile sınanmıştır; daha eski Python sürümleri denenmedi.

### Çalıştırma

Betikleri kendi klasörlerinin içinden çalıştırın; Bölüm 16 ve 17 `araclar/` klasörünü göreli yolla bulur.

```bash
cd tr
python b05_duvar_askisi.py
python araclar/olc.py b05_duvar_askisi.py aski     # ölçüm raporu
```

Bazı betikler öncekinin çıktısını okur: `b09`, `b06`'nın STEP dosyasını; `b15_*`, `b12_kulaklik_askisi.py`'nin
STEP dosyasını kullanır. Önce onları çalıştırın.

Tüm örnekleri tek komutla sınamak için: `python run_all.py tr` (ya da `en`). Betikler geçici bir kopyada çalışır;
depoya dosya yazılmaz. `b12_turlar/tur1.py` ve `tur5.py`'nin **hata vermesi beklenir**: kitabın anlattığı
başarısız denemelerdir.

Pencere açan betikler (`b04_*`, `araclar/goruntule.py`) ekran gerektirir; `run_all.py` onları atlar.

### Dosya haritası

| Bölüm | `tr/` | `en/` |
|---|---|---|
| 1 | `b01_telefon_standi*.py` | `ch01_phone_stand*.py` |
| 2 | `b02_montaj_plakasi.py`, `b02_pul.py` | `ch02_mounting_plate.py`, `ch02_washer.py` |
| 3 | `b03_blok.py` | `ch03_block.py` |
| 4 | `b04_*.py` | `ch04_*.py` |
| 5 | `b05_duvar_askisi.py` | `ch05_wall_hook.py` |
| 6 | `b06_duvar_askisi_v2.py` | `ch06_wall_hook_v2.py` |
| 7 | `b07_kapakli_kutu.py` | `ch07_lidded_box.py` |
| 8 | `b08_kutu_ailesi.py`, `b08_stand_parametrik.py` | `ch08_box_family.py`, `ch08_parametric_stand.py` |
| 9 | `b09_aski_montaji.py` | `ch09_hook_assembly.py` |
| 10 | `b10_belirsiz_tarif.py` | `ch10_ambiguous_prompt.py` |
| 11 | `b11_kablo_klipsi.py`, `b11_uc_tarif.py` | `ch11_cable_clip.py`, `ch11_three_prompts.py` |
| 12 | `b12_kulaklik_askisi.py`, `b12_turlar/` | `ch12_headphone_hanger.py`, `ch12_iterations/` |
| 13 | `b13_bosluk_mastari.py`, `b13_stand_dogrulama.py` | `ch13_clearance_gauge.py`, `ch13_stand_verification.py` |
| 14–15 | `araclar/`, `b15_*.py` | `tools/`, `ch15_*.py` |
| 16 | `b16_kumanda_standi.py` | `ch16_remote_stand.py` |
| 17 | `b17_elektronik_kutusu.py` | `ch17_electronics_enclosure.py` |
| 18 | `b18_braket_ailesi/` | `ch18_bracket_family/` |
| Ek A | `ek_a_hizli_basvuru.py` | `appendix_a_quick_reference.py` |

### Önemli not

Hiçbir parça fiziksel olarak basılmadı, kesilmedi ya da bükülmedi. Kod, geometrik denetimlerle (çakışma, hacim,
ölçü, DXF'i geri okuma) sınanmıştır; baskı yönü, malzeme ve atölye değerleri örnektir. Kendi yazıcınızın,
lazerinizin ya da büküm tezgâhınızın değerleriyle değiştirin.

---

## English

Every code listing in the book is a runnable file in this repository. There are two versions:

| Folder | Contents |
|---|---|
| `tr/` | The book's Turkish code: Turkish identifiers, comments and error messages |
| `en/` | The same code translated to English: identifiers, comments, messages and file names |

Both versions build the same geometry. The only difference is the language of the lid text
(`VİDALAR` → `SCREWS`, `UYDU` → `SAT`, `KLİMA` → `AC`), so the Chapter 7 lid differs in volume by about 5 mm³.

### Setup

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

The code was tested with CadQuery 2.8.0 on Python 3.13; older Python versions were not tried.

### Running

Run scripts from inside their own folder; Chapters 16 and 17 locate `tools/` by relative path.

```bash
cd en
python ch05_wall_hook.py
python tools/measure.py ch05_wall_hook.py hook     # measurement report
```

Some scripts read the output of an earlier one: `ch09` needs the STEP file from `ch06`, and `ch15_*` need the
STEP file from `ch12_headphone_hanger.py`. Run those first.

To smoke-test every example at once: `python run_all.py en` (or `tr`). Scripts run in a temporary copy, so nothing
is written into the repository. `ch12_iterations/iteration1.py` and `iteration5.py` are **expected to fail**: they
are the failed attempts the book walks through (a method that does not exist; a fillet that is too large).

Scripts that open a window (`ch04_*`, `tools/view.py`) need a display and are skipped by `run_all.py`.

### Tools

| Tool | What it does |
|---|---|
| `tools/measure.py` | Size, volume, mass, face types and circle centres of a part |
| `tools/view.py` | Four views of a part in one PNG |
| `tools/print_orientation.py` | For six orientations: print height, bed contact and area needing support |

### Chapter 18: bracket family

```bash
cd en/ch18_bracket_family
python batch_build.py table.csv delivery
```

Reads `table.csv` (28 rows), builds one bent L bracket per row (STEP, flat-pattern DXF, dimension sheet), runs
seven checks on each and zips the result. Expected outcome: 24 built, 3 rule violations, 1 duplicate.
Rule violations (`ValueError`) mean the *table* is wrong; failed checks (`AssertionError`) would mean the *code* is wrong.

### Important note

Nothing here has been physically printed, cut or bent. The code was verified with geometric checks (overlap, volume,
dimensions, reading the DXF back); print orientation, material and workshop values are examples. Replace them with
the values of your own printer, laser cutter or press brake.

## License

MIT. See `LICENSE`.
