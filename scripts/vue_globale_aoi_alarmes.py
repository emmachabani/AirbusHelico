"""Sept sujets × cinq alarmes, zones FND/ML et appuis externes, sans PDF.
python3 scripts/vue_globale_aoi_alarmes.py --sources /workspace/attachments
"""
import argparse,csv,json,hashlib,os,tempfile
from pathlib import Path
import numpy as np
import openpyxl
os.environ.setdefault('MPLCONFIGDIR',tempfile.gettempdir()+'/tobii-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/comparaison/vue_globale_AOI_alarmes'
ALARMS=['ALERT_FND','ALERT_ML_LARGE','ALERT_ML_LIGHT','ALERT_RED','ALERT_TEXT']
END=18.
COLORS={'FND_hors_ML':'#63b6d1','ML':'#9265b5','FND_ML_inconnu':'#e2bf64','indetermine':'#e5e8ed'}

def read(path):
    with path.open(encoding='utf-8-sig') as f:return list(csv.DictReader(f))

def extract(subject,sources):
    cache=ROOT/'local_analysis/vue_globale_AOI_alarmes';cache.mkdir(parents=True,exist_ok=True)
    source,=list(Path(sources).rglob(subject+'.xlsx'));sha=hashlib.sha256(source.read_bytes()).hexdigest()
    target=cache/(subject+'.npz')
    if target.exists():
        d=np.load(target,allow_pickle=False)
        if str(d['sha'])==sha:return {k:d[k] for k in d.files}
    project=1 if int(subject[3:])<=4 else 2
    media='HLX FND1' if project==1 else 'HLX FND';mlname=f'AOI hit [{media} - '+('ML_HLX_FND1]' if project==1 else 'HLX_FND_ML]')
    w=openpyxl.load_workbook(source,read_only=True,data_only=True);it=w.active.values;headers=next(it)
    def key(prefix):
        found=[i for i,h in enumerate(headers) if h==prefix or h.startswith(prefix+' [')]
        if len(found)!=1:raise ValueError(prefix)
        return found[0]
    prefixes=['Validity left','Validity right',f'Mapped gaze point X [{media}]',f'Mapped gaze point Y [{media}]',f'Width [{media}]',f'Height [{media}]',mlname]
    inds=[key(n) for n in prefixes];sensor=key('Sensor');rows=[];times=[]
    for row in it:
        if len(row)<=sensor or row[sensor]!='Eye Tracker':continue
        values=[row[i] if i<len(row) else None for i in inds]
        times.append(float(row[0])/1e6);rows.append(values)
    w.close();a=np.array(rows,dtype=object);t=np.array(times)
    assert np.all(np.diff(t)>0)
    valid=(a[:,0]=='Valid')|(a[:,1]=='Valid')
    def num(j):return np.array([np.nan if x is None else float(x) for x in a[:,j]])
    x,y,width,height,ml=[num(j) for j in range(2,7)]
    inside=valid&np.isfinite(x)&np.isfinite(y)&(x>=0)&(x<=width)&(y>=0)&(y<=height)
    state=np.zeros(len(t),dtype=np.int8);state[inside&(ml==0)]=1;state[inside&(ml==1)]=2;state[inside&~np.isin(ml,[0,1])]=3
    result=dict(t=t,state=state,valid=valid,sha=np.array(sha));np.savez_compressed(target,**result)
    return result

def main(sources):
    OUT.mkdir(parents=True,exist_ok=True)
    ack={(r['sujet'],r['type_alerte']):float(r['temps_declare']) for r in read(ROOT/'inputs/projet2/temps_reaction_declares.csv')}
    fig,axes=plt.subplots(7,5,figsize=(19,13),sharex=True,sharey=True)
    fig.patch.set_facecolor('#f8fafc');summary=[];spans=[];audits=[]
    for i in range(7):
        subject=f'SUJ{i+1}';project=1 if i<4 else 2;folder=ROOT/'results'/subject
        data=extract(subject,sources);t=data['t'];state=data['state'];dt=np.diff(t,append=t[-1]+np.median(np.diff(t)))
        dt=np.where(dt>.05,np.median(np.diff(t)),dt)
        events=read(folder/'alertes.csv');quality={r['alerte']:r['reserve'] for r in read(folder/'qualite_alertes.csv')}
        audits.append(dict(sujet=subject,source_sha256=str(data['sha'])))
        for j,alarm in enumerate(ALARMS):
            ax=axes[i,j];ax.set_facecolor(COLORS['indetermine']);ax.set(xlim=(0,END),ylim=(-.7,.7),yticks=[],xticks=[0,4,8,12,16,18]);ax.tick_params(axis='x',length=0,labelsize=8)
            for spine in ax.spines.values():spine.set_visible(False)
            if i==0:ax.set_title(alarm.replace('ALERT_',''),fontsize=12,fontweight='bold',pad=15)
            if j==0:ax.set_ylabel(f'{subject}\nProjet {project}',rotation=0,labelpad=40,va='center',fontsize=10,fontweight='bold')
            matches=[r for r in events if r['alerte']==alarm];assert len(matches)<=1
            value=ack.get((subject,alarm));note=quality.get(alarm,'')
            row=dict(sujet=subject,projet=project,alarme=alarm,repere_s='',appui_declare_s=value if value is not None else '',appui_place=0,ML_s='',FND_hors_ML_s='',FND_ML_inconnu_s='',indetermine_s='',reserve=note)
            if not matches:
                label='Repère absent'
                if 'Hors champ' in note:label+='\nHors champ signalé'
                if value is not None:label+=f'\nAppui fourni : {value:g} s'
                ax.text(.5,.5,label,transform=ax.transAxes,ha='center',va='center',fontsize=9,color='#637082')
                summary.append(row);continue
            onset=float(matches[0]['temps_s']);row['repere_s']=onset
            durations={k:0. for k in ['FND_hors_ML','ML','FND_ML_inconnu']}
            window=(t+dt>onset)&(t<onset+END);local=[]
            for k in np.flatnonzero(window&(state>0)):
                start=max(0.,float(t[k]-onset));end=min(END,float(t[k]+dt[k]-onset));name=['indetermine','FND_hors_ML','ML','FND_ML_inconnu'][state[k]]
                if end<=start:continue
                if local and local[-1]['etat']==name and abs(local[-1]['fin_s']-start)<1e-8:local[-1]['fin_s']=end
                else:local.append(dict(sujet=subject,alarme=alarm,etat=name,debut_s=start,fin_s=end))
                durations[name]+=end-start
            # Deux pistes imbriquées : tout point ML appartient aussi au FND.
            for y in [.18,-.18]:
                ax.broken_barh([(0,END)],(y-.12,.24),facecolors=COLORS['indetermine'],edgecolors='none')
            for span in local:
                interval=[(span['debut_s'],span['fin_s']-span['debut_s'])]
                ax.broken_barh(interval,(.06,.24),facecolors='#63b6d1',edgecolors='none')
                if span['etat']=='ML':
                    ax.broken_barh(interval,(-.30,.24),facecolors=COLORS['ML'],edgecolors='none')
                elif span['etat']=='FND_hors_ML':
                    ax.broken_barh(interval,(-.30,.24),facecolors='#ffffff',edgecolors='none')
                else:
                    ax.broken_barh(interval,(-.30,.24),facecolors=COLORS['FND_ML_inconnu'],edgecolors='none')
            for y,label in [(.18,'FND'),(-.18,'ML')]:
                ax.text(-.025,y,label,transform=ax.get_yaxis_transform(),ha='right',va='center',fontsize=6.5,color='#526174')
            spans.extend(local);durations['indetermine']=END-sum(durations.values());assert durations['indetermine']>=-1e-7
            row.update({k+'_s':v for k,v in durations.items()})
            ax.axvline(0,color='#b34848',ls='--',lw=1)
            if value is not None:
                ax.axvline(value,color='#ae3f70',ls=':',lw=1.3);ax.scatter(value,-.48,marker='*',color='#ae3f70',s=65,zorder=5)
                ax.text(value+.25,-.49,f'{value:g} s',fontsize=8,color='#96335e',va='center');row['appui_place']=1
            reserve='Publicité signalée' if 'Publicité' in note else 'Repère à vérifier' if 'mais marqueur' in note else 'Repère approximatif' if 'approximative' in note else ''
            if reserve:ax.text(.98,.95,reserve,transform=ax.transAxes,ha='right',va='top',fontsize=7,color='#8d5610',bbox={'facecolor':'#fff0d3','edgecolor':'none','pad':1})
            summary.append(row)
        print(subject+' extrait et représenté',flush=True)
    fig.suptitle('Regard sur le FND et la master liste après les cinq types d’alarme',x=.075,ha='left',fontsize=20,fontweight='bold',y=.975)
    fig.text(.075,.935,'7 sujets · 5 alarmes · 0–18 secondes après le marqueur manuel · Deux lignes : FND entier puis ML',fontsize=12,color='#526174')
    handles=[Patch(color='#63b6d1',label='Ligne FND : dans le FND, ML incluse'),Patch(color=COLORS['ML'],label='Ligne ML : dans la master liste'),Patch(facecolor='white',edgecolor='#aab3bf',label='Ligne ML : hors ML, dans le FND'),Patch(color=COLORS['FND_ML_inconnu'],label='Statut ML indisponible'),Patch(color=COLORS['indetermine'],label='Position indéterminée (pas « hors FND »)'),Line2D([],[],marker='*',color='#ae3f70',ls=':',label='Appui externe : alignement à vérifier')]
    fig.legend(handles=handles,loc='upper left',bbox_to_anchor=(.07,.92),ncol=3,frameon=False,fontsize=10)
    fig.supxlabel('Secondes après l’apparition annotée de l’alarme',y=.115,fontsize=12)
    fig.text(.075,.06,'Appuis SUJ5–7 : durées apparition → appui fournies séparément. Placement conditionnel sur le repère Tobii ; synchronisation à vérifier.\nSans marqueur d’apparition, la durée d’appui est indiquée mais aucune chronologie du regard n’est inventée.',fontsize=10,color='#526174')
    fig.text(.075,.022,'Aucune AOI vidéo manuelle utilisée. Gris : mapping absent, mesure invalide ou enregistrement indisponible ; ce n’est pas une absence de détection.\nP1 : SUJ1–4, clignotement manuel ; P2 : SUJ5–7, automatique. FND : tout le FND clignote. Géométrie ML entre projets à confirmer.',fontsize=10,color='#526174')
    fig.subplots_adjust(left=.115,right=.98,top=.82,bottom=.18,hspace=.35,wspace=.13)
    for ext in ['png','svg']:fig.savefig(OUT/f'regard_7_sujets_5_alarmes_FND_ML_lignes_appuis.{ext}',dpi=170)
    plt.close(fig)
    for name,rows in [('fenetres_AOI_alarmes.csv',summary),('periodes_AOI_alarmes.csv',spans)]:
        with (OUT/name).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    audit=dict(fenetre_s=[0,END],cases=len(summary),reperes_presents=sum(r['repere_s']!='' for r in summary),appuis_fournis=len(ack),appuis_places=sum(r['appui_place'] for r in summary),sources=audits,methode='coordonnées mappées dans limites FND et AOI ML exportée ; intervalles temporels sans prolongation des lacunes >50 ms ; aucune interpolation')
    (OUT/'audit_vue_globale.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
    for f in OUT.glob('*.svg'):f.write_text('\n'.join(x.rstrip() for x in f.read_text().splitlines())+'\n')
    print(json.dumps(audit,ensure_ascii=False))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sources',default='/workspace/attachments');main(p.parse_args().sources)
