"""Positions sur le FND : ordre numéroté et couleur temporelle, sept sujets.

python3 scripts/positions_fnd_7_sujets.py --sources /workspace/attachments
Repère : chaque image FND propre au projet ; aucune zone de clic supposée.
"""
import argparse
import csv
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import openpyxl
import numpy as np
from mouvements_fnd import ROOT
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from matplotlib.backends.backend_pdf import PdfPages

END=8.


def extract(n,sources):
    subject=f'SUJ{n}';project=1 if n<=4 else 2
    paths=list(sources.rglob(subject+'.xlsx'))
    if len(paths)!=1:raise ValueError(f'{subject} : source absente ou ambiguë.')
    source=paths[0]
    with (ROOT/'results'/subject/'alertes.csv').open(encoding='utf-8-sig') as f:
        ev=[r for r in csv.DictReader(f) if r['alerte']=='ALERT_FND']
    if len(ev)!=1:raise ValueError('Un seul marqueur FND attendu.')
    onset=float(ev[0]['temps_s']);media='HLX FND1' if project==1 else 'HLX FND'
    w=openpyxl.load_workbook(source,read_only=True,data_only=True)
    if len(w.worksheets)!=1:raise ValueError('Une seule feuille attendue.')
    it=w.active.values;headers=next(it)
    def key(prefix):
        found=[k for k in headers if k==prefix or k.startswith(prefix+' [')]
        if len(found)!=1:raise ValueError(f'{subject} : colonne {prefix} ambiguë/absente.')
        return found[0]
    xkey=key(f'Mapped gaze point X [{media}]');ykey=key(f'Mapped gaze point Y [{media}]')
    widthkey=key(f'Width [{media}]');heightkey=key(f'Height [{media}]')
    identities=set();projects=set();onsets=[];points=[];dims=set();eye_count=0;valid_count=0;mapped_count=0
    for row in it:
        d=dict(zip(headers,row));identities.add(d['Participant name']);projects.add(d['Project name'])
        t=float(row[0])/1e6
        if str(d.get('Event') or '').upper()=='ALERT_FND':onsets.append(t)
        if d['Sensor']!='Eye Tracker' or not 0<=t-onset<=END:continue
        eye_count+=1
        valid=d.get('Validity left')=='Valid' or d.get('Validity right')=='Valid'
        if valid:valid_count+=1
        width,height=float(d[widthkey]),float(d[heightkey]);dims.add((width,height))
        x,y=d.get(xkey),d.get(ykey)
        if not valid or x is None or y is None or not (0<=x<=width and 0<=y<=height):continue
        mapped_count+=1
        if d.get('Eye movement type')!='Fixation':continue
        points.append({'t':t-onset,'x':float(x),'y':float(y),'index':int(d['Eye movement type index'])})
    w.close()
    if identities!={subject} or projects!={f'Project{project}'} or len(dims)!=1:
        raise ValueError(f'{subject} : sujet, projet ou dimensions incompatibles.')
    if len(onsets)!=1 or abs(onsets[0]-onset)>1e-6:raise ValueError('Marqueur FND incompatible.')
    width,height=next(iter(dims))
    # Une lacune de mapping > 50 ms coupe un segment même si l'index Tobii persiste.
    segments=[]
    for point in points:
        if not segments or point['index']!=segments[-1][-1]['index'] or point['t']-segments[-1][-1]['t']>.05:
            segments.append([])
        segments[-1].append(point)
    rows=[]
    for segment in segments:
        span=segment[-1]['t']-segment[0]['t']
        if len(segment)<5 or span<.04:continue
        rows.append({'sujet':subject,'projet':project,'ordre_visible':len(rows)+1,
            'index_fixation_Tobii':segment[0]['index'],'debut_relatif_s':segment[0]['t'],
            'fin_relative_s':segment[-1]['t'],'intervalle_observe_s':span,
            'x_median_px':float(np.median([p['x'] for p in segment])),
            'y_median_px':float(np.median([p['y'] for p in segment])),
            'nombre_points':len(segment)})
    audit={'sujet':subject,'projet':project,'media':media,'largeur_px':width,'hauteur_px':height,
        'apparition_annotee_FND_s':onset,'fenetre_apres_alarme_s':END,'echantillons_oculaires':eye_count,
        'echantillons_oculaires_valides':valid_count,'points_valides_mappes_dans_image':mapped_count,
        'couverture_mappage_pct':100*mapped_count/eye_count if eye_count else None,
        'segments_representes':len(rows),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'reserve':'Apparition FND approximative selon les notes' if n==3 else 'Pas de clic identifié'}
    return rows,audit


