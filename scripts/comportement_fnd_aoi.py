"""Superposer FND/ML au comportement visuel et aux appuis, sans PDF.
python3 scripts/comportement_fnd_aoi.py
"""
import csv,json
from pathlib import Path
import numpy as np
from mouvements_fnd import load_subject
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/comparaison/FND_avec_acquittement'
COLORS={'FND_hors_ML':'#63b6d1','ML':'#9265b5','FND_ML_inconnu':'#e2bf64','indetermine':'#e5e8ed'}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    with (ROOT/'inputs/projet2/temps_reaction_declares.csv').open() as f:
        ack={r['sujet']:float(r['temps_declare']) for r in csv.DictReader(f) if r['type_alerte']=='ALERT_FND'}
    with (ROOT/'results/comparaison/mouvements_FND/retours_FND_5s_vs_12s.csv').open(encoding='utf-8-sig') as f:rows=list(csv.DictReader(f))
    fig,ax=plt.subplots(figsize=(16,9));fig.subplots_adjust(left=.12,right=.97,top=.7,bottom=.23)
    spans=[];audit=[]
    for i,r in enumerate(rows):
        subject=r['sujet'];d=load_subject(int(subject[3:]));t=d['t'];valid=d['valid']&(t>=0)&(t<=12)
        edges=np.diff(np.r_[False,valid,False].astype(int))
        for s,e in zip(np.flatnonzero(edges==1),np.flatnonzero(edges==-1)):
            ax.plot([max(0,t[s]),min(12,t[e-1]+.01)],[i,i],color='#c3cbd5',lw=3,zorder=1)
        def num(key):return float(r[key]) if r[key] else None
        move,hold,duration,ret=[num(key) for key in ['mouvement_s','stabilisation_s','duree_stabilisation_s','retour_fenetre_12s']]
        if move is not None:ax.scatter(move,i,s=48,color='#d29127',zorder=4)
        if hold is not None:ax.plot([hold,hold+duration],[i,i],lw=9,color='#087f83',solid_capstyle='butt',zorder=3)
        if ret is not None:ax.scatter(ret,i,s=65,marker='D',color='#4568b0',zorder=4)
        elif hold is not None:ax.scatter(12,i,marker='>',color='#8794a3',s=60)
        if subject in ack:
            value=ack[subject];ax.scatter(value,i,s=130,marker='*',color='#ae3f70',edgecolors='white',linewidths=.6,zorder=6)
            ax.text(value+.12,i-.16,f'Appui {value:.2f} s',color='#96335e',fontsize=10,fontweight='bold')
        else:ax.text(12.25,i,'Appui non fourni',va='center',fontsize=9,color='#667080')
        if hold is None:ax.text(.2,i-.15,'Motif non retrouvé',fontsize=9,color='#667080')
        data=np.load(ROOT/f'local_analysis/directions_positions_FND/{subject}.npz',allow_pickle=True)['data'].item()
        tt=data['t'];post=tt>=0;step=float(np.median(np.diff(tt)));inside=data['inside'];ml=data['ml']
        labels=np.full(len(tt),'indetermine',dtype=object)
        labels[inside&(ml==0)]='FND_hors_ML';labels[inside&(ml==1)]='ML';labels[inside&~np.isin(ml,[0,1])]='FND_ML_inconnu'
        # Le fond couvre aussi les lacunes d’acquisition ; aucun lien artificiel >50 ms.
        ax.broken_barh([(0,12)],(i+.15,.16),facecolors=COLORS['indetermine'],edgecolors='none')
        local=[]
        for j in np.flatnonzero(post):
            start=max(0,float(tt[j]));end=min(12,float(tt[j+1]) if j+1<len(tt) else float(tt[j]+step))
            if end-start>.05:end=min(12,start+step)
            if end<=start or labels[j]=='indetermine':continue
            state=labels[j]
            if local and local[-1]['etat']==state and abs(local[-1]['fin_s']-start)<1e-8:local[-1]['fin_s']=end
            else:local.append(dict(sujet=subject,etat=state,debut_s=start,fin_s=end))
        for span in local:
            ax.broken_barh([(span['debut_s'],span['fin_s']-span['debut_s'])],(i+.15,.16),facecolors=COLORS[span['etat']],edgecolors='none')
        spans.extend(local)
        durations={state:sum(s['fin_s']-s['debut_s'] for s in local if s['etat']==state) for state in ['FND_hors_ML','ML','FND_ML_inconnu']}
        durations['indetermine']=12-sum(durations.values());assert durations['indetermine']>=-1e-8
        audit.append(dict(sujet=subject,durees_s=durations,source_sha256=data['audit']['source_sha256']))
    ax.set(xlim=(0,15.2),ylim=(6.65,-.65),xticks=[0,2,4,6,8,10,12],yticks=range(7),yticklabels=[f"{r['sujet']} · P{r['projet']}" for r in rows],xlabel='Secondes depuis l’apparition annotée de ALERT_FND');ax.grid(axis='x',alpha=.15)
    fig.suptitle('ALERT_FND · Comportement visuel, zones regardées et acquittement',x=.07,ha='left',y=.97,fontsize=19,fontweight='bold')
    fig.text(.07,.9,'Sous chaque ligne, une bande indique la zone mappée : bleu = FND hors ML ; violet = ML (incluse dans le FND).\nGris clair = position indéterminée ; ce gris ne signifie pas « hors FND ».',fontsize=11,color='#526174')
    fig.legend(handles=[Line2D([],[],marker='o',ls='',color='#d29127',label='Déplacement candidat'),Line2D([],[],lw=7,color='#087f83',label='Maintien géométrique ≥ 300 ms'),Line2D([],[],marker='D',ls='',color='#4568b0',label='Retour proche de la position initiale'),Line2D([],[],marker='*',markersize=13,ls='',color='#ae3f70',label='Appui externe (alignement à vérifier)'),Patch(color=COLORS['FND_hors_ML'],label='FND hors ML'),Patch(color=COLORS['ML'],label='ML, incluse dans le FND'),Patch(color=COLORS['FND_ML_inconnu'],label='FND, statut ML indisponible'),Patch(color=COLORS['indetermine'],label='Position indéterminée')],loc='upper left',bbox_to_anchor=(.065,.845),ncol=3,frameon=False,fontsize=10)
    fig.text(.07,.065,'Appuis SUJ5–7 : durées apparition → appui fournies séparément ; alignement sur les marqueurs manuels Tobii à vérifier.\nLa bande utilise les coordonnées mappées et l’AOI ML exportée ; aucune AOI vidéo manuelle. La ligne fine grise indique la direction oculaire valide.\nDéplacements/maintiens/retours exploratoires dans le repère des lunettes : destinations non confirmées, tête non compensée.\nRéférence SUJ1 à revalider sans les AOI manuelles exclues ; SUJ3 : apparition approximative. Aucun appui attribué à SUJ1–4.',fontsize=10,color='#526174')
    for ext in ['png','svg']:fig.savefig(OUT/f'FND_comportement_visuel_acquittement_AOI.{ext}',dpi=165)
    plt.close(fig)
    with (OUT/'periodes_AOI_FND.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['sujet','etat','debut_s','fin_s'],lineterminator='\n');w.writeheader();w.writerows(spans)
    (OUT/'audit_AOI_FND.json').write_text(json.dumps({'fenetre_s':[0,12],'methode':'intervalles entre échantillons, dernière période médiane, lacunes >50 ms non prolongées ; aucune interpolation','sujets':audit},ensure_ascii=False,indent=2))
    svg=OUT/'FND_comportement_visuel_acquittement_AOI.svg';svg.write_text('\n'.join(x.rstrip() for x in svg.read_text().splitlines())+'\n')
    print(json.dumps(audit,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
