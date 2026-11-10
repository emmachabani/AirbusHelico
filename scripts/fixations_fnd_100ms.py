"""Première fixation Tobii mappée ≥100 ms dans le FND, sans PDF.
python3 scripts/fixations_fnd_100ms.py
"""
import argparse,csv,json
from pathlib import Path
import numpy as np
from vue_globale_aoi_alarmes import ROOT,extract,read
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch
OUT=ROOT/'results/comparaison/fixations_FND_100ms'
ALARMS=['ALERT_ML_LIGHT','ALERT_ML_LARGE','ALERT_FND','ALERT_RED','ALERT_TEXT']
LABELS=['ML LIGHT','ML LARGE','FND','RED','TEXT']
THRESHOLD=.100

def segments(t,inside,fixation,ids):
    # Un point non mappé/invalide/non-fixation casse le segment, même très bref.
    result=[];current=[]
    for i in range(len(t)):
        good=inside[i] and fixation[i] and np.isfinite(ids[i])
        if current and (not good or ids[i]!=ids[current[-1]] or t[i]-t[current[-1]]>.025):
            result.append(current);current=[]
        if good:current.append(i)
    if current:result.append(current)
    return result

def compute(sources):
    previous=read(ROOT/'results/comparaison/delais_durees_FND_7_sujets/mesures_FND_et_appuis.csv')
    rows=[];retained=[];audit=[]
    for n in range(1,8):
        subject=f'SUJ{n}';d=extract(subject,sources);t=d['t'];inside=d['state']>0
        runs=segments(t,inside,d['is_fixation'],d['fixation_id'])
        audit.append(dict(sujet=subject,source_sha256=str(d['sha']),segments_bruts=len(runs)))
        for old in [r for r in previous if r['sujet']==subject]:
            r=dict(sujet=subject,projet=old['projet'],alarme=old['alarme'],apparition_Tobii_s=old['apparition_Tobii_s'],fenetre_s=old['fenetre_disponible_s'],delai_premier_point_FND_historique_s=old['delai_premier_point_FND_s'],delai_premiere_fixation_FND_s='',duree_segment_apres_repere_s='',fixation_deja_en_cours_au_repere=False,appui_declare_s=old['appui_declare_s'],statut='repère absent',reserve=old['reserve'])
            if old['apparition_Tobii_s']!='':
                onset=float(old['apparition_Tobii_s']);end=onset+float(old['fenetre_disponible_s']);matches=[]
                for run in runs:
                    # Seule la partie après l’alarme et dans la fenêtre compte pour les 100 ms.
                    ix=[i for i in run if onset<=t[i]<end]
                    if len(ix)<2:continue
                    span=float(t[ix[-1]]-t[ix[0]])
                    if span+1e-9<THRESHOLD:continue
                    ongoing=t[run[0]]<=onset<=t[run[-1]] and t[ix[0]]-onset<=.025
                    delay=0. if ongoing else float(t[ix[0]]-onset)
                    item=dict(sujet=subject,alarme=old['alarme'],debut_relatif_s=delay,fin_relative_s=float(t[ix[-1]]-onset),duree_observee_apres_repere_s=span,nombre_points=len(ix),index_fixation_Tobii=int(d['fixation_id'][ix[0]]),deja_en_cours=bool(ongoing))
                    retained.append(item);matches.append(item)
                if matches:
                    first=min(matches,key=lambda s:s['debut_relatif_s'])
                    r.update(delai_premiere_fixation_FND_s=first['debut_relatif_s'],duree_segment_apres_repere_s=first['duree_observee_apres_repere_s'],fixation_deja_en_cours_au_repere=first['deja_en_cours'],statut='fixation mappée déjà en cours' if first['deja_en_cours'] else 'première fixation mappée ≥100 ms')
                else:r['statut']='aucune fixation mappée ≥100 ms dans la fenêtre'
            rows.append(r)
        print(subject+' : fixations examinées',flush=True)
    return rows,retained,audit

