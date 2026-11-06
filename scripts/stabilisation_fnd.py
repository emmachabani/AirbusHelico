"""Motif exploratoire déplacement → stabilisation après ALERT_FND.

python3 scripts/stabilisation_fnd.py
Utilise les caches locaux de extraire_fnd.py. Aucune stabilisation n'est un clic.
"""
import csv
import json
from pathlib import Path
import numpy as np
from mouvements_fnd import ROOT,BIN,load_subject,baseline,binned,candidate
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D


def pattern(s,start,reference,min_hold=.3,radius=2.):
    movement=candidate(s,start,reference)
    result={'mouvement_s':movement['time'],'stabilisation_s':None,'duree_stabilisation_s':None,
            'retour_position_initiale_s':None,'statut':movement['reason'],
            'part_echantillons_Tobii_fixation_pct':None,'part_AOI_FND_pct':None}
    if movement['time'] is None:return result
    center,_=baseline(s,start);times,delta=binned(s,start,center)
    amp=np.linalg.norm(reference);norms=np.linalg.norm(delta,axis=1)
    cosine=np.divide(delta@reference,norms*amp,out=np.zeros(len(times)),where=norms>0)
    matched=(norms>=.5*amp)&(norms<=2*amp)&(cosine>=np.cos(np.radians(45)))
    length=int(round(min_hold/BIN))
    for i in range(len(times)-length+1):
        begin=times[i]-BIN/2
        if begin<start+movement['time']-1e-8 or not matched[i:i+length].all():continue
        end=begin+min_hold
        raw=(s['t']>=begin)&(s['t']<end)
        valid=raw&s['valid']
        if raw.sum()<20 or valid.sum()/raw.sum()<.8:continue
        sample_times=s['t'][valid]
        if np.diff(np.r_[begin,sample_times,end]).max()>.05:continue
        anchor=np.median(s['angles'][valid]-center,axis=0)
        dispersion=np.percentile(np.linalg.norm(s['angles'][valid]-center-anchor,axis=1),90)
        if dispersion>radius:continue
        j=i+length
        while j<len(times) and matched[j]:
            lo=times[j]-BIN/2;hi=times[j]+BIN/2
            raw_bin=(s['t']>=lo)&(s['t']<hi);good=raw_bin&s['valid']
            if not raw_bin.any() or good.sum()<3 or good.sum()/raw_bin.sum()<.8:break
            if np.diff(np.r_[lo,s['t'][good],hi]).max()>.05:break
            if np.percentile(np.linalg.norm(s['angles'][good]-center-anchor,axis=1),90)>radius:break
            j+=1
        finish=times[j-1]+BIN/2
        result.update(stabilisation_s=float(begin-start),duree_stabilisation_s=float(finish-begin),
                      statut='déplacement puis stabilisation dans le repère des lunettes')
        episode=(s['t']>=begin)&(s['t']<finish)&s['valid']
        h=s.get('names',[])
        if 'Eye movement type' in h:
            labels=s['eye'][:,h.index('Eye movement type')]
            known=episode&np.array([x is not None for x in labels])
            if known.any():result['part_echantillons_Tobii_fixation_pct']=float(100*np.mean(labels[known]=='Fixation'))
        if 'AOI hit [Recording 5 - FND]' in h:
            aoi=s['eye'][:,h.index('AOI hit [Recording 5 - FND]')].astype(float)
            known=episode&np.isfinite(aoi)&np.isin(aoi,[0,1])
            if known.any():result['part_AOI_FND_pct']=float(100*np.mean(aoi[known]==1))
        # Retour proche de la position oculaire initiale pendant trois bins valides.
        near=(times>finish)&np.isfinite(delta).all(axis=1)&(norms<=5.)
        returns=np.flatnonzero(near[:-2]&near[1:-1]&near[2:])
        if len(returns):result['retour_position_initiale_s']=float(times[int(returns[0])]-BIN/2-start)
        return result
    result['statut']='mouvement candidat sans stabilisation répondant aux critères'
    return result


