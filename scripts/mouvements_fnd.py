"""Recherche exploratoire de réorientations ressemblant à SUJ1 autour d'ALERT_FND.

python3 scripts/extraire_fnd.py --sources /workspace/attachments
python3 scripts/mouvements_fnd.py
Cache local exclu de Git. Les sorties sont agrégées ; aucun lieu du regard ni
temps de détection n'est inféré pour les sujets dépourvus d'AOI pertinentes.
"""
import csv
import itertools
import json
import os
import tempfile
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR',str(Path(tempfile.gettempdir())/'tobii-matplotlib'))
os.environ.setdefault('XDG_CACHE_HOME',str(Path(tempfile.gettempdir())/'tobii-cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
BIN=.05
PARAMETERS=list(itertools.product([.5,.75],[1.5,2.],[30.,45.]))


def load_subject(n):
    # Caches créés localement par extraire_fnd.py, jamais des fichiers non fiables.
    d=np.load(ROOT/'local_analysis'/'fnd'/f'SUJ{n}.npz',allow_pickle=True)
    a=d['eye'];names=list(d['names']);t=a[:,0].astype(float)
    ray=a[:,3:6].astype(float)
    norms=np.linalg.norm(ray,axis=1)
    valid=(a[:,names.index('Validity left')]=='Valid')&np.isfinite(ray).all(axis=1)
    # Les vecteurs dits « norm » sont uniformément exportés à une échelle 100000.
    # atan2 annule ce facteur commun ; aucune correction par composante inventée.
    if not valid.any() or not np.all(np.abs(norms[valid]/100000-1)<.01):
        raise ValueError(f'SUJ{n} : échelle des vecteurs de direction non validée.')
    angles=np.degrees(np.column_stack([np.arctan2(ray[:,0],ray[:,2]),
        np.arctan2(ray[:,1],np.hypot(ray[:,0],ray[:,2]))]))
    angles[~valid]=np.nan
    return {'t':t,'angles':angles,'valid':valid,'eye':a,'names':names,
        'gyro':d['gyro'].astype(float),'norm_min':float(norms[valid].min()),
        'norm_max':float(norms[valid].max()),'source_sha256':str(d['source_sha256'])}


def baseline(s,start):
    mask=(s['t']>=start-.5)&(s['t']<start)&s['valid']
    if mask.sum()<20:return None,None
    center=np.median(s['angles'][mask],axis=0)
    radius=float(np.percentile(np.linalg.norm(s['angles'][mask]-center,axis=1),90))
    return center,radius


def binned(s,start,center):
    times=np.arange(-.475,5.,BIN)+start
    values=np.full((len(times),2),np.nan)
    for i,t in enumerate(times):
        mask=(s['t']>=t-BIN/2)&(s['t']<t+BIN/2)&s['valid']
        if mask.sum()>=3:values[i]=np.median(s['angles'][mask],axis=0)-center
    return times,values


def candidate(s,start,reference,lo=.5,hi=2.,cone=45.):
    center,radius=baseline(s,start)
    if center is None:return {'time':None,'reason':'moins de 20 mesures de référence','radius':None}
    amplitude=np.linalg.norm(reference)
    if radius>.5*amplitude:return {'time':None,'reason':'regard initial trop dispersé pour cette heuristique','radius':radius}
    times,delta=binned(s,start,center)
    norms=np.linalg.norm(delta,axis=1)
    cosine=np.divide(delta@reference,norms*amplitude,out=np.zeros(len(times)),where=norms>0)
    match=(times>=start)&(norms>=lo*amplitude)&(norms<=hi*amplitude)&(cosine>=np.cos(np.radians(cone)))
    hits=np.flatnonzero(match[:-1]&match[1:])
    if not len(hits):return {'time':None,'reason':'aucun déplacement répondant aux seuils','radius':radius}
    i=int(hits[0]);pos=np.median(delta[i:i+2],axis=0)
    return {'time':float(times[i]-BIN/2-start),'reason':'candidat géométrique, destination inconnue',
        'radius':radius,'amplitude':float(np.linalg.norm(pos)),
        'angle':float(np.degrees(np.arccos(np.clip(pos@reference/(np.linalg.norm(pos)*amplitude),-1,1)))),
        'position':pos.tolist()}


def gyro_relative(s):
    g=s['gyro'];t=g[:,0];v=g[:,1:4]
    good=np.isfinite(v).all(axis=1);pre=good&(t>=-2)&(t<0)
    if pre.sum()<20:return t,np.full(len(t),np.nan)
    centered=v-np.median(v[pre],axis=0)
    magnitude=np.linalg.norm(centered,axis=1)
    scale=np.median(magnitude[pre])
    if scale<=0:return t,np.full(len(t),np.nan)
    return t,np.where(good,magnitude/scale,np.nan)


def main():
    subjects={n:load_subject(n) for n in range(1,8)}
    ref=subjects[1];a=ref['eye'];t=ref['t'];h=ref['names']
    pre=(t>=-.5)&(t<0)&ref['valid']&(a[:,h.index('AOI hit [Recording 5 - Main screen]')]==1)
    post=(t>=0)&ref['valid']&(a[:,h.index('AOI hit [Recording 5 - FND]')]==1)
    if pre.sum()<20 or not post.any():raise ValueError('Référence SUJ1 non vérifiable par AOI.')
    arrival=float(t[post][0]);post&=(t<arrival+.25)
    if post.sum()<10:raise ValueError('Pas assez de points de regard SUJ1 dans FND.')
    reference=np.median(ref['angles'][post],axis=0)-np.median(ref['angles'][pre],axis=0)
    amp=float(np.linalg.norm(reference));unit=reference/amp
    xy=a[:,1:3].astype(float)
    pixel_ref=(np.median(xy[post],axis=0)-np.median(xy[pre],axis=0)).tolist()
    output=ROOT/'results'/'comparaison'/'mouvements_FND';output.mkdir(exist_ok=True)
    rows=[];traces={}
    for n,s in subjects.items():
        target=candidate(s,0,reference)
        control=candidate(s,-7,reference)
        sensitivity=[candidate(s,0,reference,*params) for params in PARAMETERS]
        found=[c['time'] for c in sensitivity if c['time'] is not None]
        base,radius=baseline(s,0)
        times,delta=binned(s,0,base) if base is not None else (np.arange(-.475,5.,BIN),np.full((110,2),np.nan))
        projection=delta@unit;transverse=delta@np.array([-unit[1],unit[0]])
        tg,gyro=gyro_relative(s);response=(tg>=0)&(tg<=5)
        coverage=float(np.mean(np.isfinite(delta).all(axis=1)[times>=0])*100)
        rows.append({'sujet':f'SUJ{n}','projet':1 if n<=4 else 2,
            'candidat_apres_alarme_s':target['time'],'statut':target['reason'],
            'amplitude_angulaire_candidat_deg':target.get('amplitude'),
            'ecart_direction_reference_deg':target.get('angle'),
            'dispersion_initiale_p90_deg':radius,'couverture_bins_50ms_post_pct':coverage,
            'candidat_periode_temoin_avant_alarme':control['time'] is not None,
            'statut_periode_temoin':control['reason'],
            'dispersion_initiale_temoin_p90_deg':control['radius'],
            'delai_candidat_dans_periode_temoin_s':control['time'],
            'sensibilite_configurations_avec_candidat_sur_8':len(found),
            'sensibilite_delai_min_s':min(found) if found else None,
            'sensibilite_delai_max_s':max(found) if found else None,
            'gyro_relatif_p95_0_5s':float(np.nanpercentile(gyro[response],95)) if np.isfinite(gyro[response]).any() else None,
            'reserve':'Apparition FND approximative selon les notes' if n==3 else 'Destination du regard non validée par cette méthode'})
        traces[n]=(times,delta,projection,transverse,tg,gyro,target)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,
        'figure.facecolor':'#f8fafc','axes.facecolor':'#f8fafc'})
    fig,axes=plt.subplots(7,2,figsize=(16,15),sharex=True)
    for n,s in subjects.items():
        times,delta,projection,transverse,tg,gyro,target=traces[n]
        ax=axes[n-1,0];ax.axhspan(.5*amp,2*amp,color='#dceae9')
        ax.plot(times,projection,color='#087f83',lw=1.8,label='Projection vers la direction SUJ1')
        ax.plot(times,transverse,color='#64748b',ls=':',lw=1,label='Composante perpendiculaire')
        ax.axhline(amp,color='#1c6b6c',ls='--',lw=.7);ax.axhline(0,color='#aab3bd',lw=.7)
        ax.axvline(0,color='#b34848',ls='--',lw=1)
        if target['time'] is not None:ax.axvline(target['time'],color='#d38b24',lw=1.5)
        label=f"SUJ{n} · P{1 if n<=4 else 2}"+(' · repère approximatif' if n==3 else '')
        result=f"Candidat {target['time']:.2f} s" if target['time'] is not None else 'Aucun candidat selon ces seuils'
        if rows[n-1]['candidat_periode_temoin_avant_alarme']:result+=' · aussi présent avant l’alarme'
        elif rows[n-1]['statut_periode_temoin']!='aucun déplacement répondant aux seuils':result+=' · témoin non évaluable'
        ax.set_title(label+' — '+result,loc='left',fontsize=10,fontweight='bold')
        ax.set_ylabel('Écart angulaire (°)');ax.set_ylim(-50,65);ax.grid(alpha=.15)
        ax=axes[n-1,1];window=(tg>=-.5)&(tg<=5)
        ax.plot(tg[window],gyro[window],color='#76669a',lw=.7)
        ax.axvline(0,color='#b34848',ls='--',lw=1)
        ax.axhline(1,color='#aab3bd',ls=':',lw=.7)
        ax.set_yscale('symlog',linthresh=1);ax.set_ylim(0,max(3,float(np.nanmax(gyro[window]))*1.1))
        ax.set_ylabel('Activité gyro relative');ax.grid(alpha=.15)
        ax.set_title('Gyroscope : activité relative au niveau médian des 2 s précédentes',loc='left',fontsize=9)
    for ax in axes[-1]:ax.set_xlabel('Temps depuis l’apparition annotée de FND (s)');ax.set_xlim(-.5,5)
    fig.suptitle('ALERT_FND · Recherche exploratoire de mouvements ressemblant au passage vers le FND de SUJ1',x=.04,ha='left',fontsize=17,fontweight='bold',y=.99)
    fig.text(.04,.956,f'Référence SUJ1 confirmée par les AOI : premier regard FND à {arrival:.2f} s ; déplacement angulaire ≈ {amp:.1f}°.\nVert : mouvement dans la direction de cette référence · Orange : premier candidat · Gris pointillé : déplacement perpendiculaire.',fontsize=11)
    fig.text(.04,.035,'Un candidat n’identifie ni le FND ni une détection. Les angles décrivent les yeux par rapport aux lunettes, pas la direction dans la pièce.\nBande verte : amplitude 50–200 % de SUJ1 ; cône ±45°, deux bins consécutifs de 50 ms. Témoin : recherche identique de −7 à −2 s.\nLe gyroscope est montré en unités relatives, axe non linéaire et échelles propres à chaque sujet ; aucune intégration/correction de tête.',fontsize=10,color='#526174')
    fig.subplots_adjust(left=.08,right=.97,top=.9,bottom=.1,hspace=.75,wspace=.28)
    trajectory,axs=plt.subplots(2,4,figsize=(16,9),sharex=True,sharey=True)
    for n in range(1,8):
        ax=axs.flat[n-1];times,delta,*_=traces[n]
        use=times>=0
        ax.plot(delta[use,0],-delta[use,1],color='#c5cdd6',lw=.6)
        points=ax.scatter(delta[use,0],-delta[use,1],c=times[use],cmap='viridis',vmin=0,vmax=5,s=10)
        ax.arrow(0,0,reference[0],-reference[1],width=.3,color='#c44d43',length_includes_head=True)
        ax.scatter([0],[0],color='black',marker='+',s=60)
        ax.set_title(f'SUJ{n} · P{1 if n<=4 else 2}',fontweight='bold')
        ax.set_xlim(-45,45);ax.set_ylim(50,-40);ax.grid(alpha=.15)
        ax.set_xlabel('Variation horizontale (°)');ax.set_ylabel('Variation verticale (°)')
    axs.flat[7].axis('off')
    axs.flat[7].text(0,1,'Flèche rouge : déplacement\nroute → FND de SUJ1.\n\nCroix : position médiane des\n0,5 s avant l’alarme.\n\nPoints : médianes de bins\nde 50 ms après l’alarme.\n\nMême amplitude ≠ même lieu.\nLes rotations de tête ne\nsont pas compensées.',transform=axs.flat[7].transAxes,va='top',fontsize=10,linespacing=1.4)
    trajectory.suptitle('ALERT_FND · Trajectoires angulaires relatives à la position du regard avant l’alarme',fontsize=17,fontweight='bold')
    trajectory.subplots_adjust(left=.06,right=.9,top=.9,bottom=.13,hspace=.4,wspace=.4)
    cax=trajectory.add_axes([.93,.2,.012,.6]);trajectory.colorbar(points,cax=cax,label='Temps après l’alarme (s)')
    trajectory.text(.06,.025,'Œil gauche valide uniquement. Projection dans le repère des lunettes : aucune reconstruction du regard dans la scène.\nSUJ3 : apparition approximative. Analyse descriptive d’une occurrence par sujet, sans test statistique de détection.',fontsize=10,color='#526174')
    overview,ax=plt.subplots(figsize=(13,8))
    for i,row in enumerate(rows):
        delay=row['candidat_apres_alarme_s'];witness=row['candidat_periode_temoin_avant_alarme']
        if delay is None:
            ax.text(.08,i,f"Aucun candidat · couverture {row['couverture_bins_50ms_post_pct']:.0f} %",va='center',color='#637082')
        else:
            color='#c68b2c' if witness else '#087f83'
            ax.errorbar(delay,i,xerr=[[delay-row['sensibilite_delai_min_s']],[row['sensibilite_delai_max_s']-delay]],fmt='o',color=color,capsize=4,markersize=9)
            label=f"{delay:.2f} s"+(' · aussi observé avant l’alarme' if witness else '')
            if i==0:label+=' · référence d’apprentissage'
            if i==2:label+=' · apparition approximative'
            if row['statut_periode_temoin'] not in ['aucun déplacement répondant aux seuils','candidat géométrique, destination inconnue']:
                label+=' · témoin non évaluable'
            ax.text(max(delay,row['sensibilite_delai_max_s'])+.12,i,label,va='center',fontsize=11)
    ax.set_yticks(range(7),[f"SUJ{n} · P{1 if n<=4 else 2}" for n in range(1,8)])
    ax.set_ylim(6.5,-.5);ax.set_xlim(0,6.5)
    ax.set_xlabel('Premier mouvement candidat après l’apparition annotée (s)')
    ax.grid(axis='x',alpha=.15)
    overview.suptitle('ALERT_FND · Peut-on repérer une réorientation ressemblant à celle de SUJ1 ?',x=.07,ha='left',fontsize=17,fontweight='bold')
    overview.text(.07,.86,f'Référence : regard route → tablette confirmé par AOI chez SUJ1, déplacement angulaire ≈ {amp:.1f}°.\nLes points représentent des candidats géométriques, pas une détection ni un lieu de regard confirmé.',fontsize=11,color='#526174')
    overview.text(.07,.04,'Barres : variation sur huit combinaisons de seuils exploratoires ; pas des intervalles de confiance.\nSUJ1 : seuil de mouvement à 0,60 s ; entrée dans l’AOI FND à 0,79 s (mesures différentes).\nOrange : mouvement semblable avant l’alarme. Témoins SUJ1/2/5 non évaluables : regard initial trop dispersé.\nSUJ4 : données partielles, pas une preuve d’absence de réaction. Mouvements de tête documentés sans reconstruction du regard dans la pièce.',fontsize=10,color='#526174')
    overview.subplots_adjust(left=.13,right=.97,top=.77,bottom=.23)
    with PdfPages(output/'ALERT_FND_mouvements_exploratoires.pdf') as pdf:
        for name,f in [('00_synthese_reorientations',overview),('01_mouvements_et_tete',fig),('02_trajectoires_angulaires',trajectory)]:
            for ext in ['png','svg']:f.savefig(output/f'{name}.{ext}',dpi=160)
            pdf.savefig(f);plt.close(f)
    with (output/'candidats_FND.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    audit={'reference_suj1':{'arrivee_FND_s':arrival,'deplacement_pixels':pixel_ref,
        'deplacement_yaw_pitch_deg':reference.tolist(),'amplitude_deg':amp},
        'methode':{'repere':'direction œil gauche / lunettes','bin_s':BIN,'points_valides_min_par_bin':3,
            'baseline_s':[-.5,0],'fenetre_s':[0,5],'temoin_s':[-7,-2],
            'rapport_amplitudes':[.5,2],'cone_deg':45,'bins_consecutifs':2,
            'sensibilite_parametres':PARAMETERS,'gyro':'indice relatif, aucune intégration/correction'},
        'audit_sources':{f'SUJ{n}':{k:s[k] for k in ['source_sha256','norm_min','norm_max']} for n,s in subjects.items()},
        'limites':['Seuils heuristiques, pas de significativité statistique.',
            'Référence apprise sur SUJ1 et évaluée sur SUJ1 : contrôle de cohérence, pas validation indépendante.',
            'Témoin antérieur non garanti exempt d’autres événements ou regards vers la tablette.',
            'Bin de 50 ms ; aucune interpolation à travers les lacunes.',
            'Angles yaw/pitch : approximation locale de déplacement, pas distance géodésique ni lieu visé.',
            'Pas de reconstruction de tête ; gyro relatif seulement, unités absolues exportées ambiguës.',
            'Un candidat peut être un regard vers tout autre objet ; absence de candidat ne prouve pas absence de détection.']}
    (output/'methode_et_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    for row in rows:print(json.dumps(row,ensure_ascii=False))


if __name__=='__main__':main()
