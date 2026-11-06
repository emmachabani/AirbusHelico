"""Vue exploratoire du regard vers ML autour des cinq alarmes, pour sept sujets.

Lit les CSV locaux exclus de Git, produits par analyse_tobii.py.
python3 scripts/regard_par_alarme.py
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
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import numpy as np


def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def main():
    root = Path(__file__).resolve().parents[1]
    out = root/'results'/'comparaison'
    alarms = ['ALERT_FND','ALERT_ML_LARGE','ALERT_ML_LIGHT','ALERT_RED','ALERT_TEXT']
    fig, axes = plt.subplots(7,5,figsize=(18,12),sharex=True,sharey=True)
    fig.patch.set_facecolor('#f8fafc')
    available = 0
    window_rows=[]
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
        ml=np.array([float(r['ML (image mappée)']) if r['ML (image mappée)'] else np.nan for r in samples])
        for j,alarm in enumerate(alarms):
            ax=axes[i,j]
            ax.set_facecolor('#e4e8ee')
            ax.set_xlim(-3,8);ax.set_ylim(-.6,.6)
            ax.set_yticks([]);ax.set_xticks([-3,0,4,8])
            ax.tick_params(axis='x',labelsize=9,length=0,pad=5)
            for spine in ax.spines.values():spine.set_visible(False)
            if i==0:ax.set_title(alarm.replace('ALERT_',''),fontsize=13,fontweight='bold',pad=16)
            if j==0:
                ax.set_ylabel(f'{subject}\nProjet {project}',rotation=0,labelpad=48,va='center',fontsize=11,fontweight='bold')
            matches=[r for r in events if r['alerte']==alarm]
            if len(matches)>1:
                raise ValueError(f'{subject}/{alarm} : répétitions à représenter séparément.')
            note=quality[alarm]['reserve']
            if not matches:
                text='Repère absent\nHors champ signalé' if 'Hors champ' in note else 'Repère absent'
                ax.text(.5,.5,text,transform=ax.transAxes,ha='center',va='center',color='#637082',fontsize=10)
                window_rows.append({'sujet':subject,'projet':project,'alarme':alarm,'repere_s':'',
                    'echantillons_fenetre':'','echantillons_valides_ML_renseignee':'','echantillons_dans_ML':'','reserve':note})
                continue
            available+=1
            onset=float(matches[0]['temps_s'])
            window=(t>=onset-3)&(t<=onset+8)
            known=window&valid&np.isfinite(ml)
            inside=known&(ml==1)
            outside=known&(ml==0)
            # Bandes disjointes : les points hors ML restent visibles près d'un regard ML.
            ax.scatter(t[outside]-onset,np.full(outside.sum(),-.18),marker='|',s=100,color='#8eb7d5',rasterized=True)
            ax.scatter(t[inside]-onset,np.full(inside.sum(),.12),marker='|',s=190,color='#087f83',rasterized=True)
            ax.axvline(0,color='#b34848',ls='--',lw=1)
            reserve=''
            if 'Publicité' in note:reserve='Publicité signalée'
            elif 'mais marqueur' in note:reserve='Repère à vérifier'
            elif 'approximative' in note:reserve='Repère approximatif'
            if reserve:
                ax.text(.98,.92,reserve,transform=ax.transAxes,ha='right',va='top',fontsize=8,color='#8d5610',bbox={'facecolor':'#fff0d3','edgecolor':'none','pad':2})
            window_rows.append({'sujet':subject,'projet':project,'alarme':alarm,'repere_s':onset,
                'echantillons_fenetre':int(window.sum()),'echantillons_valides_ML_renseignee':int(known.sum()),
                'echantillons_dans_ML':int(inside.sum()),'reserve':note})
    fig.suptitle('Comment le regard vers la zone ML évolue autour des différents types d’alarme',x=.08,ha='left',fontsize=19,fontweight='bold',y=.98)
    fig.text(.08,.935,'7 sujets · 5 alarmes · Chaque case aligne le regard sur l’apparition annotée manuellement par Élie (t = 0).',fontsize=12,color='#526174')
    legend=[Patch(color='#087f83',label='Regard dans la zone ML (bande haute)'),
            Patch(color='#8eb7d5',label='Regard hors ML, mesure valide (bande basse)'),
            Patch(color='#e4e8ee',label='Aucune mesure ML valide représentée'),
            Line2D([0],[0],color='#b34848',ls='--',label='Apparition annotée')]
    fig.legend(handles=legend,loc='upper left',bbox_to_anchor=(.075,.92),ncol=2,frameon=False,fontsize=10)
    fig.supxlabel('Temps par rapport à l’apparition annotée de l’alarme (secondes)',y=.12,fontsize=12)
    fig.text(.08,.065,'Lecture : les segments verts montrent les instants où le regard est enregistré dans ML. Le gris ne signifie pas « alarme non vue ».\nLa zone ML ne représente pas nécessairement l’emplacement de chacune des cinq alarmes. Les AOI diffèrent entre projets ; pas de classement de performance.',fontsize=10,color='#334155')
    fig.text(.08,.025,'Projet 1 : SUJ1–4 (manuel) · Projet 2 : SUJ5–7 (automatique). Réserves : publicité pour SUJ1 RED ; repères incertains pour SUJ3.\nAbsence de segment vert ≠ absence de détection. Des données manquantes et l’absence d’acquittements limitent l’interprétation.',fontsize=10,color='#526174')
    fig.subplots_adjust(left=.12,right=.98,top=.82,bottom=.19,hspace=.4,wspace=.13)
    for ext in ['png','svg','pdf']:
        fig.savefig(out/f'regard_7_sujets_5_alarmes.{ext}',dpi=180)
    plt.close(fig)
    with (out/'regard_fenetres_7_sujets.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(window_rows[0]),lineterminator='\n')
        writer.writeheader();writer.writerows(window_rows)
    print(f'{len(window_rows)} cases ; {available} repères présents ; figures PNG/SVG/PDF générées.')


if __name__=='__main__':
    main()
