"""Synthèse SUJ1 corrigée : mapping FND/ML, trois états, premiers points observés.
python3 scripts/synthese_suj1.py --sources /workspace/attachments
Aucune AOI vidéo manuelle ; le PDF est régénéré sur demande explicite.
"""
import argparse,csv,json,hashlib
from pathlib import Path
import numpy as np
from vue_globale_aoi_alarmes import extract,read,ROOT
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

COLORS={1:'#63b6d1',2:'#9265b5',3:'#e2bf64',4:'#b8c6a2',0:'#e5e8ed'}
ALARMS=['ALERT_FND','ALERT_ML_LARGE','ALERT_ML_LIGHT','ALERT_RED','ALERT_TEXT']

def main(sources):
    folder=ROOT/'results/SUJ1';output=folder/'synthese';output.mkdir(exist_ok=True)
    data=extract('SUJ1',sources);t=data['t'];state=data['state'].copy();state[(state==0)&data['valid']]=4
    step=float(np.median(np.diff(t)));dt=np.diff(t,append=t[-1]+step);dt=np.where(dt>.05,step,dt)
    end=float(t[-1]+dt[-1]);events=read(folder/'alertes.csv');by={e['alerte']:e for e in events}
    assert set(by)==set(ALARMS) and len(events)==5
    durations={code:float(dt[state==code].sum()) for code in COLORS}
    durations[0]+=end-t[0]-sum(durations.values())
    def stop_for(onset,window):return min(onset+window,end,min([float(e['temps_s']) for e in events if float(e['temps_s'])>onset],default=end))
    spans=[]
    for k in range(len(t)):
        start=float(t[k]);stop=min(end,float(t[k]+dt[k]));code=int(state[k])
        if spans and spans[-1][2]==code and abs(spans[-1][1]-start)<1e-8:spans[-1]=(spans[-1][0],stop,code)
        else:spans.append((start,stop,code))
    lanes={2:0,1:1,4:2,3:1}
    def tracks(ax,origin,lo,hi,observed_end):
        for y in range(3):ax.axhspan(y-.22,y+.22,color=COLORS[0],lw=0)
        for a,b,code in spans:
            a=max(a,lo);b=min(b,hi,observed_end)
            if b<=a or code==0:continue
            ax.broken_barh([(a-origin,b-a)],(lanes[code]-.22,.44),facecolors=COLORS[code],edgecolors='none')
        ax.set(yticks=[0,1,2],yticklabels=['Dans ML','Hors ML, dans le FND','Hors FND présumé*'],ylim=(2.6,-.7),xlim=(lo-origin,hi-origin))
        ax.grid(axis='x',alpha=.14)
        if observed_end<hi:
            ax.axvspan(observed_end-origin,hi-origin,facecolor='#fafbfc',hatch='///',edgecolor='#d4dae0',lw=0)
            ax.text(observed_end-origin+.1,1,'Fin de fenêtre\n(alarme suivante\nou fin d’essai)',fontsize=8,va='center',color='#637082')
    legend=[Patch(color=COLORS[2],label='Dans ML'),Patch(color=COLORS[1],label='FND hors ML'),Patch(color=COLORS[4],label='Hors FND présumé*'),Patch(color=COLORS[0],label='Pas de regard valide / pas de données')]
    caveat='* Hors FND présumé = regard valide sans position mappée dans le FND ; un échec de mapping reste possible.'
    figures=[]
    fig=plt.figure(figsize=(16,10));grid=fig.add_gridspec(2,2,height_ratios=[1.4,1],hspace=.7,wspace=.55)
    ax=fig.add_subplot(grid[0,:]);tracks(ax,0,0,end,end)
    for e in events:
        onset=float(e['temps_s']);ax.axvline(onset,color='#b34848',ls='--',lw=1);ax.text(onset,-.47,e['alerte'].replace('ALERT_',''),rotation=15,fontsize=9)
    ax.set_xlabel('Secondes depuis le début de l’enregistrement');ax.set_title('1 · Chronologie : trois catégories séparées',loc='left',fontweight='bold',pad=20)
    ax=fig.add_subplot(grid[1,0]);codes=[2,1,4,0];labels=['Dans ML','FND hors ML','Hors FND présumé*','Regard indisponible'];total=end-t[0]
    ax.barh(labels,[100*durations[c]/total for c in codes],color=[COLORS[c] for c in codes]);ax.invert_yaxis();ax.set_xlim(0,110)
    for i,c in enumerate(codes):ax.text(100*durations[c]/total+1,i,f'{durations[c]:.2f} s · {100*durations[c]/total:.1f} %',va='center',fontsize=10)
    ax.set_title('2 · Répartition sur le temps observé',loc='left',fontweight='bold');ax.set_xlabel('Pourcentage de durée observée (catégories exclusives)')
    ax=fig.add_subplot(grid[1,1]);ax.axis('off')
    ax.text(0,1,f'SUJ1 · Projet 1 · Clignotement manuel\n\nDurée observée : {total:.2f} s\nÉchantillons oculaires : {len(t):,}\nRegard valide : {100*np.mean(data["valid"]):.1f} % des échantillons\n5 apparitions annotées manuellement par Élie\n\nFND total = ML + FND hors ML\nRED : publicité signalée\nAucun temps d’appui disponible pour SUJ1',va='top',fontsize=12,linespacing=1.5)
    fig.suptitle('SUJ1 · Vue d’ensemble du regard — version corrigée',x=.05,ha='left',fontsize=20,fontweight='bold')
    fig.legend(handles=legend,loc='upper left',bbox_to_anchor=(.045,.93),ncol=4,frameon=False,fontsize=10)
    fig.text(.05,.045,caveat+'\nPhoto entière = FND ; ML est incluse dans le FND. Aucune AOI vidéo manuelle utilisée. Aucun appui déduit du regard.',fontsize=10,color='#526174')
    fig.subplots_adjust(left=.19,right=.97,top=.82,bottom=.16);figures.append(('01_recap_SUJ1',fig))
    fig,axes=plt.subplots(5,1,figsize=(16,14),sharex=True)
    for ax,alarm in zip(axes,ALARMS):
        onset=float(by[alarm]['temps_s']);stop=stop_for(onset,18)
        tracks(ax,onset,onset-3,onset+18,stop);ax.axvline(0,color='#b34848',ls='--',lw=1)
        ax.set_title(alarm.replace('ALERT_','')+(' · PUBLICITÉ SIGNALÉE' if alarm=='ALERT_RED' else ''),loc='left',fontweight='bold',fontsize=12)
        ax.tick_params(axis='y',labelsize=10)
    axes[-1].set_xlabel('Secondes depuis l’apparition annotée de l’alarme')
    fig.suptitle('SUJ1 · Regard avant et après les cinq alarmes',x=.05,ha='left',fontsize=20,fontweight='bold',y=.98)
    fig.legend(handles=legend,loc='upper left',bbox_to_anchor=(.045,.95),ncol=4,frameon=False,fontsize=10)
    fig.text(.05,.025,caveat+'\nFenêtre : −3 à +18 s, arrêt à l’alarme suivante ou à la fin de l’enregistrement. Gris : aucun regard valide / aucune donnée.\nLes bandes ne sont ni des preuves de détection consciente ni des acquittements. Aucune AOI vidéo manuelle.',fontsize=10,color='#526174')
    fig.subplots_adjust(left=.2,right=.97,top=.89,bottom=.1,hspace=.75);figures.append(('02_alarmes_SUJ1',fig))
    results=[]
    for alarm in ALARMS:
        onset=float(by[alarm]['temps_s']);stop=stop_for(onset,10)
        for name,codes in [('FND entier (ML incluse)',[1,2,3]),('Master liste (ML)',[2])]:
            hits=np.flatnonzero((t>=onset)&(t<stop)&np.isin(state,codes));delay=float(t[hits[0]]-onset) if len(hits) else None
            prev=np.searchsorted(t,onset,side='right')-1
            already=prev>=0 and onset-t[prev]<=.025 and state[prev] in codes
            if already:delay=0.
            results.append(dict(sujet='SUJ1',alarme=alarm,zone=name,apparition_annotee_s=onset,fenetre_s=stop-onset,premier_point_mappe_apres_repere_s=delay,statut='déjà mappé dans la zone au repère' if already else 'premier point mappé disponible' if delay is not None else 'aucun point dans la fenêtre',reserve=by[alarm]['reserve']))
    fig,axes=plt.subplots(1,2,figsize=(16,8),sharey=True)
    for ax,zone,color in zip(axes,['FND entier (ML incluse)','Master liste (ML)'],[COLORS[1],COLORS[2]]):
        for i,alarm in enumerate(ALARMS):
            r=next(r for r in results if r['alarme']==alarm and r['zone']==zone);delay=r['premier_point_mappe_apres_repere_s'];c='#a8adb5' if alarm=='ALERT_RED' else color
            if delay is None:ax.text(.2,i,'Aucun point mappé dans la fenêtre',va='center',fontsize=10,color='#637082')
            else:
                ax.hlines(i,0,delay,color=c,lw=3);ax.scatter(delay,i,s=65,color=c);ax.text(delay+.15,i,f'{delay:.2f} s',va='center',fontsize=11,fontweight='bold')
        ax.set(title=zone,xlim=(-.15,11),yticks=range(5),yticklabels=[a.replace('ALERT_','')+(' †' if a=='ALERT_RED' else '') for a in ALARMS],xlabel='Secondes jusqu’au premier point mappé disponible');ax.grid(axis='x',alpha=.15)
    axes[0].invert_yaxis()
    fig.suptitle('SUJ1 · Premiers points de regard mappés après chaque alarme',x=.06,ha='left',fontsize=20,fontweight='bold')
    fig.text(.06,.86,'Repère manuel → premier point mappé observé : ce délai ne mesure pas une détection confirmée.',fontsize=12,color='#526174')
    fig.text(.06,.055,'Les périodes sans mapping peuvent masquer un regard plus précoce. Un délai sans point observé n’est pas remplacé par 10 s.\nRecherche limitée à 10 s, arrêtée avant l’alarme suivante ou la fin de l’essai. Aucun regard interpolé.\n† RED : publicité signalée, résultat grisé. Un essai par format, un sujet : aucun classement d’efficacité.\nLes anciennes valeurs issues des AOI vidéo FND/ML sont remplacées ; aucune AOI vidéo manuelle utilisée. Aucun appui disponible pour SUJ1.',fontsize=11,color='#526174')
    fig.subplots_adjust(left=.1,right=.97,top=.75,bottom=.28,wspace=.25);figures.append(('03_delais_regard_SUJ1',fig))
    with (output/'delais_regard_SUJ1.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(results[0]),lineterminator='\n');w.writeheader();w.writerows(results)
    with PdfPages(output/'SUJ1_synthese_complete.pdf',metadata={'Title':'SUJ1 — Synthèse corrigée FND et master liste'}) as pdf:
        for name,fig in figures:
            for ext in ['png','svg']:fig.savefig(output/f'{name}.{ext}',dpi=170)
            pdf.savefig(fig);plt.close(fig)
    (output/'SUJ1_synthese_complete_actualisee.pdf').write_bytes((output/'SUJ1_synthese_complete.pdf').read_bytes())
    for name,_ in figures:
        p=output/(name+'.svg');p.write_text('\n'.join(s.rstrip() for s in p.read_text().splitlines())+'\n')
    (output/'audit_synthese_corrigee.json').write_text(json.dumps(dict(source_sha256=str(data['sha']),methode='mapping photo FND et AOI ML ; regard valide non mappé = hors FND présumé ; aucune AOI vidéo manuelle',duree_observee_s=total,durees_s={str(k):v for k,v in durations.items()},premiers_points=results),ensure_ascii=False,indent=2))
    print(json.dumps(results,ensure_ascii=False,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sources',default='/workspace/attachments');main(p.parse_args().sources)