def main():
    output=ROOT/'results'/'comparaison'/'mouvements_FND'
    audit=json.loads((output/'methode_et_audit.json').read_text())
    reference=np.array(audit['reference_suj1']['deplacement_yaw_pitch_deg'])
    rows=[];subjects={n:load_subject(n) for n in range(1,8)}
    for n,s in subjects.items():
        result=pattern(s,0,reference)
        control=pattern(s,-7,reference)
        tests=[pattern(s,0,reference,d,r) for d in [.2,.3,.5] for r in [1.,2.,3.]]
        rows.append({'sujet':f'SUJ{n}','projet':1 if n<=4 else 2,**result,
            'stabilisation_temoin_avant_alarme_s':control['stabilisation_s'],
            'statut_temoin':control['statut'],
            'sensibilite_stabilisations_sur_9':sum(x['stabilisation_s'] is not None for x in tests),
            'reserve':'Apparition approximative' if n==3 else 'Destination non confirmée sauf vérification AOI SUJ1'})
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,
                         'figure.facecolor':'#f8fafc','axes.facecolor':'#f8fafc'})
    fig,ax=plt.subplots(figsize=(15,9))
    for i,row in enumerate(rows):
        s=subjects[i+1];center,_=baseline(s,0)
        times,delta=binned(s,0,center)
        good=(times>=0)&np.isfinite(delta).all(axis=1)
        ax.scatter(times[good],np.full(good.sum(),i+.22),marker='|',s=15,color='#c4ccd6')
        move=row['mouvement_s'];hold=row['stabilisation_s'];duration=row['duree_stabilisation_s'];ret=row['retour_position_initiale_s']
        if move is not None:ax.scatter(move,i,color='#d29127',s=65,zorder=4)
        if hold is not None:
            ax.plot([hold,hold+duration],[i,i],color='#087f83',lw=9,solid_capstyle='butt')
            text=f"Stabilisation à {hold:.2f} s · maintien {duration:.2f} s"
            ax.text(5.15,i,text,va='center',fontsize=11)
            if ret is not None:ax.scatter(ret,i,color='#4568b0',s=75,marker='D',zorder=4)
        else:ax.text(5.15,i,'Aucun maintien retenu selon ces critères',va='center',fontsize=10,color='#637082')
        if row['stabilisation_temoin_avant_alarme_s'] is not None:
            ax.text(.05,i-.2,'Motif aussi présent dans la période témoin',color='#9c6a20',fontsize=9)
    ax.set_yticks(range(7),[f"SUJ{n} · P{1 if n<=4 else 2}"+(' *' if n==3 else '') for n in range(1,8)])
    ax.set_ylim(6.5,-.6);ax.set_xlim(0,8.5);ax.set_xticks([0,1,2,3,4,5])
    ax.axvline(5,color='#d6dbe2',lw=.8);ax.grid(axis='x',alpha=.15)
    ax.set_xlabel('Temps depuis l’apparition annotée de l’alarme FND (s)')
    handles=[Line2D([0],[0],marker='o',color='#d29127',lw=0,label='Mouvement candidat'),
             Line2D([0],[0],color='#087f83',lw=7,label='Position oculaire relativement stable'),
             Line2D([0],[0],marker='D',color='#4568b0',lw=0,label='Retour proche de la position oculaire initiale')]
    fig.legend(handles=handles,loc='upper left',bbox_to_anchor=(.07,.88),frameon=False,ncol=1,fontsize=11)
    fig.suptitle('ALERT_FND · Déplacement puis maintien du regard : peut-on retrouver cette séquence ?',x=.07,ha='left',fontsize=18,fontweight='bold',y=.98)
    fig.text(.07,.925,'Critère principal : position stable au moins 300 ms, dispersion p90 ≤ 2°, couverture valide ≥ 80 %, sans lacune > 50 ms.',fontsize=11,color='#526174')
    fig.text(.07,.045,'Maintien ≠ clic ni détection. Il s’agit de stabilité des yeux dans le repère des lunettes, sans compensation de tête.\nRetour proche de la position initiale ≠ retour confirmé vers la route. * SUJ3 : apparition approximative. Recherche limitée aux 5 s après l’alarme.\nLes petits traits gris indiquent les bins de regard valides. Les seuils sont exploratoires, sans validation statistique.',fontsize=10,color='#526174')
    fig.subplots_adjust(left=.12,right=.98,top=.7,bottom=.18)
    for ext in ['png','svg']:fig.savefig(output/f'03_deplacement_stabilisation.{ext}',dpi=170)
    with PdfPages(output/'ALERT_FND_deplacement_stabilisation.pdf') as pdf:pdf.savefig(fig)
    plt.close(fig)
    with (output/'stabilisations_FND.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    for r in rows:print(json.dumps(r,ensure_ascii=False))


if __name__=='__main__':main()
