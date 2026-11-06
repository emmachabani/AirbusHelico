"""Extraire ±12 s autour d'ALERT_FND dans un cache local exclu de Git.

python3 scripts/extraire_fnd.py --sources /workspace/attachments
Conserve uniquement les signaux et temps relatifs, jamais noms ou dates.
"""
import argparse
import csv
import hashlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
import openpyxl

ROOT=Path(__file__).resolve().parents[1]
NAMES=['Gaze point X','Gaze point Y','Gaze direction left X','Gaze direction left Y',
       'Gaze direction left Z','Gyro X','Gyro Y','Gyro Z','Eye movement type',
       'Recording media width','Recording media height','Validity left','Validity right',
       'AOI hit [Recording 5 - FND]','AOI hit [Recording 5 - Main screen]']


def extract(n,sources):
    subject=f'SUJ{n}'
    paths=list(sources.rglob(subject+'.xlsx'))
    if len(paths)!=1:raise ValueError(f'{subject} : un seul fichier source attendu, trouvé {len(paths)}.')
    source=paths[0]
    with (ROOT/'results'/subject/'alertes.csv').open(encoding='utf-8-sig') as f:
        events=[r for r in csv.DictReader(f) if r['alerte']=='ALERT_FND']
    if len(events)!=1:raise ValueError(f'{subject} : un seul marqueur FND attendu.')
    onset=float(events[0]['temps_s'])
    w=openpyxl.load_workbook(source,read_only=True,data_only=True)
    if len(w.worksheets)!=1:raise ValueError('Une seule feuille attendue.')
    rows=w.active.values;headers=next(rows)
    def key(prefix):return next((i for i,x in enumerate(headers) if x==prefix or x.startswith(prefix+' [')),None)
    indices={k:key(k) for k in NAMES}
    sensor=headers.index('Sensor');eye=[];gyro=[]
    participant=headers.index('Participant name');project=headers.index('Project name');event=headers.index('Event')
    identities=set();projects=set();source_onsets=[]
    for row in rows:
        identities.add(row[participant]);projects.add(row[project])
        if str(row[event] or '').upper()=='ALERT_FND':source_onsets.append(float(row[0])/1e6)
        t=float(row[0])/1e6-onset
        if not -12<=t<=12:continue
        if row[sensor]=='Eye Tracker':
            eye.append([t]+[row[i] if i is not None and i<len(row) else None for i in indices.values()])
        elif row[sensor]=='Gyroscope':
            gyro.append([t]+[row[indices[k]] if indices[k] is not None and indices[k]<len(row) else None for k in ['Gyro X','Gyro Y','Gyro Z']])
    w.close()
    expected_project='Project1' if n<=4 else 'Project2'
    if identities!={subject} or projects!={expected_project}:
        raise ValueError(f'{subject} : sujet/projet incompatible avec les résultats existants.')
    if len(source_onsets)!=1 or abs(source_onsets[0]-onset)>.000001:
        raise ValueError(f'{subject} : annotation FND de la source incompatible avec les résultats existants.')
    output=ROOT/'local_analysis'/'fnd';output.mkdir(parents=True,exist_ok=True)
    sha=hashlib.sha256(source.read_bytes()).hexdigest()
    np.savez_compressed(output/f'{subject}.npz',eye=np.array(eye,dtype=object),
        gyro=np.array(gyro,dtype=object),names=np.array(['time']+NAMES),onset=onset,source_sha256=sha)
    return f'{subject} : {len(eye)} échantillons oculaires et {len(gyro)} mesures gyro extraits.'


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources',type=Path,required=True)
    parser.add_argument('--subjects',type=int,nargs='+',default=list(range(1,8)))
    args=parser.parse_args()
    with ThreadPoolExecutor(max_workers=2) as pool:
        for message in pool.map(lambda n:extract(n,args.sources),args.subjects):print(message,flush=True)