def draw(ax,rows,audit,small=False):
    width,height=audit['largeur_px'],audit['hauteur_px']
    ax.set_xlim(0,100);ax.set_ylim(100,0);ax.set_box_aspect(height/width)
    ax.set_xticks([0,50,100]);ax.set_yticks([0,25,50,75,100]);ax.tick_params(labelsize=9)
    ax.set_xlabel('Position horizontale (% image)',fontsize=9);ax.set_ylabel('Position verticale (% image)',fontsize=9)
    ax.grid(alpha=.17)
    coverage=audit['couverture_mappage_pct']
    count=f"{len(rows)} position"+('s' if len(rows)!=1 else '')
    ax.set_title(f"{audit['sujet']} · Projet {audit['projet']}"+(' · repère approximatif' if audit['sujet']=='SUJ3' else '')+
        f"\n{count} · couverture mappage {coverage:.0f} %",fontsize=10 if small else 13,fontweight='bold')
    occupied=[]
    for row in rows:
        x=100*row['x_median_px']/width;y=100*row['y_median_px']/height
        color=plt.get_cmap('viridis')(row['debut_relatif_s']/END)
        ax.scatter(x,y,s=50 if small else 95,color=[color],edgecolor='white',linewidth=.7,zorder=3)
        # Labels décalés et reliés au point : aucune liaison entre positions à travers les lacunes.
        choices=[(x+dx,y+dy) for dx,dy in [(5,-4),(-5,-4),(5,5),(-5,5),(10,0),(-10,0),(0,-10),(0,10),(12,-8),(-12,8)]]
        choices=[(float(np.clip(a,4,96)),float(np.clip(b,4,96))) for a,b in choices]
        label=max(choices,key=lambda q:min([np.hypot(q[0]-u,q[1]-v) for u,v in occupied] or [100]))
        occupied.append(label)
        ax.annotate(str(row['ordre_visible']),(x,y),xytext=label,textcoords='data',ha='center',va='center',
            fontsize=8 if small else 11,fontweight='bold',color='#253449',
            bbox={'boxstyle':'round,pad=.15','fc':'white','ec':'#d4dbe3','lw':.5},
            arrowprops={'arrowstyle':'-','color':'#9aa6b5','lw':.6},zorder=4)
    if not rows:ax.text(.5,.5,'Aucune fixation mappée\nretenue dans cette fenêtre',transform=ax.transAxes,ha='center')


