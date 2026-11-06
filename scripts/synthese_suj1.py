"""Synthèse descriptive SUJ1 : ensemble, alarmes, premier regard observé.

Entrées : CSV locaux générés par analyse_tobii.py ; aucun échantillon individuel
n'est publié. Le délai calculé n'est ni une fixation ni une détection confirmée.
"""
import csv
import json
import os
import tempfile
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR',str(Path(tempfile.gettempdir())/'tobii-matplotlib'))
os.environ.setdefault('XDG_CACHE_HOME',str(Path(tempfile.gettempdir())/'tobii-cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Patch
import numpy as np
from regard_par_alarme import read_csv

AOIS=['FND (vidéo)','Écran principal (vidéo)','ML (vidéo)',
      'ML (image mappée)','Rectangle (vidéo, à identifier)']
LABELS=['Tablette FND · vidéo','Écran route · vidéo','Zone ML · vidéo',
        'Zone ML · image FND','Rectangle · vidéo (à identifier)']
COLORS=['#139c9e','#4568b0','#d29127','#9464b4','#c16b8d']
ALARMS=['ALERT_FND','ALERT_ML_LARGE','ALERT_ML_LIGHT','ALERT_RED','ALERT_TEXT']


def first_observed(t, valid, values, onset, end):
    """Premier échantillon dans l'AOI ; état à t0 et lacunes documentés.

    Tolérance d'état à t0 : échantillon antérieur valide au plus 25 ms avant.
    Lacune : intervalle entre mesures AOI valides > 50 ms (seuil descriptif).
    """
    window=(t>=onset)&(t<=end)
    known=valid&np.isfinite(values)
    hits=np.flatnonzero(window&known&(values==1))
    before=np.searchsorted(t,onset,side='right')-1
    at_onset=before>=0 and onset-t[before]<=.025 and known[before]
    already=at_onset and values[before]==1
    delay=0.0 if already else (float(t[hits[0]]-onset) if len(hits) else None)
    stop=onset+delay if delay is not None else end
    observed=t[(t>=onset)&(t<=stop)&known]
    gap=float(np.diff(np.r_[onset,observed,stop]).max())
    return {'delai_premier_regard_observe_s':delay,
            'statut':'déjà dans AOI à t0' if already else ('premier échantillon dans AOI' if delay is not None else 'aucune entrée observée dans la fenêtre'),
            'etat_t0':'dans AOI' if already else ('hors AOI' if at_onset else 'indisponible'),
            'couverture_AOI_fenetre_pct':round(float(100*known[window].mean()),2) if window.any() else None,
            'plus_grand_intervalle_sans_mesure_valide_avant_entree_s':gap,
            'lacune_superieure_50ms_avant_entree':bool(gap>.05)}


def main():
    root=Path(__file__).resolve().parents[1]
    source=root/'results'/'SUJ1'
    output=source/'synthese';output.mkdir(exist_ok=True)
    samples=read_csv(source/'echantillons_pseudonymises.csv')
    events=read_csv(source/'alertes.csv')
    summary=json.loads((source/'resume.json').read_text())
    assert summary.get('projet',1)==1 and len(events)==5
    t=np.array([float(r['temps_s']) for r in samples])
    valid=np.array([r['au_moins_un_oeil_valide']=='1' for r in samples])
    arrays={name:np.array([float(r[name]) if r[name] else np.nan for r in samples]) for name in AOIS}
    by_alarm={e['alerte']:e for e in events}
    if len(by_alarm)!=5 or set(by_alarm)!=set(ALARMS):raise ValueError('Cinq alarmes uniques attendues.')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,
        'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'#f8fafc','axes.facecolor':'#f8fafc'})
    figures=[]

    def tracks(ax, offset=0, bounds=None):
        for k,(name,color) in enumerate(zip(AOIS,COLORS)):
            values=arrays[name];known=valid&np.isfinite(values)
            within=np.ones(len(t),bool) if bounds is None else (t>=bounds[0])&(t<=bounds[1])
            outside=within&known&(values==0);inside=within&known&(values==1)
            ax.axhspan(k-.28,k+.28,color='#e3e8ee',lw=0)
            ax.scatter(t[outside]-offset,np.full(outside.sum(),k),marker='|',s=35,color='#b5c6d3',rasterized=True)
            ax.scatter(t[inside]-offset,np.full(inside.sum(),k),marker='|',s=65,color=color,rasterized=True)
        ax.set_yticks(range(5),LABELS);ax.set_ylim(4.6,-.8)
        ax.grid(axis='x',alpha=.12)

    fig=plt.figure(figsize=(16,10))
    grid=fig.add_gridspec(2,2,height_ratios=[1.5,1],hspace=.65,wspace=.5)
    ax=fig.add_subplot(grid[0,:]);tracks(ax)
    for e in events:
        onset=float(e['temps_s']);ax.axvline(onset,color='#b34848',ls='--',lw=1)
        ax.text(onset,-.55,e['alerte'].replace('ALERT_',''),rotation=20,fontsize=10)
    ax.set_xlim(0,summary['duree_s']);ax.set_xlabel('Temps depuis le début de l’essai (s)')
    ax.set_title('1. Chronologie du regard dans les cinq AOI',loc='left',fontweight='bold',pad=24)
    ax=fig.add_subplot(grid[1,0]);metrics=read_csv(source/'indicateurs_AOI.csv')
    metrics={m['AOI']:m for m in metrics}
    proportions=[float(metrics[a]['part_dans_AOI_pct']) for a in AOIS]
    ax.barh(LABELS,proportions,color=COLORS);ax.invert_yaxis();ax.set_xlim(0,100)
    for k,a in enumerate(AOIS):
        ax.text(proportions[k]+1,k,f"{proportions[k]:.1f} % · couverture {float(metrics[a]['couverture_AOI_pct_echantillons_oculaires']):.1f} %",va='center',fontsize=9)
    ax.set_title('2. Répartition conditionnelle par AOI',loc='left',fontweight='bold')
    ax.set_xlabel('% des échantillons valides avec cette AOI renseignée',fontsize=10)
    ax=fig.add_subplot(grid[1,1]);ax.axis('off')
    text=(f"SUJ1 · Projet 1 · Clignotement manuel\n\nDurée : {summary['duree_s']:.2f} s\nÉchantillons oculaires : {len(t):,}\nAu moins un œil valide : {summary['au_moins_un_oeil_valide_pct']:.2f} %\n5 apparitions annotées manuellement par Élie\nPériodes de mapping : {summary['duree_intervalles_mapping_s']:.2f} s\n\nRED : publicité signalée, essai perturbé.\nAucun acquittement disponible.")
    ax.text(0,1,text,va='top',fontsize=12,linespacing=1.5)
    fig.suptitle('SUJ1 · Vue d’ensemble du regard et des données disponibles',x=.04,ha='left',fontsize=20,fontweight='bold')
    fig.text(.04,.04,'Couleur : dans l’AOI · Bleu-gris : hors AOI avec mesure valide · Gris clair : mesure absente/invalide.\nLes AOI peuvent se chevaucher ; ne pas additionner les proportions. La couverture est rapportée à tous les échantillons oculaires.\nPériodes de mapping ≠ temps de regard. Rectangle : contenu à identifier. Les données pupillaires et cinématiques ne sont pas analysées ici.',fontsize=10)
    fig.subplots_adjust(left=.2,right=.97,top=.85,bottom=.17);figures.append(('01_recap_SUJ1',fig))

    fig,axes=plt.subplots(5,1,figsize=(15,13),sharex=True)
    for ax,alarm in zip(axes,ALARMS):
        onset=float(by_alarm[alarm]['temps_s']);tracks(ax,onset,(onset-3,onset+10))
        ax.axvline(0,color='#b34848',ls='--',lw=1)
        ax.set_title(alarm.replace('ALERT_','')+(' · PUBLICITÉ SIGNALÉE' if alarm=='ALERT_RED' else ''),loc='left',fontweight='bold',fontsize=12)
        ax.set_xlim(-3,10);ax.tick_params(axis='y',labelsize=9)
    axes[-1].set_xlabel('Temps depuis l’apparition annotée de l’alarme (s)')
    fig.suptitle('SUJ1 · Comment le regard évolue autour des cinq alarmes',fontsize=20,fontweight='bold',x=.04,ha='left')
    fig.text(.04,.025,'Chaque ligne est une AOI, pas un niveau de performance. Couleur : dans la zone ; bleu-gris : hors zone valide ; gris clair : mesure absente/invalide.\nRepère zéro ajouté manuellement par Élie. Une entrée dans une zone ne prouve pas que l’alarme a été comprise.',fontsize=10)
    fig.subplots_adjust(left=.23,right=.97,top=.92,bottom=.1,hspace=.7);figures.append(('02_alarmes_SUJ1',fig))

    results=[]
    for alarm in ALARMS:
        onset=float(by_alarm[alarm]['temps_s'])
        following=[float(e['temps_s']) for e in events if float(e['temps_s'])>onset]
        end=min(onset+10,summary['duree_s'],min(following,default=summary['duree_s']))
        for aoi in ['FND (vidéo)','ML (vidéo)','ML (image mappée)']:
            results.append({'sujet':'SUJ1','alarme':alarm,'AOI':aoi,'apparition_annotee_s':onset,
                'fenetre_apres_alarme_s':end-onset,**first_observed(t,valid,arrays[aoi],onset,end),
                'reserve':by_alarm[alarm]['reserve']})
    fig,axes=plt.subplots(1,2,figsize=(15,7),sharey=True)
    for ax,aoi,title,color in zip(axes,['FND (vidéo)','ML (vidéo)'],
            ['Premier regard vers la tablette FND','Premier regard vers la zone ML (vidéo)'],[COLORS[0],COLORS[2]]):
        for k,alarm in enumerate(ALARMS):
            r=next(x for x in results if x['alarme']==alarm and x['AOI']==aoi)
            d=r['delai_premier_regard_observe_s'];c='#a8adb5' if alarm=='ALERT_RED' else color
            if alarm=='ALERT_RED':ax.axhspan(k-.35,k+.35,color='#edf0f4',zorder=0)
            if d is None:ax.text(.12,k,'Aucune entrée observée dans les 10 s',va='center',fontsize=10,color='#637082')
            else:
                ax.hlines(k,0,d,color=c,lw=3);ax.scatter(d,k,s=75,color=c,zorder=3)
                star=' *' if r['lacune_superieure_50ms_avant_entree'] or r['etat_t0']=='indisponible' else ''
                ax.text(d+.15,k,f'{d:.2f} s'+star,va='center',fontsize=11,fontweight='bold',color='#334155')
        ax.set_title(title,loc='left',fontweight='bold',fontsize=13)
        ax.set_xlim(0,5.5);ax.set_yticks(range(5),[a.replace('ALERT_','')+(' †' if a=='ALERT_RED' else '') for a in ALARMS])
        ax.set_xlabel('Délai du premier échantillon de regard observé (s)');ax.grid(axis='x',alpha=.15)
    axes[0].invert_yaxis()
    fig.suptitle('SUJ1 · Rapidité d’orientation du regard après chaque alarme',x=.06,ha='left',fontsize=20,fontweight='bold')
    fig.text(.06,.85,'Mesure exploratoire : apparition annotée → premier regard observé dans une AOI. Aucun temps de détection confirmé.',fontsize=11,color='#526174')
    fig.text(.06,.065,'† RED : publicité signalée ; résultat grisé, à écarter des conclusions sur le format d’alarme.\n* Mesure indisponible au repère zéro ou lacune > 50 ms avant l’entrée : le premier regard réel peut avoir été manqué.\nFenêtre : 10 s après le repère (arrêt avant l’alarme suivante). Un seul essai par type, un seul sujet ; aucun classement d’efficacité.\nTablette FND et ML ne sont pas nécessairement la zone exacte de chaque alarme. Pas de fixation ni d’acquittement exigé.',fontsize=10,color='#526174')
    fig.subplots_adjust(left=.1,right=.97,top=.75,bottom=.27,wspace=.25);figures.append(('03_delais_regard_SUJ1',fig))

    with (output/'delais_regard_SUJ1.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(results[0]),lineterminator='\n');writer.writeheader();writer.writerows(results)
    with PdfPages(output/'SUJ1_synthese_complete.pdf') as pdf:
        for name,fig in figures:
            for ext in ['png','svg']:fig.savefig(output/f'{name}.{ext}',dpi=180)
            pdf.savefig(fig);plt.close(fig)
    print(json.dumps(results,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
