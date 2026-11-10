"""Délais du premier point FND, durées mappées et appuis, sept sujets × cinq alarmes.
python3 scripts/delais_durees_fnd_7_sujets.py
Aucun PDF ; aucune AOI vidéo manuelle ni interpolation du regard.
"""
import argparse,csv,json,hashlib
from pathlib import Path
import numpy as np
from vue_globale_aoi_alarmes import extract,read,ROOT
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
OUT=ROOT/'results/comparaison/delais_durees_FND_7_sujets'
ALARMS=['ALERT_ML_LIGHT','ALERT_ML_LARGE','ALERT_FND','ALERT_RED','ALERT_TEXT']
TITLES=['ML LIGHT','ML LARGE','FND entier clignotant','RED','TEXT']
WINDOW=10.

def main(sources):
    OUT.mkdir(parents=True,exist_ok=True)
    ack={(r['sujet'],r['type_alerte']):float(r['temps_declare']) for r in read(ROOT/'inputs/projet2/temps_reaction_declares.csv')}
    rows=[];sources_audit=[]
    for n in range(1,8):
        subject=f'SUJ{n}';data=extract(subject,sources);t=data['t'];state=data['state'];valid=data['valid'];inside=state>0
        step=float(np.median(np.diff(t)));dt=np.diff(t,append=t[-1]+step);dt=np.where(dt>.05,step,dt);record_end=float(t[-1]+dt[-1])
        events=read(ROOT/'results'/subject/'alertes.csv');quality={r['alerte']:r['reserve'] for r in read(ROOT/'results'/subject/'qualite_alertes.csv')}
        sources_audit.append({'sujet':subject,'source_sha256':str(data['sha'])})
        for alarm in ALARMS:
            matches=[e for e in events if e['alerte']==alarm];assert len(matches)<=1
            r=dict(sujet=subject,projet=1 if n<=4 else 2,alarme=alarm,apparition_Tobii_s='',appui_declare_s=ack.get((subject,alarm),''),fenetre_disponible_s='',delai_premier_point_FND_s='',statut_premier_point='repère absent',temps_FND_s='',temps_ML_s='',regard_valide_non_mappe_s='',regard_indisponible_s='',presence_mapping_juste_avant_repere=False,reserve=quality.get(alarm,''))
            if matches:
                onset=float(matches[0]['temps_s']);end=min(onset+WINDOW,record_end,min([float(e['temps_s']) for e in events if float(e['temps_s'])>onset],default=record_end));window=max(0.,end-onset)
                weights=np.maximum(0,np.minimum(t+dt,end)-np.maximum(t,onset));weights[t>=end]=0
                hits=np.flatnonzero((t>=onset)&(t<end)&inside)
                before=np.searchsorted(t,onset,side='right')-1;already=before>=0 and onset-t[before]<=.025 and inside[before]
                delay=0. if already else float(t[hits[0]]-onset) if len(hits) else ''
                fnd=float(weights[inside].sum());ml=float(weights[state==2].sum());nonmapped=float(weights[valid&~inside].sum());unavailable=window-fnd-nonmapped
                assert unavailable>=-1e-7 and ml<=fnd+1e-7
                r.update(apparition_Tobii_s=onset,fenetre_disponible_s=window,delai_premier_point_FND_s=delay,statut_premier_point='déjà mappé au repère' if already else 'premier point mappé observé' if delay!='' else 'aucun point mappé observé',temps_FND_s=fnd,temps_ML_s=ml,regard_valide_non_mappe_s=nonmapped,regard_indisponible_s=max(0,unavailable),presence_mapping_juste_avant_repere=bool(already))
            rows.append(r)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'#f8fafc','axes.facecolor':'#f8fafc'})
    def setup(title,subtitle):
        fig,axes=plt.subplots(2,3,figsize=(19,12));fig.subplots_adjust(left=.07,right=.98,top=.81,bottom=.16,wspace=.3,hspace=.4)
        fig.suptitle(title,x=.06,ha='left',fontsize=21,fontweight='bold',y=.975)
        fig.text(.06,.925,subtitle,fontsize=12,color='#526174')
        return fig,axes.ravel()
    fig,axes=setup('Après les alarmes · Premier regard mappé dans le FND et appui','Un panneau par alarme · Un point bleu par sujet pour le premier regard mappé · Une étoile rose pour l’appui externe connu')
    for j,(alarm,title) in enumerate(zip(ALARMS,TITLES)):
        ax=axes[j]
        for i in range(7):
            r=next(r for r in rows if r['sujet']==f'SUJ{i+1}' and r['alarme']==alarm);delay=r['delai_premier_point_FND_s'];press=r['appui_declare_s'];color='#9ba4af' if i==0 and alarm=='ALERT_RED' else '#168fa3'
            if r['apparition_Tobii_s']=='':ax.text(.2,i-.13,'Repère Tobii absent',va='center',fontsize=8.5,color='#7c8796')
            elif delay=='':ax.text(.2,i-.13,'Aucun point FND sur la fenêtre',va='center',fontsize=8.5,color='#7c8796')
            else:
                ax.hlines(i-.13,0,delay,lw=2,color=color);ax.scatter(delay,i-.13,s=43,color=color,zorder=4);ax.annotate(f'{delay:.2f} s',(delay,i-.13),xytext=(5,0),textcoords='offset points',va='center',fontsize=9,color=color,fontweight='bold')
            if press!='':
                ax.scatter(press,i+.16,s=80,color='#ae3f70',marker='*',zorder=4);ax.annotate(f'{press:g} s',(press,i+.16),xytext=(5,0),textcoords='offset points',va='center',fontsize=9,color='#96335e')
        ax.set(title=title+(' †' if alarm=='ALERT_RED' else ''),xlim=(-.1,19.8),ylim=(6.6,-.6),xticks=[0,4,8,12,16,18],yticks=range(7),yticklabels=[f'SUJ{n} · P{1 if n<=4 else 2}' for n in range(1,8)],xlabel='Secondes depuis l’apparition de l’alarme');ax.grid(axis='x',alpha=.15)
        ax.axvline(10,color='#c4cad2',lw=.8,ls='--')
    axes[5].axis('off');axes[5].text(0,1,'Comment lire',fontsize=16,fontweight='bold',va='top')
    axes[5].text(0,.83,'Point bleu : premier point mappé dans le FND,\nML incluse, recherché sur les 10 premières secondes.\n\nÉtoile rose : apparition → appui d’acquittement.\nAffichée même sans repère Tobii, car la durée\nest fournie indépendamment du regard.\n\nLa différence appui / premier point n’est pas\nun temps de traitement validé : les repères\nd’apparition doivent être mis en concordance.\n\nLes étoiles au-delà de 10 s restent affichées ;\nla recherche du premier point reste limitée à 10 s.',fontsize=11,va='top',linespacing=1.55,color='#526174')
    fig.legend(handles=[Line2D([],[],marker='o',color='#168fa3',lw=2,label='Premier point mappé dans le FND'),Line2D([],[],marker='*',color='#ae3f70',ls='',markersize=12,label='Appui déclaré (alignement à vérifier)')],loc='upper left',bbox_to_anchor=(.055,.895),ncol=2,frameon=False,fontsize=11)
    fig.text(.06,.045,'Délai observé ≠ détection consciente : un regard plus précoce peut être masqué par une absence de mapping. Aucun regard interpolé.\nRecherche arrêtée à l’alarme suivante ou à la fin de l’enregistrement. † SUJ1/RED : publicité, point grisé. Repères SUJ3 incertains.\nAppuis disponibles pour SUJ5–7 uniquement. Aucune AOI vidéo manuelle. La correspondance ML_LARGE/ML_LIGHT de SUJ6 avec les captures reste à vérifier.',fontsize=10,color='#526174')
    for ext in ['png','svg']:fig.savefig(OUT/f'premier_regard_FND_et_appuis_7_sujets.{ext}',dpi=170)
    plt.close(fig)
    fig,axes=setup('Après les alarmes · Temps de regard effectivement mappé dans le FND','Durée cumulée sur les 10 premières secondes · FND entier, ML incluse · Les périodes non mappées restent séparées')
    for j,(alarm,title) in enumerate(zip(ALARMS,TITLES)):
        ax=axes[j]
        for i in range(7):
            r=next(r for r in rows if r['sujet']==f'SUJ{i+1}' and r['alarme']==alarm)
            if r['apparition_Tobii_s']=='':ax.text(.1,i,'Repère Tobii absent',va='center',fontsize=9,color='#7c8796');continue
            fnd=r['temps_FND_s'];non=r['regard_valide_non_mappe_s'];absent=r['regard_indisponible_s'];color='#a7afb8' if i==0 and alarm=='ALERT_RED' else '#63b6d1'
            ax.barh(i,fnd,height=.5,color=color,label=None);ax.barh(i,non,left=fnd,height=.5,color='#e0e5eb');ax.barh(i,absent,left=fnd+non,height=.5,color='#b8c0ca')
            ax.text(min(fnd+.1,8.8),i,f'{fnd:.2f} s',va='center',fontsize=9,fontweight='bold',color='#243448')
            if r['fenetre_disponible_s']<9.99:ax.text(10.1,i,f"Fenêtre {r['fenetre_disponible_s']:.1f} s",fontsize=8,va='center')
        ax.set(title=title+(' †' if alarm=='ALERT_RED' else ''),xlim=(0,12.2),ylim=(6.6,-.6),xticks=[0,2,4,6,8,10],yticks=range(7),yticklabels=[f'SUJ{n} · P{1 if n<=4 else 2}' for n in range(1,8)],xlabel='Durée cumulée observée (s)');ax.grid(axis='x',alpha=.12)
    axes[5].axis('off');axes[5].text(0,1,'Une mesure différente du délai',fontsize=16,fontweight='bold',va='top')
    axes[5].text(0,.83,'Bleu : somme des périodes effectivement\nmappées dans le FND, ML incluse.\n\nGris clair : regard valide non mappé.\nCe n’est pas une preuve de regard hors FND.\n\nGris foncé : regard invalide ou données absentes.\n\nLa durée mappée est une durée documentée,\npas une durée totale réelle de consultation.\nLes différences de mapping peuvent expliquer\nune partie des différences entre sujets.\n\nLes appuis restent dans la première figure :\nun instant d’appui et une durée cumulée\nne sont pas la même mesure.',fontsize=11,va='top',linespacing=1.55,color='#526174')
    fig.legend(handles=[Patch(color='#63b6d1',label='Regard mappé dans le FND'),Patch(color='#e0e5eb',label='Regard valide non mappé'),Patch(color='#b8c0ca',label='Regard indisponible / données absentes')],loc='upper left',bbox_to_anchor=(.055,.895),ncol=3,frameon=False,fontsize=11)
    fig.text(.06,.045,'Fenêtre commune de 10 s, arrêt avant l’alarme suivante ou à la fin de l’enregistrement. Les durées des catégories totalisent la fenêtre disponible.\nAucune interpolation ni AOI vidéo manuelle. † SUJ1/RED : publicité signalée ; résultat grisé. Repères SUJ3 incertains.\nUn temps mappé court ne prouve ni une détection rapide ni un manque d’attention. Pas de classement de performance.',fontsize=10,color='#526174')
    for ext in ['png','svg']:fig.savefig(OUT/f'temps_cumule_FND_7_sujets.{ext}',dpi=170)
    plt.close(fig)
    with (OUT/'mesures_FND_et_appuis.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    audit=dict(fenetre_recherche_s=WINDOW,cases=35,reperes=sum(r['apparition_Tobii_s']!='' for r in rows),appuis=sum(r['appui_declare_s']!='' for r in rows),sources=sources_audit,methode='coordonnées mappées dans les limites photo FND ; premier point après repère ou zéro si déjà mappé dans les 25 ms avant ; durées pondérées par les intervalles échantillons ; lacunes >50 ms non prolongées')
    (OUT/'audit_mesures_FND.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
    for f in OUT.glob('*.svg'):f.write_text('\n'.join(s.rstrip() for s in f.read_text().splitlines())+'\n')
    print(json.dumps(audit,ensure_ascii=False))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sources',default='/workspace/attachments');main(p.parse_args().sources)
