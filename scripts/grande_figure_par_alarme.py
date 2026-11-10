"""Grande figure en cinq zones d’alarme, sept sujets par zone, sans PDF."""
import csv,os,tempfile
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR',tempfile.gettempdir()+'/tobii-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/comparaison/delais_durees_FND_7_sujets'
ALARMS=['ALERT_ML_LIGHT','ALERT_ML_LARGE','ALERT_FND','ALERT_RED','ALERT_TEXT']
TITLES=['1 · ML LIGHT','2 · ML LARGE','3 · FND entier clignotant','4 · RED','5 · TEXT']

def main():
    with (OUT/'mesures_FND_et_appuis.csv').open() as f:rows=list(csv.DictReader(f))
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    fig=plt.figure(figsize=(19,21),facecolor='#f3f6fa')
    grid=fig.add_gridspec(3,2,left=.085,right=.965,top=.87,bottom=.13,wspace=.30,hspace=.32)
    # Trois grandes zones en colonne à gauche et deux à droite ; lecture par lignes.
    locations=[(0,0),(0,1),(1,0),(1,1),(2,0)]
    for alarm,title,loc in zip(ALARMS,TITLES,locations):
        ax=fig.add_subplot(grid[loc]);ax.set_facecolor('white')
        bounds=ax.get_position();fig.add_artist(FancyBboxPatch((bounds.x0-.065,bounds.y0-.034),bounds.width+.083,bounds.height+.06,boxstyle='round,pad=0.008,rounding_size=0.008',transform=fig.transFigure,facecolor='white',edgecolor='#d4dde7',linewidth=1,zorder=-1))
        for i in range(7):
            r=next(r for r in rows if r['sujet']==f'SUJ{i+1}' and r['alarme']==alarm)
            ax.axhspan(i-.44,i+.44,color='#edf3f9' if i<4 else '#f9f0f5',alpha=.65,lw=0,zorder=0)
            delay=r['delai_premier_point_FND_s'];press=r['appui_declare_s'];color='#9ca5af' if i==0 and alarm=='ALERT_RED' else '#168fa3'
            if r['apparition_Tobii_s']=='':ax.text(.15,i-.13,'Premier regard non datable',fontsize=9,color='#8a95a3',va='center')
            elif delay=='':ax.text(.15,i-.13,'Aucun point FND observé',fontsize=9,color='#8a95a3',va='center')
            else:
                delay=float(delay);ax.hlines(i-.13,0,delay,lw=2.5,color=color);ax.scatter(delay,i-.13,color=color,s=55,zorder=4)
                ax.annotate(f'{delay:.2f} s',(delay,i-.13),xytext=(6,0),textcoords='offset points',va='center',fontsize=11,color=color,fontweight='bold')
            if press!='':
                press=float(press);ax.hlines(i+.17,0,press,color='#ae3f70',lw=1,alpha=.35,ls=':');ax.scatter(press,i+.17,marker='*',s=110,color='#ae3f70',zorder=4)
                ax.annotate(f'{press:g} s',(press,i+.17),xytext=(6,0),textcoords='offset points',va='center',fontsize=11,color='#96335e')
        ax.axhline(3.5,color='#c3ccd7',lw=1)
        ax.set(xlim=(-.1,20),ylim=(6.6,-.6),yticks=range(7),yticklabels=[f'SUJ{n} · P{1 if n<=4 else 2}' for n in range(1,8)],xticks=[0,2,4,6,8,10,12,14,16,18],xlabel='Secondes depuis l’apparition de l’alarme')
        ax.set_title(title+(' †' if alarm=='ALERT_RED' else ''),loc='left',fontweight='bold',fontsize=16,pad=16);ax.grid(axis='x',alpha=.15)
    guide=fig.add_subplot(grid[2,1]);guide.axis('off')
    guide.text(0,1,'Lecture commune aux cinq zones',fontsize=18,fontweight='bold',va='top')
    guide.text(0,.86,'Chaque zone regroupe une même alarme\net les sept sujets, toujours dans le même ordre.\n\nPoint bleu : premier regard mappé dans le FND,\nmaster liste incluse. Recherche sur les dix premières\nsecondes, avant l’alarme suivante ou la fin de l’essai.\n\nÉtoile rose : appui d’acquittement fourni pour SUJ5–7.\nL’étoile reste visible même sans repère Tobii :\nla durée d’appui est connue indépendamment.\n\nToutes les zones utilisent la même échelle.\nP1 = clignotement manuel ; P2 = automatique.\nLes fonds légers distinguent les deux projets.\n\nL’absence de point bleu ne signifie pas\nque l’alarme n’a pas été détectée.',fontsize=12,color='#526174',va='top',linespacing=1.45)
    fig.suptitle('Les cinq alarmes · Premier regard vers le FND et acquittement',x=.045,ha='left',fontsize=24,fontweight='bold',y=.978)
    fig.text(.045,.942,'Une grande zone par alarme · Sept sujets dans chaque zone · Échelle identique partout',fontsize=15,color='#526174')
    fig.legend(handles=[Line2D([],[],marker='o',color='#168fa3',lw=2,label='Premier point mappé dans le FND'),Line2D([],[],marker='*',markersize=14,color='#ae3f70',ls=':',label='Appui externe (alignement à vérifier)')],loc='upper left',bbox_to_anchor=(.04,.923),ncol=2,frameon=False,fontsize=14)
    fig.text(.045,.025,'Le premier point mappé est une observation disponible, pas une détection consciente confirmée ; des regards plus précoces peuvent manquer.\nAppuis externes : apparition → appui ; correspondance avec le marqueur manuel Tobii à vérifier avant d’interpréter l’écart regard/appui.\n† SUJ1/RED : publicité signalée, point grisé. Repères SUJ3 incertains ; ML_LARGE/ML_LIGHT de SUJ6 à vérifier avec les captures.\nAucune AOI vidéo manuelle, aucun regard interpolé, aucun appui attribué à SUJ1–4. Aucun classement de performance.',fontsize=11,color='#526174',linespacing=1.45)
    for ext in ['png','svg']:fig.savefig(OUT/f'grande_figure_5_zones_alarmes_7_sujets.{ext}',dpi=150)
    plt.close(fig)
    p=OUT/'grande_figure_5_zones_alarmes_7_sujets.svg';p.write_text('\n'.join(x.rstrip() for x in p.read_text().splitlines())+'\n')
if __name__=='__main__':main()
