"""Cartographier les régions haut/milieu/bas du FND et leurs lacunes.

python3 scripts/regions_fnd.py --sources /workspace/attachments
python3 scripts/regions_fnd.py --render-only
Tiers géométriques descriptifs, pas des AOI fonctionnelles validées.
"""
import argparse
import csv
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
import openpyxl
from mouvements_fnd import ROOT
import matplotlib.pyplot as plt
from matplotlib.patches import Patch,Rectangle
from matplotlib.lines import Line2D
from matplotlib.backends.backend_pdf import PdfPages

STEP=.1
END=12.
REGIONS=['haut','milieu','bas','non attribuable']
COLORS={'haut':'#6275ba','milieu':'#dcac48','bas':'#c46b99','non attribuable':'#e1e6ed'}


def region(y,height):
    if not np.isfinite(y) or y<0 or y>height:return 'non attribuable'
    return 'haut' if y<height/3 else ('milieu' if y<2*height/3 else 'bas')


def extract(n,sources):
    subject=f'SUJ{n}';project=1 if n<=4 else 2
    files=list(sources.rglob(subject+'.xlsx'))
    if len(files)!=1:raise ValueError(f'{subject} : un seul Excel attendu.')
    source=files[0]
    with (ROOT/'results'/subject/'alertes.csv').open(encoding='utf-8-sig') as f:
        events=[r for r in csv.DictReader(f) if r['alerte']=='ALERT_FND']
    if len(events)!=1:raise ValueError('Un seul marqueur FND attendu.')
    onset=float(events[0]['temps_s']);media='HLX FND1' if project==1 else 'HLX FND'
    w=openpyxl.load_workbook(source,read_only=True,data_only=True);it=w.active.values;headers=next(it)
    def key(prefix):
        found=[h for h in headers if h==prefix or h.startswith(prefix+' [')]
        if len(found)!=1:raise ValueError(f'{subject} : colonne {prefix} ambiguë/absente.')
        return found[0]
    xkey=key(f'Mapped gaze point X [{media}]');ykey=key(f'Mapped gaze point Y [{media}]')
    widthkey=key(f'Width [{media}]');heightkey=key(f'Height [{media}]')
    bins=[[] for _ in range(120)];identities=set();projects=set();onsets=[];dims=set()
    for row in it:
        d=dict(zip(headers,row));identities.add(d['Participant name']);projects.add(d['Project name'])
        t=float(row[0])/1e6
        if str(d.get('Event') or '').upper()=='ALERT_FND':onsets.append(t)
        rel=t-onset
        if d['Sensor']!='Eye Tracker' or not 0<=rel<END:continue
        width,height=float(d[widthkey]),float(d[heightkey]);dims.add((width,height))
        valid=d.get('Validity left')=='Valid' or d.get('Validity right')=='Valid'
        x,y=d.get(xkey),d.get(ykey)
        assigned='non attribuable'
        if valid and d.get('Eye movement type')=='Fixation' and x is not None and y is not None and 0<=x<=width:
            assigned=region(y,height)
        bins[min(119,int(rel/STEP))].append(assigned)
    w.close()
    if identities!={subject} or projects!={f'Project{project}'} or len(dims)!=1 or len(onsets)!=1 or abs(onsets[0]-onset)>1e-6:
        raise ValueError(f'{subject} : métadonnées incompatibles.')
    states=[]
    for i,labels in enumerate(bins):
        known=[s for s in labels if s!='non attribuable']
        assigned='non attribuable'
        if len(known)>=5:
            most=max(REGIONS[:3],key=known.count)
            if known.count(most)/len(known)>=.8:assigned=most
        states.append({'sujet':subject,'projet':project,'debut_s':i*STEP,'fin_s':(i+1)*STEP,
            'region':assigned,'echantillons_oculaires':len(labels),'echantillons_fixation_mappes':len(known)})
    return states,{'sujet':subject,'projet':project,'media':media,'apparition_FND_s':onset,
        'dimensions_image_px':list(next(iter(dims))),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}