def draw(ax,rows,subjects=None,alarm=None):
    entries=[next(r for r in rows if r['sujet']==s and r['alarme']==alarm) for s in subjects] if alarm else rows
    for i,r in enumerate(entries):
        ax.axhspan(i-.43,i+.43,color='#edf3f9' if r['projet']=='1' else '#f9f0f5',alpha=.7,lw=0)
        delay=r['delai_premiere_fixation_FND_s'];press=r['appui_declare_s'];color='#9ca5af' if r['sujet']=='SUJ1' and r['alarme']=='ALERT_RED' else '#168fa3'
        if r['apparition_Tobii_s']=='':ax.text(.1,i-.12,'Repère Tobii absent',fontsize=9,color='#8993a0',va='center')
        elif delay=='':ax.text(.1,i-.12,'Aucune fixation ≥100 ms observée',fontsize=8,color='#8993a0',va='center')
        else:
            ax.hlines(i-.12,0,delay,color=color,lw=2.5);ax.scatter(delay,i-.12,color=color,s=55,zorder=4)
            ax.annotate(f'{delay:.2f} s',(delay,i-.12),xytext=(6,0),textcoords='offset points',fontsize=10,color=color,fontweight='bold',va='center')
        if press!='':
            press=float(press);ax.hlines(i+.17,0,press,color='#ae3f70',lw=1,ls=':',alpha=.35);ax.scatter(press,i+.17,marker='*',s=100,color='#ae3f70',zorder=4)
            ax.annotate(f'{press:g} s',(press,i+.17),xytext=(6,0),textcoords='offset points',fontsize=10,color='#96335e',va='center')
    labels=[f"{r['sujet']} · P{r['projet']}" for r in entries] if alarm else [LABELS[ALARMS.index(r['alarme'])] for r in entries]
    ax.set(xlim=(-.1,20),ylim=(len(entries)-.4,-.6),yticks=range(len(entries)),yticklabels=labels,xticks=[0,4,8,12,16,18],xlabel='Secondes depuis l’apparition');ax.grid(axis='x',alpha=.15)

