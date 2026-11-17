"""Smoke test: runs every example in a copy of tr/ or en/ and reports the exit codes.

Usage:  python run_all.py en      (or: python run_all.py tr)

Scripts are run in book order inside a temporary copy, so the files they
produce (STEP, STL, DXF) never end up in the repository. Two scripts are
EXPECTED to fail: iteration 1 and iteration 5 of Chapter 12. They are the
failed attempts the book walks through (a method that does not exist, and
a fillet that is too large). Scripts that open a viewer (Chapter 4 and
tools/view.py) are skipped; they need a display.
"""
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))

ORDER = {
    "en": (
        ["ch01_phone_stand.py", "ch01_phone_stand_slotted.py",
         "ch02_mounting_plate.py", "ch02_washer.py", "ch03_block.py",
         "ch05_wall_hook.py", "ch06_wall_hook_v2.py", "ch07_lidded_box.py",
         "ch08_box_family.py", "ch08_parametric_stand.py",
         "ch09_hook_assembly.py", "ch10_ambiguous_prompt.py",
         "ch11_cable_clip.py", "ch11_three_prompts.py",
         "ch12_headphone_hanger.py"]
        + [f"ch12_iterations/iteration{i}.py" for i in range(1, 7)]
        + ["ch13_clearance_gauge.py", "ch13_stand_verification.py",
           "ch15_print_file.py", "ch15_test_sections.py",
           "ch15_laser_plate.py", "ch16_remote_stand.py",
           "ch17_electronics_enclosure.py", "appendix_a_quick_reference.py"],
        {"ch12_iterations/iteration1.py", "ch12_iterations/iteration5.py"},
        ("ch18_bracket_family", ["batch_build.py", "table.csv", "delivery"]),
    ),
    "tr": (
        ["b01_telefon_standi.py", "b01_telefon_standi_yarik.py",
         "b02_montaj_plakasi.py", "b02_pul.py", "b03_blok.py",
         "b05_duvar_askisi.py", "b06_duvar_askisi_v2.py",
         "b07_kapakli_kutu.py", "b08_kutu_ailesi.py",
         "b08_stand_parametrik.py", "b09_aski_montaji.py",
         "b10_belirsiz_tarif.py", "b11_kablo_klipsi.py", "b11_uc_tarif.py",
         "b12_kulaklik_askisi.py"]
        + [f"b12_turlar/tur{i}.py" for i in range(1, 7)]
        + ["b13_bosluk_mastari.py", "b13_stand_dogrulama.py",
           "b15_baski_dosyasi.py", "b15_deneme_kesitleri.py",
           "b15_lazer_plaka.py", "b16_kumanda_standi.py",
           "b17_elektronik_kutusu.py", "ek_a_hizli_basvuru.py"],
        {"b12_turlar/tur1.py", "b12_turlar/tur5.py"},
        ("b18_braket_ailesi", ["toplu_uret.py", "tablo.csv", "teslim"]),
    ),
}


def main(lang):
    scripts, expected_fail, (batch_dir, batch_args) = ORDER[lang]
    work = os.path.join(tempfile.mkdtemp(), lang)
    shutil.copytree(os.path.join(ROOT, lang), work)
    env = dict(os.environ, MPLBACKEND="Agg")
    failures = 0
    jobs = [(name, work, [name]) for name in scripts]
    # The batch script runs inside its own folder: <script> <table> <output dir>
    jobs.append((batch_dir + "/" + batch_args[0], os.path.join(work, batch_dir),
                 [batch_args[0], batch_args[1], batch_args[2]]))
    for name, cwd, args in jobs:
        script = os.path.join(cwd, args[0]) if cwd != work else os.path.join(work, args[0])
        r = subprocess.run([sys.executable, script] + args[1:], cwd=cwd,
                           env=env, capture_output=True, text=True)
        want_fail = name in expected_fail
        ok = (r.returncode != 0) if want_fail else (r.returncode == 0)
        failures += not ok
        note = " (expected to fail)" if want_fail else ""
        print(f"{'ok ' if ok else 'BAD'} {name}{note}")
        if not ok:
            print(r.stderr[-500:])
    print("\nall as expected" if not failures else f"\n{failures} unexpected result(s)")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ORDER:
        sys.exit("usage: python run_all.py en|tr")
    main(sys.argv[1])
