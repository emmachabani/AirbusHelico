"""Directions horizontale/verticale et points FND, 0–12 s, sans PDF.
python3 scripts/regard_fnd_7_sujets.py --sources /workspace/attachments
"""
import argparse,csv,hashlib,json,os,tempfile
from pathlib import Path
import numpy as np
import openpyxl
os.environ.setdefault('MPLCONFIGDIR',tempfile.gettempdir()+'/tobii-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.lines import Line2D
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/comparaison/directions_positions_FND'
NORM=Normalize(0,12)

def extract(subject,sources):
    project=1 if int(subject[3:])<=4 else 2
    media='HLX FND1' if project==1 else 'HLX FND'
    mlname=f'AOI hit [{media} - '+('ML_HLX_FND1]' if project==1 else 'HLX_FND_ML]')
    source,=list(Path(sources).rglob(subject+'.xlsx'))
    with (ROOT/'results'/subject/'alertes.csv').open(encoding='utf-8-sig') as f:
        onset=float(next(e for e in csv.DictReader(f) if e['alerte']=='ALERT_FND')['temps_s'])
    w=openpyxl.load_workbook(source,read_only=True,data_only=True);it=w.active.values;headers=next(it)
    def key(prefix):
        matches=[i for i,h in enumerate(headers) if h==prefix or h.startswith(prefix+' [')]
        if len(matches)!=1:raise ValueError(prefix)
        return matches[0]
    names=['Validity left','Validity right',f'Mapped gaze point X [{media}]',f'Mapped gaze point Y [{media}]',f'Width [{media}]',f'Height [{media}]',mlname,'Eye movement type','Eye movement type index']
    names += [f'Gaze direction {eye} {axis}' for eye in ['left','right'] for axis in 'XYZ']
    inds=[key(n) for n in names];sensor=key('Sensor');records=[];times=[]
    for row in it:
        if len(row)<=sensor or row[sensor]!='Eye Tracker':continue
        t=float(row[0])/1e6-onset
        if -.5<=t<=12:
            times.append(t);records.append([row[i] if i<len(row) else None for i in inds])
    w.close();a=np.array(records,dtype=object);t=np.array(times)
    assert len(t)>0 and np.all(np.diff(t)>0)
    def num(i):return np.array([np.nan if x is None else float(x) for x in a[:,i]])
    valid=(a[:,0]=='Valid')|(a[:,1]=='Valid')
    mx,my,width,height,ml=[num(i) for i in range(2,7)]
    inside=valid&np.isfinite(mx)&np.isfinite(my)&(mx>=0)&(my>=0)&(mx<=width)&(my<=height)
    choices={}
    for eye,col,offset in [('left',0,9),('right',1,12)]:
        r=np.column_stack([num(i) for i in range(offset,offset+3)])
        ok=(a[:,col]=='Valid')&np.isfinite(r).all(axis=1)&(np.linalg.norm(r,axis=1)>0)
        angles=np.degrees(np.column_stack([np.arctan2(r[:,0],r[:,2]),np.arctan2(r[:,1],np.hypot(r[:,0],r[:,2]))]));angles[~ok]=np.nan
        choices[eye]=(angles,ok)
    eligible=[eye for eye,(angle,ok) in choices.items() if (ok&(t<0)).sum()>=10]
    if not eligible:raise ValueError(subject+': référence pré-alarme insuffisante')
    eye=max(eligible,key=lambda e:(choices[e][1]&(t>=0)).sum())
    angles,ok=choices[eye];baseline=np.nanmedian(angles[t<0],axis=0);delta=angles-baseline
    post=t>=0
    # Segments de fixation réellement mappés ; aucune liaison entre les lacunes.
    segments=[]
    for i in np.flatnonzero(post&inside&(a[:,7]=='Fixation')):
        if not segments or a[i,8]!=a[segments[-1][-1],8] or t[i]-t[segments[-1][-1]]>.05:segments.append([])
        segments[-1].append(i)
    segments=[s for s in segments if len(s)>=5 and t[s[-1]]-t[s[0]]>=.04]
    points=[{'ordre':k+1,'debut_s':float(t[s[0]]),'fin_s':float(t[s[-1]]),'x_pct':float(np.median(100*mx[s]/width[s])),'y_pct':float(np.median(100*my[s]/height[s]))} for k,s in enumerate(segments)]
    audit={'sujet':subject,'projet':project,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'alarme_FND_s':onset,'oeil_direction':eye,'baseline_deg':baseline.tolist(),'reference_points_valides':int((ok&(t<0)).sum()),'echantillons_apres_alarme':int(post.sum()),'direction_valide':int((post&ok).sum()),'points_FND':int((post&inside).sum()),'points_ML':int((post&inside&(ml==1)).sum()),'points_FND_hors_ML':int((post&inside&(ml==0)).sum()),'points_FND_statut_ML_inconnu':int((post&inside&~np.isin(ml,[0,1])).sum()),'positions_numerotees':points}
    return dict(subject=subject,project=project,t=t,delta=delta,ok=ok,inside=inside,mx=mx/width*100,my=my/height*100,ml=ml,audit=audit)

def draw_row(axes,d):
    t=d['t'];post=t>=0
    # Couleurs continues uniquement pour les points ; courbes de direction distinctes.
    for j,ax in enumerate(axes[:2]):
        ax.plot(t[post],d['delta'][post,j],color=['#3973a5','#b56b31'][j],lw=.9)
        missing=~d['inside'];edges=np.diff(np.r_[False,missing,False].astype(int))
        for s,e in zip(np.flatnonzero(edges==1),np.flatnonzero(edges==-1)):
            start=max(0,t[s]);end=min(12,t[e] if e<len(t) else t[-1])
            if end>start:ax.axvspan(start,end,color='#e0e5ee',alpha=.65,zorder=-1)
        ax.axhline(0,color='#8b929b',lw=.6,ls='--');ax.set_xlim(0,12);ax.set_xlabel('Secondes après ALERT_FND');ax.grid(alpha=.15)
        ax.set_title(('Direction horizontale' if j==0 else 'Direction verticale')+' · écart à avant l’alarme',fontsize=10)
        ax.set_ylabel('Degrés')
    ax=axes[2]
    for mask,marker in [(d['inside']&(d['ml']==0),'o'),(d['inside']&(d['ml']==1),'^'),(d['inside']&~np.isin(d['ml'],[0,1]),'x')]:
        mask=mask&post
        if mask.any():ax.scatter(d['mx'][mask],d['my'][mask],c=t[mask],cmap='viridis',norm=NORM,s=12,marker=marker,alpha=.75,linewidths=.3)
    for point in d['audit']['positions_numerotees']:
        ax.annotate(str(point['ordre']),(point['x_pct'],point['y_pct']),xytext=(5,5),textcoords='offset points',fontsize=7,bbox=dict(facecolor='white',edgecolor='none',alpha=.8,pad=.4))
    ax.set(xlim=(0,100),ylim=(100,0),xlabel='Position horizontale (% largeur FND)',ylabel='Position verticale (% hauteur FND)')
    ax.set_title('Points mappés sur le FND · couleur = temps',fontsize=10);ax.grid(alpha=.15)
    ax.text(.01,.02,f"{d['audit']['points_ML']} points dans ML",transform=ax.transAxes,fontsize=8)
    axes[0].text(-.17,1.14,f"{d['subject']} · P{d['project']} · œil {'G' if d['audit']['oeil_direction']=='left' else 'D'}",transform=axes[0].transAxes,fontweight='bold',fontsize=11)

def decorate(fig):
    fig.legend(handles=[Line2D([],[],marker='o',ls='',color='#555',label='FND hors ML'),Line2D([],[],marker='^',ls='',color='#555',label='ML incluse dans le FND'),Line2D([],[],marker='x',ls='',color='#555',label='FND, statut ML inconnu')],loc='lower left',bbox_to_anchor=(.06,.013),ncol=3,fontsize=9)
    cax=fig.add_axes([.73,.075 if fig.get_figheight()<10 else .028,.22,.012]);cb=fig.colorbar(plt.cm.ScalarMappable(norm=NORM,cmap='viridis'),cax=cax,orientation='horizontal');cb.set_label('Secondes après ALERT_FND',fontsize=8);cb.ax.tick_params(labelsize=8)

def main(sources,render_only=False):
    cache=ROOT/'local_analysis/directions_positions_FND';cache.mkdir(parents=True,exist_ok=True)
    data=[]
    for n in range(1,8):
        if render_only:
            d=np.load(cache/f'SUJ{n}.npz',allow_pickle=True)['data'].item()
        else:
            d=extract(f'SUJ{n}',sources);np.savez_compressed(cache/f'SUJ{n}.npz',data=np.array(d,dtype=object))
        data.append(d);print(f"SUJ{n}: {d['audit']['points_FND']} points FND, {d['audit']['points_ML']} ML",flush=True)
    OUT.mkdir(parents=True,exist_ok=True)
    limits=[]
    for j in range(2):
        values=np.concatenate([d['delta'][(d['t']>=0)&d['ok'],j] for d in data]);lo,hi=float(values.min()),float(values.max());pad=max(2,(hi-lo)*.05);limits.append((lo-pad,hi+pad))
    for d in data:
        fig,axes=plt.subplots(1,3,figsize=(17,5.8),gridspec_kw={'width_ratios':[1,1,1]});fig.subplots_adjust(left=.06,right=.97,top=.77,bottom=.25,wspace=.3)
        draw_row(axes,d)
        for j in range(2):axes[j].set_ylim(*limits[j])
        fig.suptitle(d['subject']+' · Après ALERT_FND : mouvements du regard et positions sur le FND',fontsize=16,fontweight='bold',y=.96)
        fig.text(.06,.86,'Fond gris : position non mappée dans le FND. Les courbes continuent si la direction oculaire est mesurée. Aucun regard interpolé.',fontsize=10)
        fig.text(.06,.14,'Numéros : ordre des segments de fixation mappés disponibles ; des regards intermédiaires peuvent manquer. Aucun contour ML reconstitué.',fontsize=9)
        decorate(fig)
        for ext in ['png','svg']:fig.savefig(OUT/f"{d['subject']}_directions_positions_FND.{ext}",dpi=160)
        plt.close(fig)
    fig,axes=plt.subplots(7,3,figsize=(18,23));fig.subplots_adjust(left=.07,right=.97,top=.94,bottom=.065,hspace=.8,wspace=.3)
    for row,d in zip(axes,data):
        draw_row(row,d)
        for j in range(2):row[j].set_ylim(*limits[j])
    fig.suptitle('ALERT_FND · Sept sujets · Directions du regard et positions sur le FND',fontsize=19,fontweight='bold',y=.982)
    fig.text(.07,.96,'0–12 s après le marqueur manuel · gris : non mappé · angles relatifs à −0,5–0 s · échelles communes · tête non compensée',fontsize=11)
    decorate(fig)
    for ext in ['png','svg']:fig.savefig(OUT/f'7_sujets_directions_positions_FND.{ext}',dpi=145)
    plt.close(fig)
    audits=[d['audit'] for d in data]
    for a in audits:
        assert a['points_FND']==a['points_ML']+a['points_FND_hors_ML']+a['points_FND_statut_ML_inconnu']
    (OUT/'audit_directions_positions_FND.json').write_text(json.dumps({'fenetre_s':[0,12],'reference_s':[-.5,0],'limites_angles_deg':limits,'sujets':audits},ensure_ascii=False,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sources',default='/workspace/attachments');p.add_argument('--render-only',action='store_true');args=p.parse_args();main(args.sources,args.render_only)
