"""Examiner les fixations Tobii de SUJ1 : passage vers deux zones du FND.

python3 scripts/sequence_fnd_suj1.py --source /chemin/SUJ1.xlsx
La région d'acquittement n'est pas définie et aucun clic n'est inféré.
"""
import argparse
import csv
import json
from pathlib import Path
import openpyxl
import numpy as np
from mouvements_fnd import ROOT
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Patch


def main(source):
    folder=ROOT/'results'/'SUJ1'
    with (folder/'alertes.csv').open(encoding='utf-8-sig') as f:
        events=list(csv.DictReader(f))
    onset=float(next(e['temps_s'] for e in events if e['alerte']=='ALERT_FND'))
    w=openpyxl.load_workbook(source,read_only=True,data_only=True);it=w.active.values;headers=next(it)
    groups={};screen=[];identities=set();projects=set();dims=set()
    for row in it:
        d=dict(zip(headers,row));identities.add(d['Participant name']);projects.add(d['Project name'])
        if d['Sensor']!='Eye Tracker':continue
        t=float(row[0])/1e6
        valid=d.get('Validity left')=='Valid' or d.get('Validity right')=='Valid'
        if not valid:continue
        if abs(t-112.256)<.006:
            screen.append({'temps_s':t,'type_mouvement':d.get('Eye movement type'),
                'x_image_FND':d.get('Mapped gaze point X [HLX FND1] [MCS px]'),
                'y_image_FND':d.get('Mapped gaze point Y [HLX FND1] [MCS px]')})
        if not onset-1<=t<=onset+8 or d.get('Eye movement type')!='Fixation':continue
        dims.add((float(d['Width [HLX FND1] [px]']),float(d['Height [HLX FND1] [px]'])))
        idx=int(d['Eye movement type index'])
        groups.setdefault(idx,[]).append({'t':t-onset,
            'fnd':d.get('AOI hit [Recording 5 - FND]'),'route':d.get('AOI hit [Recording 5 - Main screen]'),
            'x':d.get('Mapped gaze point X [HLX FND1] [MCS px]'),
            'y':d.get('Mapped gaze point Y [HLX FND1] [MCS px]')})
    w.close()
    if identities!={'SUJ1'} or projects!={'Project1'} or len(dims)!=1:raise ValueError('Source incompatible avec SUJ1 / projet 1.')
    width,height=next(iter(dims));rows=[]
    for idx,g in groups.items():
        begin=g[0]['t'];end=g[-1]['t']
        if end-begin<.08:continue
        def prop(key):
            values=[r[key] for r in g if r[key] in (0,1)]
            return float(np.mean(values)) if values else None
        pf,pr=prop('fnd'),prop('route')
        mapped=np.array([[r['x'],r['y']] for r in g],float)
        good=np.isfinite(mapped).all(axis=1)&(mapped[:,0]>=0)&(mapped[:,0]<=width)&(mapped[:,1]>=0)&(mapped[:,1]<=height)
        point=np.median(mapped[good],axis=0) if good.any() else [None,None]
        rows.append({'index_fixation_Tobii':idx,'debut_relatif_s':begin,'fin_relative_s':end,
            'intervalle_observe_s':end-begin,'part_AOI_FND_pct':None if pf is None else 100*pf,
            'part_AOI_route_pct':None if pr is None else 100*pr,
            'zone':'FND' if pf is not None and pf>.5 else ('écran route' if pr is not None and pr>.5 else 'autre / non attribuée'),
            'points_mappes_dans_image':int(good.sum()),'x_median_image_FND':point[0],'y_median_image_FND':point[1]})
    output=folder/'synthese'
    with (output/'sequence_fixations_FND.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    audit={'apparition_FND_s':onset,'image_FND_largeur_hauteur_px':[width,height],
        'hypothese_utilisatrice':'Acquittement possiblement dans le bas de la tablette ; non confirmé, aucune zone de clic délimitée.',
        'capture_recue_curseur_lu_s':112.256,'echantillon_proche_capture':screen,
        'capture_depuis_TEXT_s':112.256-float(next(e['temps_s'] for e in events if e['alerte']=='ALERT_TEXT')),
        'limites':['Fixations identifiées par Tobii ; bornes observées sur échantillons valides et fenêtre tronquée.',
            'Les positions sur l’image ne sont pas des zones fonctionnelles définies.',
            'Aucun clic ni acquittement horodaté ; région de réponse à confirmer.',
            'La capture correspond à une autre alarme que FND si le curseur est bien 112,256 s.']}
    (output/'sequence_FND_et_capture.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'figure.facecolor':'#f8fafc','axes.facecolor':'#f8fafc','axes.spines.top':False,'axes.spines.right':False})
    fig,(ax,spatial)=plt.subplots(1,2,figsize=(16,9),gridspec_kw={'width_ratios':[1.7,1]})
    colors={'FND':'#139c9e','écran route':'#4568b0','autre / non attribuée':'#b2bac6'}
    for i,r in enumerate(rows):
        ax.plot([r['debut_relatif_s'],r['fin_relative_s']],[i,i],lw=7,color=colors[r['zone']],solid_capstyle='butt')
        ax.text(r['fin_relative_s']+.1,i,r['zone'],va='center',fontsize=9)
    ax.set_yticks(range(len(rows)),[f"Fix. {r['index_fixation_Tobii']}" for r in rows]);ax.invert_yaxis()
    ax.axvline(0,color='#b34848',ls='--',lw=1);ax.set_xlim(-1,10)
    ax.set_xlabel('Temps depuis l’apparition annotée de FND (s)')
    ax.set_title('Séquence des fixations identifiées par Tobii',loc='left',fontweight='bold')
    ax.grid(axis='x',alpha=.15)
    mapped=[r for r in rows if r['x_median_image_FND'] is not None and r['fin_relative_s']>0 and r['debut_relatif_s']<4]
    for r in mapped:
        spatial.scatter(r['x_median_image_FND'],r['y_median_image_FND'],s=80+220*r['intervalle_observe_s'],color='#139c9e',alpha=.65,edgecolor='white')
        idx=r['index_fixation_Tobii']
        label={129:'Haut',132:'Milieu',133:'Bas',134:'Bas, à droite'}.get(idx,f'Fix. {idx}')
        offset={129:(12,-25),132:(12,8),133:(-105,-18),134:(15,-25)}.get(idx,(12,8))
        spatial.annotate(f"{label}\n+{r['debut_relatif_s']:.2f} s",(r['x_median_image_FND'],r['y_median_image_FND']),xytext=offset,textcoords='offset points',fontsize=9)
    spatial.set_xlim(0,width);spatial.set_ylim(height,0);spatial.set_aspect('equal')
    spatial.set_xlabel('Position horizontale sur l’image FND (px)');spatial.set_ylabel('Position verticale sur l’image FND (px)')
    spatial.grid(alpha=.15);spatial.set_title('Positions médianes reportées sur le FND\nFond de l’interface non représenté',fontsize=12)
    fig.suptitle('SUJ1 · Après FND, le regard consulte plusieurs zones de l’instrument',x=.06,ha='left',fontsize=19,fontweight='bold')
    fig.text(.06,.88,'Premier regard près du haut du FND, puis consultation de sa partie centrale basse.\nHypothèse à confirmer : acquittement en bas de la tablette. Aucun clic ni zone de réponse précise identifiés.',fontsize=12,color='#526174')
    fig.text(.06,.04,'Les cercles représentent des médianes de points mappés ; leur taille reflète l’intervalle observé, pas une durée d’acquittement.\nLa capture reçue semble montrer 1 min 52,256 s, environ 2,15 s après TEXT : elle illustre un autre événement que FND.\nUn doigt au contact et un regard sur une zone ne prouvent pas l’activation du bouton. Aucun clic n’est identifié dans l’export.',fontsize=10,color='#526174')
    fig.subplots_adjust(left=.08,right=.94,top=.76,bottom=.17,wspace=.45)
    for ext in ['png','svg']:fig.savefig(output/f'04_sequence_zones_FND.{ext}',dpi=170)
    with PdfPages(output/'SUJ1_sequence_zones_FND.pdf') as pdf:pdf.savefig(fig)
    plt.close(fig)
    for r in rows:print(json.dumps(r,ensure_ascii=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source',type=Path,required=True)
    main(parser.parse_args().source)
