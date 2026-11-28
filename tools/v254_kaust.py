"""v2.54: research-partner corrections (28 Nov 2026).

1. Battery-recycling pilot: no "ultrasonic" anywhere; the process is called a
   "novel intensified process" (EN, fr-CA, es-MX, catalogues, IRA).
2. Cryogenic carbon capture pilot: the HMI screen is published with instrument,
   valve and line tags, live readings and selected equipment (three columns,
   three heat exchangers, cryo unit) blurred. New file name so caches refresh.

Run from the repo root:  python3 tools/v254_kaust.py <blurred.webp>
Edits built pages and catalogues in place (no i18n rebuild: see v2.53 note).
"""
import glob, hashlib, os, shutil, sys

OLD_IMG = 'b4ac85c345'

REPLACE = [
    # English (page text and catalogue keys)
    ('Ultrasonic Battery Recycling Pilot', 'Novel Intensified Battery Recycling Pilot'),
    ('Ultrasonic battery-recycling pilot', 'Novel intensified battery-recycling pilot'),
    ('an ultrasonically intensified battery-recycling process', 'a novel intensified battery-recycling process'),
    ('control of ultrasonic energy, temperature and flow', 'control of energy input, temperature and flow'),
    # French (Canada)
    ('recyclage de batteries par ultrasons pour la récupération',
     'recyclage de batteries par un procédé intensifié novateur pour la récupération'),
    ('recyclage de batteries par ultrasons', 'recyclage de batteries par procédé intensifié novateur'),
    ('un procédé de recyclage de batteries intensifié par ultrasons',
     'un procédé intensifié novateur de recyclage de batteries'),
    ('de l’énergie ultrasonore', 'de l’apport d’énergie'),
    # Spanish (Mexico)
    ('reciclaje de baterías por ultrasonido para recuperar',
     'reciclaje de baterías con un proceso intensificado novedoso para recuperar'),
    ('reciclaje de baterías por ultrasonido', 'reciclaje de baterías con proceso intensificado novedoso'),
    ('un proceso de reciclaje de baterías intensificado por ultrasonido',
     'un proceso intensificado novedoso de reciclaje de baterías'),
    ('de energía ultrasónica,', 'del aporte de energía,'),
    # IRA keyword
    ("['ultrasonic']", "['intensified']"),
    ('"ultrasonic"', '"intensified"'),
]


def main(blurred):
    data = open(blurred, 'rb').read()
    new_img = hashlib.md5(data).hexdigest()[:10]
    shutil.copyfile(blurred, f'assets/img/{new_img}.webp')
    if os.path.exists(f'assets/img/{OLD_IMG}.webp'):
        os.remove(f'assets/img/{OLD_IMG}.webp')
    files = [f for f in glob.glob('**/*', recursive=True)
             if f.endswith(('.html', '.json', '.py', '.csv')) and '/packs/' not in f
             and not f.endswith('v254_kaust.py')]
    changed = {}
    for f in files:
        s = open(f, encoding='utf-8', newline='').read()
        t = s
        for a, b in REPLACE:
            t = t.replace(a, b)
        t = t.replace(f'assets/img/{OLD_IMG}.webp', f'assets/img/{new_img}.webp')
        if t != s:
            open(f, 'w', encoding='utf-8', newline='').write(t)
            changed[f] = 1
    print('image', new_img)
    print(len(changed), 'files changed')
    for f in sorted(changed):
        print(' ', f)


if __name__ == '__main__':
    main(sys.argv[1])
