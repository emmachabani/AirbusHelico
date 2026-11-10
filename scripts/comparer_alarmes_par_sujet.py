"""Comparer les cinq alarmes dans chaque sujet : premier regard FND et appui.
python3 scripts/comparer_alarmes_par_sujet.py
"""
import csv,os,tempfile
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR',tempfile.gettempdir()+'/tobii-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/comparaison/delais_durees_FND_7_sujets'
ALARMS=['ALERT_ML_LIGHT','ALERT_ML_LARGE','ALERT_FND','ALERT_RED','ALERT_TEXT']
LABELS=['ML LIGHT','ML LARGE','FND','RED','TEXT']

def main():
    with (OUT/'mesures_FND_et_appuis.csv').open() as f:rows=list(csv.DictReader(f))
    assert len(rows)==35
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'#f8fafc','axes.facecolor':'#f8fafc'})
    fig,axes=plt.subplots(2,4,figsize=(23,11));fig.subplots_adjust(left=.065,right=.98,top=.8,bottom=.16,wspace=.38,hspace=.4)
    for n,ax in enumerate(axes.ravel()[:7],1):
        for i,alarm in enumerate(ALARMS):
            r=next(r for r in rows if r['sujet']==f'SUJ{n}' and r['alarme']==alarm)
            delay=r['delai_premier_point_FND_s'];press=r['appui_declare_s'];color='#a0a8b2' if n==1 and alarm=='ALERT_RED' else '#168fa3'
            ax.axhspan(i-.4,i+.4,color='#f0f3f7' if i%2==0 else '#f8fafc',lw=0,zorder=0)
            if r['apparition_Tobii_s']=='':ax.text(.15,i-.12,'Regard non datable',va='center',fontsize=8.5,color='#8993a0')
            elif delay=='':ax.text(.15,i-.12,'Aucun point FND observé',va='center',fontsize=8.5,color='#8993a0')
            else:
                delay=float(delay);ax.hlines(i-.12,0,delay,color=color,lw=2.5);ax.scatter(delay,i-.12,s=45,color=color,zorder=4)
                ax.annotate(f'{delay:.2f} s',(delay,i-.12),xytext=(5,1),textcoords='offset points',va='center',fontsize=9,color=color,fontweight='bold')
            if press!='':
                press=float(press);ax.scatter(press,i+.17,s=90,marker='*',color='#ae3f70',zorder=4)
                ax.annotate(f'{press:g} s',(press,i+.17),xytext=(5,-1),textcoords='offset points',va='center',fontsize=9,color='#96335e')
        ax.set(title=f'SUJ{n} · Projet {1 if n<=4 else 2}',xlim=(-.1,20),ylim=(4.6,-.6),yticks=range(5),yticklabels=[x+(' †' if n==1 and x=='RED' else '') for x in LABELS],xticks=[0,4,8,12,16,18],xlabel='Secondes depuis l’apparition');ax.grid(axis='x',alpha=.15)
        ax.title.set_fontweight('bold')
    guide=axes.ravel()[7];guide.axis('off')
    guide.text(0,1,'Comparer les alarmes',va='top',fontsize=16,fontweight='bold')
    guide.text(0,.83,'Dans chaque panneau :\nles cinq alarmes d’un même sujet.\n\nPlus le point bleu est à gauche,\nplus tôt un regard sur le FND\nest effectivement mappé.\n\nL’étoile rose donne le temps\nd’appui d’acquittement fourni.\n\nToutes les échelles sont identiques.\nSans repère Tobii : pas de point bleu,\nmais l’appui fourni reste visible.',va='top',fontsize=11,color='#526174',linespacing=1.5)
    fig.suptitle('Comparer les cinq alarmes chez chaque sujet · Premier regard FND et appui',x=.055,ha='left',fontsize=22,fontweight='bold',y=.975)
    fig.text(.055,.922,'Un panneau par sujet · Les cinq alarmes alignées sur une même échelle · FND entier, master liste incluse',fontsize=13,color='#526174')
    fig.legend(handles=[Line2D([],[],marker='o',lw=2,color='#168fa3',label='Premier point mappé dans le FND'),Line2D([],[],marker='*',ls='',markersize=12,color='#ae3f70',label='Appui externe déclaré (SUJ5–7)')],loc='upper left',bbox_to_anchor=(.05,.89),ncol=2,frameon=False,fontsize=12)
    fig.text(.055,.045,'Délai du premier point mappé ≠ détection consciente. Recherche sur 10 s, arrêt à l’alarme suivante ou à la fin de l’essai.\nAppuis : apparition → appui, fournis séparément ; concordance des repères avec Tobii à vérifier avant d’interpréter l’écart regard/appui.\n† SUJ1/RED : publicité signalée, point grisé. Repères SUJ3 incertains ; libellé ML_LARGE/ML_LIGHT de SUJ6 à vérifier. Aucune AOI vidéo manuelle.',fontsize=11,color='#526174')
    for ext in ['png','svg']:fig.savefig(OUT/f'comparaison_5_alarmes_par_sujet_regard_appui.{ext}',dpi=165)
    plt.close(fig)
    p=OUT/'comparaison_5_alarmes_par_sujet_regard_appui.svg';p.write_text('\n'.join(x.rstrip() for x in p.read_text().splitlines())+'\n')
if __name__=='__main__':main()
