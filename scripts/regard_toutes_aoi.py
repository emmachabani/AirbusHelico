"""Toutes les AOI exportées, sept sujets, cinq alarmes ; sorties descriptives.

Nécessite les CSV locaux d'échantillons, exclus de Git. Relancer analyse_tobii.py
sur les sept Excel avant ce script ; Rectangle est inclus sans interprétation.
"""
import csv
import json
import os
import tempfile
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR', str(Path(tempfile.gettempdir())/'tobii-matplotlib'))
os.environ.setdefault('XDG_CACHE_HOME', str(Path(tempfile.gettempdir())/'tobii-cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np
from regard_par_alarme import read_csv

AOIS = {
    'FND (vidéo)': ('FND vidéo', '#139c9e'),
    'Écran principal (vidéo)': ('Écran route vidéo', '#4568b0'),
    'ML (vidéo)': ('ML vidéo', '#d29127'),
    'ML (image mappée)': ('ML image FND', '#9464b4'),
    'Rectangle (vidéo, à identifier)': ('Rectangle vidéo*', '#c16b8d'),
}
ALARMS = ['ALERT_FND','ALERT_ML_LARGE','ALERT_ML_LIGHT','ALERT_RED','ALERT_TEXT']


def main():
    root=Path(__file__).resolve().parents[1]
    output=root/'results'/'comparaison'
    fig,axes=plt.subplots(7,5,figsize=(23,18),sharex=True,sharey=True)
    fig.patch.set_facecolor('#f8fafc')
    counts=[]
    for i in range(7):
        subject=f'SUJ{i+1}'
        folder=root/'results'/subject
        summary=json.loads((folder/'resume.json').read_text())
        project=summary.get('projet',1)
        samples=read_csv(folder/'echantillons_pseudonymises.csv')
        events=read_csv(folder/'alertes.csv')
        quality={r['alerte']:r for r in read_csv(folder/'qualite_alertes.csv')}
        t=np.array([float(r['temps_s']) for r in samples])
        valid=np.array([r['au_moins_un_oeil_valide']=='1' for r in samples])
        arrays={name:np.array([float(r[name]) if r.get(name) else np.nan for r in samples]) for name in AOIS}
        for j,alarm in enumerate(ALARMS):
            ax=axes[i,j]
            ax.set_facecolor('#f8fafc')
            ax.set_xlim(-3,8);ax.set_ylim(4.6,-1.15)
            ax.set_yticks(range(5),[v[0] for v in AOIS.values()])
            ax.set_xticks([-3,0,4,8]);ax.tick_params(length=0,labelsize=9,pad=5)
            for spine in ax.spines.values():spine.set_visible(False)
            if i==0:ax.set_title(alarm.replace('ALERT_',''),fontsize=15,fontweight='bold',pad=20)
            if j==0:
                ax.text(-.65,.5,f'{subject}\nProjet {project}',transform=ax.transAxes,ha='right',va='center',fontsize=13,fontweight='bold')
            matches=[r for r in events if r['alerte']==alarm]
            if len(matches)>1:raise ValueError(f'{subject}/{alarm} : répétition à représenter séparément.')
            note=quality[alarm]['reserve']
            if not matches:
                text='Repère absent\nHors champ signalé' if 'Hors champ' in note else 'Repère absent'
                ax.set_facecolor('#edf0f4')
                ax.text(.5,.5,text,transform=ax.transAxes,ha='center',va='center',color='#637082',fontsize=11)
                for name in AOIS:
                    counts.append({'sujet':subject,'projet':project,'alarme':alarm,'AOI':name,'repere_s':'',
                        'statut':'repère absent','echantillons_valides_AOI':'','echantillons_dans_AOI':'','reserve':note})
                continue
            onset=float(matches[0]['temps_s'])
            window=(t>=onset-3)&(t<=onset+8)
            for k,(name,(_,color)) in enumerate(AOIS.items()):
                values=arrays[name]
                known=window&valid&np.isfinite(values)
                inside=known&(values==1)
                outside=known&(values==0)
                ax.axhspan(k-.32,k+.32,color='#e3e8ee',lw=0)
                ax.scatter(t[outside]-onset,np.full(outside.sum(),k),marker='|',s=55,color='#b5c6d3',rasterized=True)
                ax.scatter(t[inside]-onset,np.full(inside.sum(),k),marker='|',s=85,color=color,rasterized=True)
                if name not in samples[0]:
                    state='non exportée'
                    ax.text(7.8,k,state,ha='right',va='center',fontsize=8,color='#657384')
                elif not np.isfinite(values).any():
                    state='non renseignée'
                    ax.text(7.8,k,state,ha='right',va='center',fontsize=8,color='#657384')
                else:
                    state='mesures dans la fenêtre' if known.any() else 'aucune mesure valide dans la fenêtre'
                counts.append({'sujet':subject,'projet':project,'alarme':alarm,'AOI':name,'repere_s':onset,
                    'statut':state,'echantillons_valides_AOI':int(known.sum()),'echantillons_dans_AOI':int(inside.sum()),'reserve':note})
            ax.axvline(0,color='#b34848',ls='--',lw=1)
            reserve='Publicité signalée' if 'Publicité' in note else ('Repère à vérifier' if 'mais marqueur' in note else ('Repère approximatif' if 'approximative' in note else ''))
            if reserve:
                ax.text(.99,.99,reserve,transform=ax.transAxes,ha='right',va='top',fontsize=8,color='#8d5610',bbox={'facecolor':'#fff0d3','edgecolor':'none','pad':2})
    fig.suptitle('Regard autour des cinq alarmes · Toutes les AOI des sept sujets',x=.12,ha='left',fontsize=23,fontweight='bold',y=.985)
    fig.text(.12,.95,'Une ligne de sujets par enregistrement · Une colonne par alarme · Dans chaque case : cinq pistes AOI, aux mêmes positions.',fontsize=13,color='#526174')
    legend=[Patch(color=color,label=label) for label,color in AOIS.values()]
    legend += [Patch(color='#b5c6d3',label='Hors AOI avec mesure valide'),Patch(color='#e3e8ee',label='Mesure absente ou invalide'),Line2D([0],[0],color='#b34848',ls='--',label='Apparition annotée par Élie')]
    fig.legend(handles=legend,loc='upper left',bbox_to_anchor=(.115,.935),ncol=4,frameon=False,fontsize=11)
    fig.supxlabel('Temps depuis l’apparition annotée de l’alarme (secondes)',y=.105,fontsize=14)
    fig.text(.12,.06,'Les couleurs indiquent le regard DANS chaque AOI. Une mesure non exportée/non renseignée ne signifie pas « zone non regardée ».\nP1 : SUJ1–4, manuel · P2 : SUJ5–7, automatique. Les AOI vidéo et image ne sont pas interchangeables et peuvent se chevaucher.',fontsize=12,color='#334155')
    fig.text(.12,.025,'* Rectangle : nom de zone présent dans l’export, contenu à identifier ; aucune fonction supposée.\nRéserves : SUJ1 RED perturbé par une publicité ; SUJ3 repères incertains. Une entrée dans une AOI ne prouve pas la détection de l’alarme.',fontsize=11,color='#526174')
    fig.subplots_adjust(left=.23,right=.985,top=.84,bottom=.16,hspace=.45,wspace=.15)
    for ext in ['png','svg','pdf']:
        fig.savefig(output/f'regard_7_sujets_5_alarmes_toutes_AOI.{ext}',dpi=180)
    plt.close(fig)
    with (output/'regard_fenetres_toutes_AOI.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(counts[0]),lineterminator='\n');writer.writeheader();writer.writerows(counts)
    print(f'{len(counts)} situations sujet/alarme/AOI ; cinq AOI, sept sujets, cinq alarmes.')


if __name__=='__main__':
    main()
