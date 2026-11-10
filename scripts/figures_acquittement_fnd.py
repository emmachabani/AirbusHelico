"""Ajouter les appuis externes aux figures FND, sans PDF ni synchronisation supposée.
python3 scripts/figures_acquittement_fnd.py
"""
import csv,json
from pathlib import Path
import numpy as np
import regard_fnd_7_sujets as directions
from mouvements_fnd import load_subject
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/comparaison/FND_avec_acquittement'

def main():
    with (ROOT/'inputs/projet2/temps_reaction_declares.csv').open() as f:
        entries=[r for r in csv.DictReader(f) if r['type_alerte']=='ALERT_FND']
    assert all(r['unite']=='secondes' and r['debut_mesure']=='apparition_alarme' and r['fin_mesure']=='appui_acquittement' for r in entries)
    ack={r['sujet']:float(r['temps_declare']) for r in entries}
    assert ack=={'SUJ5':3.68,'SUJ6':3.61,'SUJ7':7.99}
    OUT.mkdir(parents=True,exist_ok=True)
    with (ROOT/'results/comparaison/mouvements_FND/retours_FND_5s_vs_12s.csv').open(encoding='utf-8-sig') as f:rows=list(csv.DictReader(f))
    fig,ax=plt.subplots(figsize=(15,8));fig.subplots_adjust(left=.12,right=.97,top=.71,bottom=.23)
    def number(r,k):return float(r[k]) if r[k] else None
    for i,r in enumerate(rows):
        subject=r['sujet'];d=load_subject(int(subject[3:]));t=d['t'];valid=d['valid']&(t>=0)&(t<=12)
        edges=np.diff(np.r_[False,valid,False].astype(int))
        for s,e in zip(np.flatnonzero(edges==1),np.flatnonzero(edges==-1)):
            ax.plot([max(0,t[s]),min(12,t[e-1]+.01)],[i,i],color='#c3cbd5',lw=3,zorder=1)
        move=number(r,'mouvement_s');hold=number(r,'stabilisation_s');duration=number(r,'duree_stabilisation_s');ret=number(r,'retour_fenetre_12s')
        if move is not None:ax.scatter(move,i,s=48,color='#d29127',zorder=3)
        if hold is not None:ax.plot([hold,hold+duration],[i,i],lw=10,color='#087f83',solid_capstyle='butt',zorder=3)
        if ret is not None:ax.scatter(ret,i,s=65,marker='D',color='#4568b0',zorder=4)
        elif hold is not None:ax.scatter(12,i,marker='>',color='#8794a3',s=60)
        if subject in ack:
            value=ack[subject];ax.scatter(value,i,s=130,marker='*',color='#ae3f70',edgecolors='white',linewidths=.6,zorder=6)
            ax.text(value+.12,i-.2,f'Appui {value:.2f} s',color='#96335e',fontsize=10,fontweight='bold')
        else:ax.text(12.25,i,'Appui non fourni',va='center',fontsize=9,color='#667080')
        if hold is None:ax.text(.2,i-.2,'Motif non retrouvé',fontsize=9,color='#667080')
    ax.set(xlim=(0,15.2),ylim=(6.6,-.7),xticks=[0,2,4,6,8,10,12],yticks=range(7),yticklabels=[f"{r['sujet']} · P{r['projet']}" for r in rows],xlabel='Secondes depuis l’apparition annotée de ALERT_FND');ax.grid(axis='x',alpha=.15)
    fig.suptitle('ALERT_FND · Comportement visuel et appui d’acquittement',x=.07,ha='left',y=.97,fontsize=20,fontweight='bold')
    fig.text(.07,.885,'Appuis fournis : SUJ5 3,68 s · SUJ6 3,61 s · SUJ7 7,99 s après l’apparition de l’alarme.\nLe repère d’apparition des durées externes est supposé correspondre au marqueur Tobii : alignement à vérifier.',fontsize=11,color='#526174')
    fig.legend(handles=[Line2D([],[],marker='o',ls='',color='#d29127',label='Déplacement candidat'),Line2D([],[],lw=7,color='#087f83',label='Maintien géométrique ≥ 300 ms'),Line2D([],[],marker='D',ls='',color='#4568b0',label='Retour proche de la position initiale'),Line2D([],[],marker='*',markersize=13,ls='',color='#ae3f70',label='Appui externe, placement conditionnel'),Line2D([],[],lw=3,color='#c3cbd5',label='Direction oculaire valide')],loc='upper left',bbox_to_anchor=(.065,.835),ncol=3,frameon=False,fontsize=10)
    fig.text(.07,.055,'Les étoiles représentent des appuis fournis séparément, pas des clics retrouvés dans Tobii. Aucun appui inventé pour SUJ1–4.\nLes déplacements, maintiens et retours sont exploratoires dans le repère des lunettes ; destinations et rotations de tête non confirmées.\nRéférence du motif SUJ1 à revalider sans les AOI manuelles exclues. SUJ3 : apparition approximative.\nSUJ6 : retour non observé avant +12 s. Un regard dans le bas du FND ne prouve pas un appui.',fontsize=10,color='#526174')
    for ext in ['png','svg']:fig.savefig(OUT/f'FND_comportement_visuel_acquittement.{ext}',dpi=165)
    plt.close(fig)
    # Même annotation sur les figures récentes H/V + positions, depuis les caches locaux.
    original_row=directions.draw_row
    def row(axes,d):
        original_row(axes,d)
        if d['subject'] in ack:
            value=ack[d['subject']]
            for ax in axes[:2]:
                ax.axvline(value,color='#ae3f70',ls='--',lw=1.5)
                ax.text(value+.1,.95,f'Appui {value:.2f} s',transform=ax.get_xaxis_transform(),color='#96335e',fontsize=8,va='top')
        else:axes[0].text(.02,.95,'Appui non fourni',transform=axes[0].transAxes,fontsize=8,va='top',color='#667080')
    original_dec=directions.decorate
    def decorate(fig):
        original_dec(fig)
        y=.19 if fig.get_figheight()<10 else .052
        fig.text(.06,y,'Trait rose : appui externe SUJ5–7 ; alignement sur le marqueur manuel Tobii à vérifier. Aucune position spatiale d’appui inférée.',fontsize=9,color='#96335e')
    directions.draw_row=row;directions.decorate=decorate;directions.OUT=OUT/'directions_positions'
    directions.main('/workspace/attachments',render_only=True)
    (OUT/'appuis_FND.json').write_text(json.dumps({'appuis_secondes':ack,'definition':'apparition de l’alarme à appui d’acquittement','alignement':'placement conditionnel sur le marqueur manuel Tobii ; correspondance des apparitions à vérifier','position_spatiale_appui':'non connue, non inférée'},ensure_ascii=False,indent=2))
    for f in OUT.rglob('*.svg'):f.write_text('\n'.join(s.rstrip() for s in f.read_text().splitlines())+'\n')
if __name__=='__main__':main()