def render(rows):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    legend=[Line2D([],[],marker='o',color='#168fa3',lw=2,label='Début de la première fixation mappée ≥100 ms'),Line2D([],[],marker='*',markersize=14,color='#ae3f70',ls=':',label='Appui externe (alignement à vérifier)')]
    foot='Fixation Tobii + mapping continu dans le FND pendant au moins 100 ms après le repère ; une coupure casse le segment.\nRecherche sur 10 s, arrêt avant l’alarme suivante ou la fin de l’essai. Aucune AOI vidéo manuelle ni interpolation.\nCe critère exclut les passages très brefs, mais ne prouve pas la détection ou la compréhension. Appuis externes à mettre en concordance avec Tobii.\nSUJ1/RED : publicité, point grisé. Repères SUJ3 incertains ; ML_LARGE/ML_LIGHT de SUJ6 à vérifier.'
    fig=plt.figure(figsize=(19,21),facecolor='#f3f6fa');grid=fig.add_gridspec(3,2,left=.085,right=.965,top=.87,bottom=.13,wspace=.3,hspace=.32)
    for alarm,label,loc in zip(ALARMS,LABELS,[(0,0),(0,1),(1,0),(1,1),(2,0)]):
        ax=fig.add_subplot(grid[loc]);ax.set_facecolor('white');b=ax.get_position();fig.add_artist(FancyBboxPatch((b.x0-.065,b.y0-.034),b.width+.083,b.height+.06,boxstyle='round,pad=0.008',transform=fig.transFigure,facecolor='white',edgecolor='#d4dde7',zorder=-1))
        draw(ax,rows,subjects=[f'SUJ{n}' for n in range(1,8)],alarm=alarm);ax.set_title(label,loc='left',fontweight='bold',fontsize=16,pad=15);ax.axhline(3.5,color='#c3ccd7',lw=1)
    ax=fig.add_subplot(grid[2,1]);ax.axis('off');ax.text(0,1,'Un regard soutenu, pas un point isolé',fontsize=17,fontweight='bold',va='top')
    ax.text(0,.85,'Le point bleu marque le début d’un segment :\n• classé Fixation par Tobii ;\n• regard valide et mappé dans le FND ;\n• même fixation, sans point non mappé ;\n• durée observée après l’alarme ≥100 ms.\n\nLe seuil est vérifié sur les mesures réellement\nprésentes, sans combler les coupures.\n\nUne fixation commencée avant l’alarme peut\nêtre retenue à 0 s si elle continue au moins\n100 ms observées après le repère.\n\nCe n’est pas une preuve de détection consciente.\nUn contrôle visuel peut lui aussi durer 100 ms.\n\nL’étoile reste l’appui fourni indépendamment.',fontsize=12,va='top',color='#526174',linespacing=1.45)
    fig.suptitle('Les cinq alarmes · Première fixation soutenue sur le FND et appui',x=.045,ha='left',fontsize=23,fontweight='bold',y=.978)
    fig.text(.045,.942,'Une zone par alarme · Sept sujets · Même échelle · FND entier, master liste incluse',fontsize=15,color='#526174')
    fig.legend(handles=legend,loc='upper left',bbox_to_anchor=(.04,.923),ncol=2,frameon=False,fontsize=13)
    fig.text(.045,.025,foot,fontsize=11,color='#526174',linespacing=1.45)
    save(fig,'grande_figure_5_alarmes_fixations_100ms_appuis')
    fig,axes=plt.subplots(2,4,figsize=(23,11));fig.subplots_adjust(left=.065,right=.98,top=.8,bottom=.18,wspace=.38,hspace=.4)
    for n,ax in enumerate(axes.ravel()[:7],1):
        ordered=[next(r for r in rows if r['sujet']==f'SUJ{n}' and r['alarme']==alarm) for alarm in ALARMS]
        draw(ax,ordered);ax.set_title(f'SUJ{n} · P{1 if n<=4 else 2}',fontweight='bold')
    axes.ravel()[7].axis('off');axes.ravel()[7].text(0,1,'Cinq alarmes par sujet\n\nBleu : début d’une fixation\nmappée ≥100 ms sur le FND.\n\nRose : appui d’acquittement\nfourni séparément.\n\nLes données non observées\nne sont pas reconstruites.',va='top',fontsize=13,color='#526174',linespacing=1.5)
    fig.suptitle('Comparer les alarmes chez chaque sujet · Première fixation FND ≥100 ms et appui',x=.055,ha='left',fontsize=22,fontweight='bold',y=.97)
    fig.legend(handles=legend,loc='upper left',bbox_to_anchor=(.05,.91),ncol=2,frameon=False,fontsize=12)
    fig.text(.055,.035,foot,fontsize=10.5,color='#526174',linespacing=1.4)
    save(fig,'comparaison_par_sujet_fixations_100ms_appuis')

def save(fig,name):
    for ext in ['png','svg']:fig.savefig(OUT/(name+'.'+ext),dpi=150)
    plt.close(fig)
    p=OUT/(name+'.svg');p.write_text('\n'.join(x.rstrip() for x in p.read_text().splitlines())+'\n')

def main(sources):
    OUT.mkdir(parents=True,exist_ok=True);rows,retained,audit=compute(sources)
    for name,data in [('premieres_fixations_FND_100ms.csv',rows),('segments_fixations_FND_100ms.csv',retained)]:
        with (OUT/name).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(data[0]),lineterminator='\n');w.writeheader();w.writerows(data)
    render(rows)
    (OUT/'audit_fixations_100ms.json').write_text(json.dumps(dict(seuil_s=THRESHOLD,fenetre_s=10,ecart_max_entre_points_s=.025,continuite='tout point non mappé, invalide, non Fixation ou changement d’index casse le segment ; aucune interpolation',sujets=audit,fixations_retenues=sum(r['delai_premiere_fixation_FND_s']!='' for r in rows)),ensure_ascii=False,indent=2))
    print(json.dumps(rows,ensure_ascii=False))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sources',default='/workspace/attachments');main(p.parse_args().sources)