def main(sources,render_only=False):
    output=ROOT/'results'/'comparaison'/'positions_FND';output.mkdir(exist_ok=True)
    if render_only:
        audit=json.loads((output/'audit_positions_FND.json').read_text())
        with (output/'positions_FND_ordre_temps.csv').open(encoding='utf-8-sig') as f:
            all_rows=list(csv.DictReader(f))
        integer={'projet','ordre_visible','index_fixation_Tobii','nombre_points'}
        rows=[{k:v if k=='sujet' else (int(v) if k in integer else float(v)) for k,v in row.items()} for row in all_rows]
        data=[([r for r in rows if r['sujet']==a['sujet']],a) for a in audit]
    else:
        with ThreadPoolExecutor(max_workers=2) as pool:
            data=list(pool.map(lambda n:extract(n,sources),range(1,8)))
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'figure.facecolor':'#f8fafc','axes.facecolor':'#f8fafc'})
    fig,axes=plt.subplots(2,4,figsize=(17,13))
    for ax,(rows,audit) in zip(axes.flat,data):draw(ax,rows,audit,small=True)
    axes.flat[7].axis('off')
    axes.flat[7].text(.05,.98,'COMMENT LIRE\n\n1 → 2 → 3 : ordre des positions\nmappées visibles.\n\nViolet : plus tôt après FND.\nJaune : plus tard (jusqu’à 8 s).\n\nChaque point résume un segment\nde fixation identifié par Tobii.\n\nLes points manquants ne sont\npas reconstruits.\n\nLe fond de l’interface n’est\npas représenté.\n\nBas du FND = zone d’action :\nhypothèse à confirmer.\nAucun clic n’est identifié.',transform=axes.flat[7].transAxes,va='top',linespacing=1.45,fontsize=11)
    fig.suptitle('ALERT_FND · Où le regard se pose, et dans quel ordre — sept sujets',x=.055,ha='left',fontsize=20,fontweight='bold',y=.98)
    fig.text(.055,.935,'Même fenêtre : 0 à 8 s après l’apparition annotée par Élie. Numéros chronologiques et couleur du temps.',fontsize=12,color='#526174')
    fig.subplots_adjust(left=.055,right=.89,top=.86,bottom=.12,hspace=.35,wspace=.55)
    cax=fig.add_axes([.935,.22,.012,.55]);fig.colorbar(ScalarMappable(norm=Normalize(0,END),cmap='viridis'),cax=cax,label='Temps depuis l’apparition annotée de FND (s)')
    fig.text(.055,.025,'Ordre des points disponibles uniquement : des regards intermédiaires peuvent manquer. Les numéros ne correspondent pas entre sujets.\nPositions normalisées sur chaque image FND ; images/AOI différentes entre projets, sans équivalence géométrique démontrée.\nLa couverture est la part des échantillons oculaires avec regard valide mappé dans l’image sur ces 8 s ; elle ne mesure pas le temps de regard vers le FND.',fontsize=10,color='#526174')
    fig.savefig(output/'positions_FND_7_sujets_ordre_temps.png',dpi=180)
    fig.savefig(output/'positions_FND_7_sujets_ordre_temps.svg',dpi=180)
    with PdfPages(output/'positions_FND_7_sujets_ordre_temps.pdf') as pdf:
        pdf.savefig(fig);plt.close(fig)
        for rows,audit in data:
            f,ax=plt.subplots(figsize=(8,11));draw(ax,rows,audit)
            f.subplots_adjust(left=.15,right=.8,top=.87,bottom=.19)
            cax=f.add_axes([.87,.28,.025,.48]);f.colorbar(ScalarMappable(norm=Normalize(0,END),cmap='viridis'),cax=cax,label='Secondes après l’apparition annotée')
            f.suptitle('ALERT_FND · Positions et ordre du regard',fontsize=17,fontweight='bold',y=.96)
            f.text(.1,.075,'Numéros = ordre des segments mappés visibles ; des regards peuvent manquer.\nPoint = position médiane sur un segment de fixation, sans fond d’interface.\nAucune trajectoire n’est interpolée entre les points. Aucun clic inféré.\nHypothèse non confirmée : acquittement vers le bas de la tablette.',fontsize=10,color='#526174')
            f.savefig(output/f"{audit['sujet']}_positions_FND_ordre_temps.png",dpi=180)
            pdf.savefig(f);plt.close(f)
    all_rows=[r for rows,_ in data for r in rows]
    with (output/'positions_FND_ordre_temps.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(all_rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(all_rows)
    (output/'audit_positions_FND.json').write_text(json.dumps([a for _,a in data],ensure_ascii=False,indent=2))
    for _,a in data:print(json.dumps(a,ensure_ascii=False),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--sources',type=Path)
    group.add_argument('--render-only',action='store_true',help='Redessiner depuis les résultats agrégés publiés, sans Excel.')
    args=parser.parse_args();main(args.sources,args.render_only)