def summarise(states,start,end):
    durations={r:0. for r in REGIONS};chain=[]
    for s in states:
        duration=max(0.,min(s['fin_s'],end)-max(s['debut_s'],start))
        if duration<=0:continue
        durations[s['region']]+=duration
        if not chain or chain[-1]!=s['region']:chain.append(s['region'])
    return durations,chain


def runs(states):
    result=[]
    for s in states:
        if result and result[-1]['region']==s['region'] and abs(result[-1]['fin_s']-s['debut_s'])<1e-7:
            result[-1]['fin_s']=s['fin_s']
        else:result.append({'debut_s':s['debut_s'],'fin_s':s['fin_s'],'region':s['region']})
    return result


def main(sources=None,render_only=False):
    output=ROOT/'results'/'comparaison'/'regions_FND';output.mkdir(exist_ok=True)
    if render_only:
        payload=json.loads((output/'regions_FND_100ms.json').read_text())
        data=payload['sujets']
    else:
        with ThreadPoolExecutor(max_workers=2) as pool:
            values=list(pool.map(lambda n:extract(n,sources),range(1,8)))
        data=[{'bins':s,'audit':a} for s,a in values]
        (output/'regions_FND_100ms.json').write_text(json.dumps({'sujets':data,'parametres':{
            'bin_s':STEP,'points_fixation_mappes_min':5,'majorite_region_min':.8,
            'frontieres_verticales_normalisees':[1/3,2/3],'fenetre_s':[0,END]}},ensure_ascii=False,indent=2))
    with (ROOT/'results'/'comparaison'/'mouvements_FND'/'retours_FND_5s_vs_12s.csv').open(encoding='utf-8-sig') as f:
        markers={r['sujet']:r for r in csv.DictReader(f)}
    rows=[]
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'figure.facecolor':'#f8fafc','axes.facecolor':'#f8fafc',
        'axes.spines.top':False,'axes.spines.right':False})
    fig,(ax,bar)=plt.subplots(1,2,figsize=(19,11),gridspec_kw={'width_ratios':[2.4,1]},sharey=True)
    for i,item in enumerate(data):
        states=item['bins'];audit=item['audit'];subject=audit['sujet'];marker=markers[subject]
        move=float(marker['mouvement_s']) if marker['mouvement_s'] else None
        hold=float(marker['stabilisation_s']) if marker['stabilisation_s'] else None
        duration=float(marker['duree_stabilisation_s']) if marker['duree_stabilisation_s'] else None
        ret=float(marker['retour_fenetre_12s']) if marker['retour_fenetre_12s'] else None
        for s in runs(states):ax.broken_barh([(s['debut_s'],s['fin_s']-s['debut_s'])],(i+.04,.3),facecolor=COLORS[s['region']])
        if move is not None:ax.scatter(move,i-.19,s=50,color='#d29127',zorder=4)
        if hold is not None:
            ax.plot([hold,hold+duration],[i-.19,i-.19],color='#087f83',lw=8,solid_capstyle='butt')
            if ret is not None:ax.scatter(ret,i-.19,color='#4568b0',marker='D',s=65)
            finish=hold+duration;stop=ret if ret is not None else END
            # Cadre : intervalle dont l'utilisatrice demande l'exploration.
            ax.add_patch(Rectangle((finish,i+.02),stop-finish,.34,fill=False,edgecolor='#334155',lw=1.2))
            durations,chain=summarise(states,finish,stop)
            total=stop-finish;left=0
            for r in REGIONS:
                value=100*durations[r]/total
                bar.barh(i,value,left=left,color=COLORS[r],height=.4);left+=value
            label=' … '.join('?' if x=='non attribuable' else x for x in chain)
            rows.append({'sujet':subject,'projet':audit['projet'],'debut_apres_maintien_s':finish,'fin_analyse_s':stop,
                'statut_fin':'retour de position observé' if ret is not None else 'fin de fenêtre, retour non observé',
                **{f'duree_{r.replace(" ","_")}_s':durations[r] for r in REGIONS},
                'part_intervalle_classifiable_pct':100*(1-durations['non attribuable']/total),
                'succession_regions_visibles_avec_lacunes':label})
            bar.text(102,i,f"{100*(1-durations['non attribuable']/total):.0f} % attribuable",va='center',fontsize=9,color='#526174')
        else:
            bar.text(0,i,'Non évalué : aucun maintien retenu',va='center',fontsize=9,color='#637082')
            rows.append({'sujet':subject,'projet':audit['projet'],'debut_apres_maintien_s':'','fin_analyse_s':'',
                'statut_fin':'non évalué, aucun maintien retenu',**{f'duree_{r.replace(" ","_")}_s':'' for r in REGIONS},
                'part_intervalle_classifiable_pct':'','succession_regions_visibles_avec_lacunes':''})
    ax.set_ylim(6.65,-.65);ax.set_xlim(0,12);ax.set_xticks(range(0,13,2));ax.grid(axis='x',alpha=.12)
    ax.set_yticks(range(7),[f'SUJ{n} · P{1 if n<=4 else 2}'+(' *' if n==3 else '') for n in range(1,8)])
    ax.set_xlabel('Secondes depuis l’apparition annotée de FND')
    ax.set_title('Région visible du regard — cadre = entre fin du maintien et retour',loc='left',fontsize=12,fontweight='bold')
    bar.set_xlim(0,143);bar.set_xticks([0,50,100]);bar.set_xlabel('% de l’intervalle encadré');bar.grid(axis='x',alpha=.12)
    bar.tick_params(axis='y',left=False);bar.spines['left'].set_visible(False)
    bar.set_title('Répartition entre maintien et retour\nGris : région non attribuable',loc='left',fontsize=12,fontweight='bold')
    fig.suptitle('ALERT_FND · Où le regard se pose entre le maintien et le retour ?',x=.055,ha='left',fontsize=21,fontweight='bold',y=.98)
    fig.text(.055,.915,'Haut, milieu et bas = trois tiers de l’image FND, pas des zones fonctionnelles validées.\nLes couleurs viennent des coordonnées mappées pendant les fixations ; le gris ne signifie pas « hors du FND ».',fontsize=12,color='#526174')
    handles=[Patch(color=COLORS[r],label=r.capitalize()) for r in REGIONS]
    handles += [Line2D([0],[0],marker='o',color='#d29127',lw=0,label='Déplacement candidat'),
                Line2D([0],[0],color='#087f83',lw=6,label='Maintien retenu'),
                Line2D([0],[0],marker='D',color='#4568b0',lw=0,label='Retour de position')]
    fig.legend(handles=handles,loc='upper left',bbox_to_anchor=(.05,.865),frameon=False,ncol=4,fontsize=11)
    fig.text(.055,.04,'Une séquence colorée séparée par du gris ne reconstitue pas le trajet manquant. Un changement de tiers n’est pas un appui ni un acquittement.\nRégion attribuée par bin de 100 ms : ≥ 5 points de fixation valides mappés, dont ≥ 80 % dans le même tiers. Aucune interpolation.\nRetour de position oculaire / lunettes, sans compensation de tête ni confirmation du lieu final. * SUJ3 : apparition approximative.\nSUJ6/7 : motif aussi trouvé avant l’alarme ; témoins SUJ1/2/5 non évaluables. Comparaison descriptive, sans classement de performance.',fontsize=10,color='#526174')
    fig.subplots_adjust(left=.08,right=.97,top=.73,bottom=.18,wspace=.25)
    for ext in ['png','svg']:fig.savefig(output/f'FND_maintien_exploration_retour.{ext}',dpi=170)
    with PdfPages(output/'FND_maintien_exploration_retour.pdf') as pdf:pdf.savefig(fig)
    plt.close(fig)
    with (output/'regions_entre_maintien_retour.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    for row in rows:print(json.dumps(row,ensure_ascii=False),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);g=parser.add_mutually_exclusive_group(required=True)
    g.add_argument('--sources',type=Path);g.add_argument('--render-only',action='store_true')
    args=parser.parse_args();main(args.sources,args.render_only)
