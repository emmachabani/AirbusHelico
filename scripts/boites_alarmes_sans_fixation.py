"""Comparer cinq alarmes par boîtes et points individuels, sans critère de fixation."""
import csv,json,os,tempfile
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR',tempfile.gettempdir()+'/tobii-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/comparaison/boites_5_alarmes_sans_fixation'
ALARMS=['ALERT_ML_LIGHT','ALERT_ML_LARGE','ALERT_FND','ALERT_RED','ALERT_TEXT']
LABELS=['ML LIGHT','ML LARGE','FND','RED','TEXT']
PALETTE=['#356ca3','#da8635','#4b9b70','#9860ad','#d45d76','#927444','#389da4']

def main():
    source=ROOT/'results/comparaison/delais_durees_FND_7_sujets/mesures_FND_et_appuis.csv'
    with source.open() as f:rows=list(csv.DictReader(f))
    OUT.mkdir(parents=True,exist_ok=True);summaries=[];used=[]
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'#f8fafc','axes.facecolor':'#f8fafc'})
    fig,axes=plt.subplots(1,2,figsize=(18,9));fig.subplots_adjust(left=.075,right=.97,top=.73,bottom=.27,wspace=.22)
    for ax,key,title in zip(axes,['delai_premier_point_FND_s','appui_declare_s'],['Premier point de regard mappé dans le FND','Appui d’acquittement : apparition → appui']):
        arrays=[];groups=[]
        for alarm in ALARMS:
            group=[r for r in rows if r['alarme']==alarm and r[key]!='' and not(r['sujet']=='SUJ1' and alarm=='ALERT_RED')]
            groups.append(group);arrays.append([float(r[key]) for r in group])
            values=np.array(arrays[-1]);q=np.percentile(values,[25,50,75]);iqr=q[2]-q[0]
            summaries.append(dict(mesure=key,alarme=alarm,n=len(values),mediane_s=float(q[1]),q1_s=float(q[0]),q3_s=float(q[2]),minimum_s=float(values.min()),maximum_s=float(values.max()),moustache_basse_s=float(values[values>=q[0]-1.5*iqr].min()),moustache_haute_s=float(values[values<=q[2]+1.5*iqr].max())))
            for r in group:used.append(dict(mesure=key,sujet=r['sujet'],projet=r['projet'],alarme=alarm,valeur_s=float(r[key]),reserve=r['reserve']))
        boxes=ax.boxplot(arrays,positions=range(1,6),widths=.48,patch_artist=True,showfliers=False,whis=1.5,medianprops={'color':'#243448','linewidth':2},boxprops={'edgecolor':'#637487'},whiskerprops={'color':'#637487'},capprops={'color':'#637487'})
        for box in boxes['boxes']:box.set(facecolor='#dce6ef',alpha=.75)
        for j,(alarm,group) in enumerate(zip(ALARMS,groups),1):
            for r in group:
                n=int(r['sujet'][3:]);x=j+(n-4)*.065;y=float(r[key]);ax.scatter(x,y,s=58,color=PALETTE[n-1],marker='o' if n<=4 else '^',edgecolors='white',lw=.6,zorder=4)
            if key=='delai_premier_point_FND_s' and alarm=='ALERT_RED':
                old=next(r for r in rows if r['sujet']=='SUJ1' and r['alarme']==alarm);ax.scatter(j-.22,float(old[key]),marker='x',s=70,color='#939ba5',zorder=5)
            median=float(np.median(arrays[j-1]));ax.text(j,.98,f'n = {len(group)}',transform=ax.get_xaxis_transform(),ha='center',va='top',fontsize=10,color='#526174')
            ax.annotate(f'{median:.2f} s',(j+.25,median),xytext=(3,0),textcoords='offset points',fontsize=9,va='center',color='#243448',fontweight='bold')
        ax.set(title=title,xticks=range(1,6),xticklabels=LABELS,xlim=(.4,5.75),ylabel='Secondes');ax.grid(axis='y',alpha=.15)
        ax.set_ylim(bottom=0,top=5.3 if key=='delai_premier_point_FND_s' else 18.5)
    fig.suptitle('Comparer les cinq alarmes · Premier regard FND et temps d’appui',x=.055,ha='left',fontsize=22,fontweight='bold',y=.975)
    fig.text(.055,.92,'Sans règle de fixation · Chaque point représente un sujet · Boîtes descriptives, sans test d’efficacité',fontsize=13,color='#526174')
    handles=[Line2D([],[],marker='o' if n<=4 else '^',ls='',color=PALETTE[n-1],markersize=8,label=f'SUJ{n} · P{1 if n<=4 else 2}') for n in range(1,8)]
    handles.append(Line2D([],[],marker='x',ls='',color='#939ba5',markersize=8,label='SUJ1/RED : publicité, exclu de la boîte'))
    fig.legend(handles=handles,loc='upper left',bbox_to_anchor=(.05,.89),ncol=4,frameon=False,fontsize=11)
    fig.text(.055,.075,'Boîte : quartiles 25–75 % ; trait : médiane (valeur affichée) ; moustaches : observations à moins de 1,5 × l’écart interquartile. Tous les points sont visibles.\nÀ gauche : premier échantillon valide mappé dans le FND, ML incluse, recherché sur 10 s ; aucune durée minimale ni fixation exigée.\nLes effectifs varient selon les marqueurs disponibles : les boîtes ne regroupent pas les mêmes sujets. Pas de délai inventé pour les repères absents.\nÀ droite : trois sujets du projet 2 pour chaque alarme. À gauche : projets 1 et 2 mélangés ; leurs conditions diffèrent.\nUn premier point mappé ne prouve pas une détection consciente. Repères SUJ3 incertains ; ML_LARGE/ML_LIGHT de SUJ6 à vérifier. Aucun classement de performance.',fontsize=10.5,color='#526174',linespacing=1.5)
    for ext in ['png','svg']:fig.savefig(OUT/f'boites_5_alarmes_premier_point_FND_appui.{ext}',dpi=165)
    plt.close(fig)
    for name,data in [('statistiques_boites.csv',summaries),('observations_representees.csv',used)]:
        with (OUT/name).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(data[0]),lineterminator='\n');w.writeheader();w.writerows(data)
    (OUT/'audit_boites.json').write_text(json.dumps(dict(source=str(source.relative_to(ROOT)),regle='premier point mappé, sans seuil de fixation',exclusion_boites='SUJ1 ALERT_RED : publicité ; point gris conservé hors boîte',quartiles='numpy.percentile, interpolation linéaire',moustaches='observations dans Q1−1.5 IQR et Q3+1.5 IQR',statistiques=summaries),ensure_ascii=False,indent=2))
    for p in OUT.glob('*.svg'):p.write_text('\n'.join(x.rstrip() for x in p.read_text().splitlines())+'\n')
    print(json.dumps(summaries,ensure_ascii=False))
if __name__=='__main__':main()
