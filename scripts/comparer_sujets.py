"""Comparer la disponibilité des données ; pas les performances des participants.

python3 scripts/comparer_sujets.py
Découvre les dossiers results/SUJ* : ajouter les prochains résultats puis relancer.
"""
import csv
import json
import os
from pathlib import Path
import tempfile

os.environ.setdefault('MPLCONFIGDIR', str(Path(tempfile.gettempdir())/'tobii-matplotlib'))
os.environ.setdefault('XDG_CACHE_HOME', str(Path(tempfile.gettempdir())/'tobii-cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np


def main():
    root = Path(__file__).resolve().parents[1]
    folders = sorted((root/'results').glob('SUJ*'), key=lambda p: int(p.name[3:]))
    data = []
    for folder in folders:
        if not (folder/'resume.json').exists():
            continue
        summary = json.loads((folder/'resume.json').read_text())
        with (folder/'qualite_alertes.csv').open(encoding='utf-8-sig') as f:
            quality = {r['alerte']: r for r in csv.DictReader(f)}
        data.append((folder.name, summary, quality))
    if not data:
        raise ValueError('Aucun résultat disponible.')
    output = root/'results'/'comparaison'
    output.mkdir(exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,
                         'axes.spines.top':False,'axes.spines.right':False,
                         'figure.facecolor':'#f8fafc','axes.facecolor':'#f8fafc'})
    fig = plt.figure(figsize=(15, 10 + max(0,len(data)-3)*1.2))
    grid = fig.add_gridspec(2,2,height_ratios=[1,1.25],hspace=.55,wspace=.35)
    ax1, ax2, ax3 = fig.add_subplot(grid[0,0]), fig.add_subplot(grid[0,1]), fig.add_subplot(grid[1,:])
    names=[f"{name} · P{s.get('projet', 1)}" for name,s,_ in data]
    valid=[s['au_moins_un_oeil_valide_pct'] for _,s,_ in data]
    coverage=[100*s['duree_intervalles_mapping_s']/s['duree_s'] for _,s,_ in data]
    y=np.arange(len(data))
    for ax,values,color in [(ax1,valid,'#248b9a'),(ax2,coverage,'#6576b5')]:
        ax.barh(y,[100]*len(y),color='#e7ecf2',height=.5)
        ax.barh(y,values,color=color,height=.5)
        ax.set_yticks(y,names);ax.invert_yaxis();ax.set_xlim(0,116)
        ax.set_xticks([0,25,50,75,100],['0','25','50','75','100 %'])
        ax.spines[['left','bottom']].set_visible(False)
        ax.tick_params(axis='both',length=0,pad=8)
        for i,value in enumerate(values):
            ax.text(102,i,f'{value:.1f} %',va='center',fontweight='bold')
    ax1.set_title('1. Qualité du suivi oculaire',loc='left',fontweight='bold',pad=30)
    ax1.text(0,1.03,'Échantillons avec au moins un œil déclaré valide',transform=ax1.transAxes,fontsize=10,color='#526174')
    ax2.set_title('2. Périodes délimitées pour le mapping',loc='left',fontweight='bold',pad=30)
    ax2.text(0,1.03,'Report du regard sur l’image FND : part de l’essai',transform=ax2.transAxes,fontsize=10,color='#526174')
    alerts=['ALERT_FND','ALERT_ML_LARGE','ALERT_ML_LIGHT','ALERT_RED','ALERT_TEXT']
    colors={'annoté':'#cce9e6','réserve':'#fae1b3','hors champ':'#e0e5ec','absent':'#edf0f5'}
    table=[]
    for i,(name,s,quality) in enumerate(data):
        for j,alert in enumerate(alerts):
            row=quality[alert];count=int(row['nombre_marqueurs']);note=row['reserve']
            if count and ('approximative' in note or 'vérifier' in note or 'perturbé' in note):
                status='réserve'
                label='Annoté*\nPublicité' if 'Publicité' in note else ('Annoté*\nÀ vérifier' if 'mais marqueur' in note else 'Annoté*\nApproximatif')
            elif count:
                status='annoté';label='Annoté'
            elif 'Hors champ' in note:
                status='hors champ';label='Non daté\nHors champ'
            else:
                status='absent';label='Non annoté\nCause inconnue'
            ax3.add_patch(FancyBboxPatch((j-.44,i-.35),.88,.7,boxstyle='round,pad=0.02,rounding_size=0.05',facecolor=colors[status],edgecolor='none'))
            ax3.text(j,i,label,ha='center',va='center',fontsize=10,color='#253449')
            table.append({'sujet':name,'projet':s.get('projet',1),'alerte':alert,'marqueurs':count,'statut':status,'reserve':note})
    ax3.set_xlim(-.6,4.6);ax3.set_ylim(len(data)-.5,-.8)
    ax3.set_yticks(y,names);ax3.set_xticks(range(5),['FND','ML LARGE','ML LIGHT','RED','TEXT'])
    ax3.xaxis.tick_top();ax3.tick_params(length=0,pad=12)
    for spine in ax3.spines.values():spine.set_visible(False)
    ax3.set_title('3. Apparitions d’alertes annotées manuellement par Élie',loc='left',fontweight='bold',pad=42)
    fig.suptitle('Eye tracking · Ce que les trois premiers enregistrements permettent d’exploiter' if len(data)==3 else f'Eye tracking · Disponibilité des données de {len(data)} sujets',x=.08,ha='left',fontsize=19,fontweight='bold',y=.98)
    fig.text(.08,.925,'P1 : clignotement manuel · SUJ1–3  |  P2 : clignotement automatique · SUJ5–7\nComparaison de disponibilité uniquement ; zones de référence différentes entre projets.',fontsize=11,color='#526174')
    fig.text(.08,.105,'* Réserves de prétraitement : SUJ1 RED perturbé par une publicité ; SUJ3 FND et ML LIGHT incertains ;\n  SUJ3 ML LARGE signalé hors champ malgré un marqueur présent. Rejeu éventuel de ML LIGHT à vérifier.\n  P2 : les notes initiales de prétraitement ne sont pas appliquées, faute de rattachement confirmé à ce projet.',fontsize=10,color='#526174')
    fig.text(.08,.035,'Lecture : un bon suivi oculaire ne garantit pas des données interprétables sur chaque alerte.\nLes périodes de mapping ne sont pas du temps de regard vers le FND. Ces résultats ne comparent pas les performances des participants.',fontsize=11,fontweight='bold',color='#253449')
    fig.subplots_adjust(top=.82,bottom=.19,left=.08,right=.95)
    for ext in ['png','svg','pdf']:
        fig.savefig(output/f'comparaison_disponibilite.{ext}',dpi=200)
    plt.close(fig)
    with (output/'qualite_par_sujet_alerte.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(table[0]),lineterminator='\n');writer.writeheader();writer.writerows(table)
    print(f'Comparaison créée pour {len(data)} sujets : {output}')


if __name__=='__main__':
    main()
