"""Analyse descriptive d'un export Tobii Pro Lab, sans métadonnées personnelles.

Usage : python scripts/analyse_tobii.py fichier.xlsx --output results/SUJ1
Les taux sont des proportions d'échantillons, pas des durées de fixation.
"""
import argparse
import csv
import json
import os
import tempfile
import unicodedata
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR', str(Path(tempfile.gettempdir())/'tobii-matplotlib'))
os.environ.setdefault('XDG_CACHE_HOME', str(Path(tempfile.gettempdir())/'tobii-cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import openpyxl

AOIS = {
    'FND (vidéo)': 'AOI hit [Recording 5 - FND]',
    'Écran principal (vidéo)': 'AOI hit [Recording 5 - Main screen]',
    'ML (vidéo)': 'AOI hit [Recording 5 - ML]',
    'ML (image mappée)': 'AOI hit [HLX FND1 - ML_HLX_FND1]',
}
COLORS = ['#22a6b3', '#4568b0', '#e5a23c', '#a16cc1']


def write_csv(path, rows, fields):
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def analyse(source, output, subject='SUJ1'):
    project = 2 if subject in {'SUJ5', 'SUJ6', 'SUJ7'} else 1
    aois = AOIS if project == 1 else {'ML (image mappée)': 'AOI hit [HLX FND - HLX_FND_ML]'}
    media = 'HLX FND1' if project == 1 else 'HLX FND'
    notes = {
        'SUJ1': {'ALERT_RED': 'Publicité signalée ; essai perturbé'},
        'SUJ2': {name: 'Hors champ signalé ; apparition non datable sur la vidéo'
                 for name in ['ALERT_ML_LARGE', 'ALERT_ML_LIGHT', 'ALERT_RED', 'ALERT_TEXT']},
        'SUJ3': {
            'ALERT_ML_LARGE': 'Hors champ selon les notes, mais marqueur présent : annotation à vérifier',
            'ALERT_ML_LIGHT': 'Hors champ puis apparition approximative signalés ; rejeu possible à vérifier',
            'ALERT_FND': 'Apparition approximative : visibilité incertaine selon les notes',
        },
        'SUJ5': {}, 'SUJ6': {}, 'SUJ7': {},
    }[subject]

    output.mkdir(parents=True, exist_ok=True)
    workbook = openpyxl.load_workbook(source, read_only=True, data_only=True)
    if len(workbook.worksheets) != 1:
        raise ValueError('Un seul enregistrement/une seule feuille attendu.')
    rows = workbook.active.values
    headers = tuple(unicodedata.normalize("NFKC", h) if isinstance(h, str) else h for h in next(rows))
    timestamp_without_unit = 'Recording timestamp [μs]' not in headers and 'Recording timestamp' in headers
    if timestamp_without_unit:
        headers = tuple('Recording timestamp [μs]' if h == 'Recording timestamp' else h for h in headers)
    declared_durations = set()
    required = {'Recording timestamp [μs]', 'Sensor', 'Event', 'Validity left',
                'Validity right', 'Participant name', 'Recording name', *aois.values()}
    if required - set(headers):
        raise ValueError(f'Colonnes manquantes : {sorted(required-set(headers))}')
    eye, events, mapping = [], [], []
    identities, recordings, projects = set(), set(), set()
    start = None
    duration = 0
    for row in rows:
        d = dict(zip(headers, row))
        identities.add(d['Participant name'])
        recordings.add(d['Recording name'])
        projects.add(d.get('Project name'))
        declared = d.get('Recording duration [ms]', d.get('Recording duration'))
        if declared is not None:
            declared_durations.add(float(declared))
        t = float(d['Recording timestamp [μs]']) / 1_000_000
        duration = max(duration, t)
        event = d.get('Event') or ''
        if event.upper().startswith('ALERT_'):
            events.append({'temps_s': t, 'alerte': event.upper(),
                           'reserve': notes.get(event.upper(), 'Apparition annotée manuellement par Élie')})
        if event == f'{media} IntervalStart':
            if start is not None:
                raise ValueError('Intervalles de mapping imbriqués.')
            start = t
        elif event == f'{media} IntervalEnd':
            if start is None or t < start:
                raise ValueError('Fin de mapping sans début valide.')
            mapping.append((start, t))
            start = None
        if d['Sensor'] == 'Eye Tracker':
            valid = d['Validity left'] == 'Valid' or d['Validity right'] == 'Valid'
            sample = {'temps_s': t, 'au_moins_un_oeil_valide': int(valid)}
            for label, column in aois.items():
                value = d.get(column)
                if value not in (None, -1, 0, 1):
                    raise ValueError(f'Valeur AOI inattendue : {value}')
                sample[label] = value if value in (0, 1) else None
            eye.append(sample)
    workbook.close()
    last_export_time = duration
    if timestamp_without_unit:
        if len(declared_durations) != 1:
            raise ValueError('Durée déclarée non unique ; unité temporelle indéterminée.')
        declared_s = next(iter(declared_durations)) / 1000
        if declared_s <= 0 or abs(duration-declared_s) > max(.002, .01*declared_s):
            raise ValueError('Unité temporelle non confirmée : écart supérieur à 1 % avec la durée déclarée.')
        duration = declared_s
    if start is not None or len(identities) != 1 or len(recordings) != 1 or not eye:
        raise ValueError('Export incomplet ou plusieurs sujets/enregistrements.')
    if identities != {subject} or projects != {f'Project{project}'}:
        raise ValueError('Sujet ou projet incompatible avec le profil attendu.')
    if not events:
        raise ValueError('Aucune annotation ALERT_ trouvée.')
    eye.sort(key=lambda x: x['temps_s'])
    events.sort(key=lambda x: x['temps_s'])
    times = np.array([r['temps_s'] for r in eye])
    valid = np.array([r['au_moins_un_oeil_valide'] for r in eye], dtype=bool)
    if np.any(np.diff(times) <= 0):
        raise ValueError('Horodatages oculaires dupliqués ou non croissants.')
    arrays = {k: np.array([np.nan if r[k] is None else r[k] for r in eye]) for k in aois}
    metrics = []
    for label, values in arrays.items():
        known = valid & np.isfinite(values)
        hits = known & (values == 1)
        metrics.append({'AOI': label, 'echantillons_valides_AOI_renseignee': int(known.sum()),
                        'echantillons_dans_AOI': int(hits.sum()),
                        'part_dans_AOI_pct': round(100*hits.sum()/known.sum(), 2) if known.any() else None,
                        'couverture_AOI_pct_echantillons_oculaires': round(100*known.mean(), 2)})
    summary = {'projet': project, 'aoi_source': aois, 'horodatage_sans_unite_verifie_par_duree': timestamp_without_unit, 'dernier_horodatage_export_s': last_export_time, 'duree_s': duration, 'echantillons_oculaires': len(eye),
               'au_moins_un_oeil_valide_pct': round(100*valid.mean(), 2),
               'pas_median_ms': round(1000*np.median(np.diff(times)), 3),
               'nombre_marqueurs_alerte': len(events), 'intervalles_mapping': mapping,
               'duree_intervalles_mapping_s': sum(b-a for a,b in mapping),
               'avertissements': [f'{subject} / projet {project} ; analyse exploratoire.',
                 *[f'{name} : {note}' for name, note in notes.items()],
                 *([f'Écart durée déclarée / dernier horodatage exporté : {duration-last_export_time:.6f} s.'] if timestamp_without_unit else []),
                 *(['Les notes initiales SUJ5–SUJ7 ne sont pas appliquées : leur rattachement au projet 2 reste à confirmer.'] if project == 2 else []),
                 'Marqueurs d’apparition ajoutés manuellement par Élie ; précision selon les réserves de prétraitement.',
                 'Mapping disponible ne signifie ni fixation ni visibilité continue du FND.',
                 'AOI vidéo et AOI image mappée : référentiels et dénominateurs distincts.',
                 'AOI potentiellement imbriquées : les proportions ne se somment pas.',
                 'Aucun acquittement identifié ; aucune mesure de compréhension ou de détection.',
                 'Pas de carte de chaleur sans image de référence et coordonnées validées.']}
    write_csv(output/'echantillons_pseudonymises.csv', eye, list(eye[0]))
    write_csv(output/'alertes.csv', events, ['temps_s','alerte','reserve'])
    expected = ['ALERT_FND', 'ALERT_ML_LARGE', 'ALERT_ML_LIGHT', 'ALERT_RED', 'ALERT_TEXT']
    quality = [{'alerte': name,
                'nombre_marqueurs': sum(e['alerte'] == name for e in events),
                'reserve': notes.get(name, 'Apparition annotée manuellement par Élie'
                    if any(e['alerte'] == name for e in events) else 'Aucun marqueur exporté ; cause non documentée')} for name in expected]
    write_csv(output/'qualite_alertes.csv', quality, ['alerte','nombre_marqueurs','reserve'])
    write_csv(output/'indicateurs_AOI.csv', metrics, list(metrics[0]))
    (output/'resume.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')

    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,
                         'axes.spines.top':False,'axes.spines.right':False,
                         'figure.facecolor':'#f8fafc','axes.facecolor':'#f8fafc'})

    def plot_states(ax, relative=0, bounds=None):
        for i,(label,values) in enumerate(arrays.items()):
            hit = valid & (values == 1)
            unknown = ~valid | ~np.isfinite(values)
            if bounds is not None:
                within = (times >= bounds[0]) & (times <= bounds[1])
                hit &= within
                unknown &= within
            ax.scatter(times[unknown]-relative, np.full(unknown.sum(),i), marker='|', s=10, color='#d5dbe2', rasterized=True)
            ax.scatter(times[hit]-relative,np.full(hit.sum(),i),marker='|',s=38,color=COLORS[i],rasterized=True)
        ax.set_yticks(range(len(aois)),list(aois))
        ax.set_ylim(-.6,len(aois)-.4)
        ax.invert_yaxis()
        ax.grid(axis='x',alpha=.15)

    fig,ax = plt.subplots(figsize=(15,5))
    plot_states(ax)
    ax.broken_barh([(a,b-a) for a,b in mapping],(len(aois),.4),facecolors='#334155')
    ax.set_ylim(len(aois)+.7,-1.1)
    ax.set_yticks(range(len(aois)+1),[*aois,'Intervalles de mapping'])
    for i,e in enumerate(events):
        ax.axvline(e['temps_s'], color='#c84343' if e['alerte']=='ALERT_RED' else '#687585', ls='--',lw=1)
        ax.text(e['temps_s'], -.65, e['alerte'].replace('ALERT_',''), rotation=25, fontsize=9)
    ax.set_xlim(0,duration)
    ax.set_xlabel('Temps depuis le début de l’enregistrement (s)')
    ax.set_title(f'{subject} · Projet {project} — regard et annotations d’alerte',loc='left',fontweight='bold',pad=30)
    fig.text(.02,.025,'Couleur : regard dans l’AOI · Gris : mesure invalide ou AOI non renseignée · Blanc : hors AOI avec mesure valide\nTraits verticaux : apparitions annotées manuellement · Voir les réserves dans qualite_alertes.csv',fontsize=9)
    fig.tight_layout(rect=(0,.12,1,1))
    for ext in ('png','svg'): fig.savefig(output/f'01_chronologie.{ext}',dpi=180)
    plt.close(fig)

    fig,axes = plt.subplots(len(events),1,figsize=(13,12),sharex=True,squeeze=False)
    for ax,e in zip(axes[:,0],events):
        plot_states(ax,e['temps_s'],(e['temps_s']-5,e['temps_s']+10))
        ax.axvline(0,color='#c84343',ls='--')
        ax.set_title(f"{e['alerte']} · marqueur à {e['temps_s']:.2f} s" + (' · PUBLICITÉ SIGNALÉE' if subject == 'SUJ1' and e['alerte']=='ALERT_RED' else ''),loc='left',fontsize=10,fontweight='bold')
        ax.set_xlim(-5,10)
    axes[-1,0].set_xlabel('Temps relatif au marqueur Tobii (s) — zéro = apparition annotée manuellement ; réserves à consulter')
    fig.suptitle(f'{subject} · Regard autour de chaque annotation',fontweight='bold')
    fig.text(.02,.01,'Couleur : dans l’AOI · Gris : invalide / non renseigné · Blanc : hors AOI valide. Aucun délai de détection calculé.',fontsize=9)
    fig.tight_layout(rect=(0,.03,1,.97))
    for ext in ('png','svg'): fig.savefig(output/f'02_fenetres_alertes.{ext}',dpi=180)
    plt.close(fig)

    fig,ax=plt.subplots(figsize=(12,5))
    bars=ax.barh(list(aois),[m['part_dans_AOI_pct'] or 0 for m in metrics],color=COLORS[:len(aois)])
    for bar,m in zip(bars,metrics):
        value=m['part_dans_AOI_pct']
        label=f"{value:.1f} %" if value is not None else 'Non disponible'
        ax.text(bar.get_width()+1,bar.get_y()+bar.get_height()/2,
                label+f" · couverture {m['couverture_AOI_pct_echantillons_oculaires']:.1f} %",va='center',fontsize=9)
    ax.set_xlim(0,100);ax.invert_yaxis()
    ax.set_xlabel('Échantillons dans l’AOI / échantillons oculaires valides avec cette AOI renseignée (%)')
    ax.set_title(f'{subject} · Indicateurs descriptifs du regard',loc='left',fontweight='bold')
    fig.text(.02,.025,'Couverture : part des échantillons oculaires valides avec AOI renseignée, parmi tous les échantillons oculaires.\nAOI potentiellement imbriquées et référentiels distincts : ne pas additionner. Ces proportions ne sont pas des durées de fixation.',fontsize=9)
    fig.tight_layout(rect=(0,.14,1,1))
    for ext in ('png','svg'): fig.savefig(output/f'03_indicateurs_AOI.{ext}',dpi=180)
    plt.close(fig)
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    print(json.dumps(metrics,ensure_ascii=False,indent=2))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path)
    parser.add_argument('--output',type=Path,default=Path('results/SUJ1'))
    parser.add_argument('--subject', choices=['SUJ1','SUJ2','SUJ3','SUJ5','SUJ6','SUJ7'], default='SUJ1')
    args=parser.parse_args()
    analyse(args.source,args.output,args.subject)
