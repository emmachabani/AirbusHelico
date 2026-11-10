"""Audit exploratoire des coupures SUJ1 ou SUJ2, sans AOI vidéo ni interpolation.
python3 scripts/coupures_mapping_suj1.py --sources /workspace/attachments
"""
import argparse,csv,hashlib,json,os,tempfile
from pathlib import Path
import numpy as np
import openpyxl
os.environ.setdefault('MPLCONFIGDIR',tempfile.gettempdir()+'/tobii-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]

def main(sources,subject='SUJ1'):
    OUT=ROOT/'results'/subject/'coupures_mapping'
    source,=list(Path(sources).rglob(f'{subject}.xlsx'))
    w=openpyxl.load_workbook(source,read_only=True,data_only=True)
    rows=w.active.values;headers=next(rows)
    def key(prefix):
        found=[i for i,h in enumerate(headers) if h==prefix or h.startswith(prefix+' [')]
        if len(found)!=1:raise ValueError(prefix)
        return found[0]
    names=['Recording timestamp','Gaze point X','Gaze point Y','Validity left','Validity right',
      'Mapped gaze point X [HLX FND1]','Mapped gaze point Y [HLX FND1]',
      'Width [HLX FND1]','Height [HLX FND1]','Recording media width','Recording media height',
      'Eye movement type','AOI hit [HLX FND1 - ML_HLX_FND1]']
    names += [f'Gaze direction {eye} {axis}' for eye in ('left','right') for axis in 'XYZ']
    inds=[key(n) for n in names];sensor=key('Sensor');records=[]
    for row in rows:
        if len(row)>sensor and row[sensor]=='Eye Tracker':records.append([row[i] if i<len(row) else None for i in inds])
    w.close();a=np.array(records,dtype=object)
    def num(n):return np.array([np.nan if x is None else float(x) for x in a[:,names.index(n)]])
    t=num(names[0])/1e6
    assert np.all(np.diff(t)>0)
    dt=np.diff(t,append=t[-1]+np.median(np.diff(t)))
    vx,vy=num('Gaze point X'),num('Gaze point Y');video=np.column_stack((vx,vy))
    left=a[:,names.index('Validity left')]=='Valid';right=a[:,names.index('Validity right')]=='Valid'
    valid=(left|right)&np.isfinite(video).all(axis=1)
    mx,my=num(names[5]),num(names[6]);mw,mh=num(names[7]),num(names[8])
    mapped=valid&np.isfinite(mx)&np.isfinite(my)
    inside=mapped&(mx>=0)&(my>=0)&(mx<=mw)&(my<=mh)
    ml=num('AOI hit [HLX FND1 - ML_HLX_FND1]')
    types=a[:,names.index('Eye movement type')]
    rays={};angles={}
    for eye,v in [('left',left),('right',right)]:
        r=np.column_stack([num(f'Gaze direction {eye} {axis}') for axis in 'XYZ'])
        norm=np.linalg.norm(r,axis=1);ok=v&np.isfinite(r).all(axis=1)&(norm>0)
        r=np.divide(r,norm[:,None],out=np.full_like(r,np.nan),where=ok[:,None]);rays[eye]=r
        angles[eye]=np.degrees(np.column_stack((np.arctan2(r[:,0],r[:,2]),np.arctan2(r[:,1],np.hypot(r[:,0],r[:,2])))))
    def separation(u,v):return float(np.degrees(np.arccos(np.clip(np.dot(u,v),-1,1))))
    def center(r,mask):
        x=np.nanmedian(r[mask],axis=0);return x/np.linalg.norm(x)
    missing=~mapped
    edges=np.diff(np.r_[False,missing,False].astype(int));starts=np.flatnonzero(edges==1);ends=np.flatnonzero(edges==-1)
    gaps=[]
    for start,end in zip(starts,ends):
        begin=t[start];stop=t[end] if end<len(t) else t[-1]+dt[-1]
        mask=np.zeros(len(t),bool);mask[start:end]=True
        duration=stop-begin
        before=inside&(t>=begin-.15)&(t<begin)
        after=inside&(t>=stop)&(t<stop+.15)
        bounded=before.sum()>=5 and after.sum()>=5
        frac=float(np.sum(dt[mask&valid])/duration)
        eye=max(rays,key=lambda eye:np.isfinite(rays[eye][mask]).all(axis=1).sum())
        r=rays[eye];ok=np.isfinite(r).all(axis=1)
        metrics={'angle_avant_apres_deg':None,'excursion_p90_deg':None,'distance_bords_image_FND_pct_diagonale':None,'excursion_video_p90_pct_diagonale':None}
        stable=False;excursion=False
        if bounded and (before&ok).sum()>=5 and (after&ok).sum()>=5 and (mask&ok).sum()>=1:
            b=center(r,before&ok);e=center(r,after&ok)
            distances=np.degrees(np.arccos(np.clip(r[mask&ok]@b,-1,1)))
            excursion90=float(np.percentile(distances,90));angle=separation(b,e)
            map_before=np.median(np.column_stack((mx,my))[before],axis=0);map_after=np.median(np.column_stack((mx,my))[after],axis=0)
            mapdist=100*np.linalg.norm(map_after-map_before)/np.hypot(np.nanmedian(mw),np.nanmedian(mh))
            diag=np.hypot(np.nanmedian(num('Recording media width')),np.nanmedian(num('Recording media height')))
            vb=np.median(video[before],axis=0)
            v90=float(100*np.percentile(np.linalg.norm(video[mask&valid]-vb,axis=1),90)/diag)
            metrics=dict(angle_avant_apres_deg=angle,excursion_p90_deg=excursion90,distance_bords_image_FND_pct_diagonale=float(mapdist),excursion_video_p90_pct_diagonale=v90)
            stable=duration<=.25 and frac>=.9 and ok[mask].mean()>=.9 and angle<=2 and excursion90<=2 and mapdist<=5 and v90<=3
            excursion=frac>=.8 and angle<=3 and excursion90>=5 and v90>=5
        label='continuite_FND_compatible' if stable else 'excursion_retour_candidate' if excursion else 'regard_majoritairement_invalide' if frac<.5 else 'non_tranche'
        gaps.append(dict(coupure=len(gaps)+1,debut_s=float(begin),fin_s=float(stop),duree_s=float(duration),part_regard_valide=float(frac),ancrages_FND_avant_apres=bool(bounded),oeil_direction=eye,part_type_saccade=float(np.mean(types[mask]=='Saccade')),classe=label,**metrics))
    OUT.mkdir(parents=True,exist_ok=True)
    # Traces directement observées : aucune interpolation des coordonnées manquantes.
    with (ROOT/'results'/subject/'alertes.csv').open(encoding='utf-8-sig') as f:
        onset=float(next(e for e in csv.DictReader(f) if e['alerte']=='ALERT_FND')['temps_s'])
    zoom=(t>=onset-2)&(t<=onset+12)
    fig,axes=plt.subplots(3,1,figsize=(15,9),sharex=True)
    fig.subplots_adjust(top=.87,bottom=.12,hspace=.28)
    axes[0].plot(t[zoom]-onset,np.where(valid,vx,np.nan)[zoom],lw=.8,label='X vidéo')
    axes[0].plot(t[zoom]-onset,np.where(valid,vy,np.nan)[zoom],lw=.8,label='Y vidéo')
    axes[0].set_ylabel('Pixels vidéo');axes[0].legend(loc='upper right')
    for j,label in enumerate(['Horizontal','Vertical']):
        axes[1].plot(t[zoom]-onset,angles['left'][zoom,j],lw=.8,label=label)
    axes[1].set_ylabel('Direction œil gauche (°)');axes[1].legend(loc='upper right')
    axes[2].scatter(t[zoom&inside]-onset,100*my[zoom&inside]/mh[zoom&inside],s=6,label='Hauteur mappée sur FND')
    axes[2].set(ylabel='Hauteur sur photo FND (%)',ylim=(105,-5),xlabel='Secondes depuis le marqueur ALERT_FND')
    axes[2].legend(loc='upper right')
    for ax in axes:
        ax.axvline(0,color='#bd3b3b',ls='--');ax.grid(alpha=.2)
        for g in gaps:
            if g['debut_s']<onset+12 and g['fin_s']>onset-2:
                ax.axvspan(max(g['debut_s']-onset,-2),min(g['fin_s']-onset,12),color='#8799be',alpha=.12)
        ax.set_xlim(-2,12)
    fig.suptitle(f'{subject} · Regard mesuré pendant les coupures de mapping autour de FND',fontsize=17,fontweight='bold')
    fig.text(.12,.91,'Fond bleuté : mapping absent. Les positions vidéo et directions restent mesurées ; elles ne donnent pas seules le contour du FND.',fontsize=10)
    fig.text(.12,.03,'Coordonnées vidéo et angles : repères différents, sans compensation de tête. Aucun contour FND ni AOI vidéo manuelle utilisé.',fontsize=10)
    fig.savefig(OUT/'traces_autour_ALERT_FND.png',dpi=150);fig.savefig(OUT/'traces_autour_ALERT_FND.svg');plt.close(fig)

    with (OUT/f'coupures_{subject}.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(gaps[0]));writer.writeheader();writer.writerows(gaps)
    summary={'sujet':subject,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'echantillons':len(t),'types_mouvement':{str(x):int(np.sum(types==x)) for x in set(types)},'duree_observee_s':float(dt.sum()),'mapping_present_s':float(dt[mapped].sum()),'mapping_dans_FND_s':float(dt[inside].sum()),'mapping_hors_image_s':float(dt[mapped&~inside].sum()),'mapping_absent_regard_valide_s':float(dt[missing&valid].sum()),'mapping_absent_regard_invalide_s':float(dt[missing&~valid].sum()),'classes':{c:{'nombre':sum(g['classe']==c for g in gaps),'duree_s':sum(g['duree_s'] for g in gaps if g['classe']==c)} for c in sorted(set(g['classe'] for g in gaps))},'parametres':{'ancrages_avant_apres_s':.15,'ancrages_min_points':5,'continuite_duree_max_s':.25,'continuite_validite_min':.9,'continuite_angle_max_deg':2,'continuite_excursion_p90_max_deg':2,'continuite_distance_ancrages_max_pct_diag_FND':5,'continuite_excursion_video_p90_max_pct_diag':3,'excursion_validite_min':.8,'excursion_angle_retour_max_deg':3,'excursion_p90_min_deg':5,'excursion_video_p90_min_pct_diag':5},'limites':['Aucune AOI vidéo manuelle utilisée. Aucun point interpolé.','Les classes décrivent une compatibilité, pas une preuve de localisation.','Les saccades ne sont pas une preuve de sortie du FND ; mouvements de tête non compensés.','Les durées utilisent les intervalles entre échantillons, dernière mesure prolongée de la période médiane.']}
    events=list(csv.DictReader((ROOT/'results'/subject/'alertes.csv').open(encoding='utf-8-sig')))
    onset=float(next(e for e in events if e['alerte']=='ALERT_FND')['temps_s'])
    summary['coupures_autour_FND_moins2_plus12']=[g for g in gaps if g['fin_s']>onset-2 and g['debut_s']<onset+12]
    (OUT/f'audit_{subject}.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    colors={'continuite_FND_compatible':'#39a27b','excursion_retour_candidate':'#e69535','regard_majoritairement_invalide':'#c4c9d0','non_tranche':'#8799be'}
    fig,axes=plt.subplots(2,1,figsize=(16,7));fig.subplots_adjust(top=.84,bottom=.2,hspace=.6)
    for ax,(lo,hi,title) in zip(axes,[(t[0],t[-1],'Enregistrement complet'),(onset-2,onset+12,'Zoom ALERT_FND : temps depuis le marqueur manuel')]):
        origin=0 if ax is axes[0] else onset
        for g in gaps:
            ax.broken_barh([(g['debut_s']-origin,g['duree_s'])],(.72,.45),facecolors=colors[g['classe']])
        for mask,y,col in [(inside&(ml==1),.12,'#b25393'),(inside&(ml==0),.12,'#147e85')]:
            edges=np.diff(np.r_[False,mask,False].astype(int))
            for s,e in zip(np.flatnonzero(edges==1),np.flatnonzero(edges==-1)):
                ax.broken_barh([(t[s]-origin,float(dt[s:e].sum()))],(y,.35),facecolors=col)
        ax.set(xlim=(lo-origin,hi-origin),ylim=(0,1.35),yticks=[.3,.95],yticklabels=['FND mappé\nrose : ML / bleu-vert : hors ML','Coupures de mapping'],title=title,xlabel='Secondes');ax.grid(axis='x',alpha=.15)
    axes[1].axvline(0,color='#bd3b3b',ls='--')
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(color=v,label=k.replace('_',' ')) for k,v in colors.items()],loc='lower center',ncol=2,bbox_to_anchor=(.52,.065))
    fig.suptitle(f'{subject} · Peut-on interpréter les coupures du mapping FND ?',fontsize=18,fontweight='bold')
    fig.text(.15,.9,'Aucune AOI vidéo manuelle. Vert : continuité compatible ; orange : excursion avec retour candidate, destination inconnue.',fontsize=10)
    fig.text(.1,.025,'Aucune absence de mapping n’est automatiquement classée « hors FND ». Aucun regard n’est reconstruit.',fontsize=11)
    fig.savefig(OUT/f'coupures_mapping_{subject}.png',dpi=150);fig.savefig(OUT/f'coupures_mapping_{subject}.svg');plt.close(fig)
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sources',required=True);p.add_argument('--subject',choices=['SUJ1','SUJ2'],default='SUJ1');args=p.parse_args();main(args.sources,args.subject)
