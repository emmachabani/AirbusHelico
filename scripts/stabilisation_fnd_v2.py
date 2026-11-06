"""Même motif initial (0–5 s), recherche de retour étendue à +12 s.

L'ancienne figure est conservée. Les caches de extraire_fnd.py sont requis.
"""
import csv
import json
import numpy as np
from mouvements_fnd import ROOT,BIN,load_subject,baseline,binned
from stabilisation_fnd import pattern
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.backends.backend_pdf import PdfPages


def main():
    output=ROOT/'results'/'comparaison'/'mouvements_FND'
    method=json.loads((output/'methode_et_audit.json').read_text())
    reference=np.array(method['reference_suj1']['deplacement_yaw_pitch_deg'])
    rows=[];signals={}
    for n in range(1,8):
        s=load_subject(n);result=pattern(s,0,reference)
        center,_=baseline(s,0);times,delta=binned(s,0,center,end_seconds=12)
        good=np.isfinite(delta).all(axis=1);norm=np.linalg.norm(delta,axis=1)
        hold=result['stabilisation_s'];ret=None;after_coverage=None
        if hold is not None:
            finish=hold+result['duree_stabilisation_s']
            after=times>finish
            after_coverage=float(100*np.mean(good[after]))
            near=after&good&(norm<=5)
            returns=np.flatnonzero(near[:-2]&near[1:-1]&near[2:])
            if len(returns):ret=float(times[int(returns[0])]-BIN/2)
        status='retour observé' if ret is not None else ('non observé avant +12 s' if hold is not None else 'non évalué : motif initial non retrouvé')
        rows.append({'sujet':f'SUJ{n}','projet':1 if n<=4 else 2,
            'mouvement_s':result['mouvement_s'],'stabilisation_s':hold,
            'duree_stabilisation_s':result['duree_stabilisation_s'],
            'retour_ancienne_fenetre_5s':result['retour_position_initiale_s'],
            'retour_fenetre_12s':ret,'statut_retour':status,
            'couverture_bins_valides_0_5s_pct':float(100*np.mean(good[(times>=0)&(times<=5)])),
            'couverture_bins_valides_apres_maintien_pct':after_coverage,
            'reserve':'Apparition approximative' if n==3 else 'Position oculaire / lunettes ; lieu non confirmé'})
        signals[n]=(times,good)
    assert sum(r['retour_ancienne_fenetre_5s'] is not None for r in rows)==2
    assert sum(r['retour_fenetre_12s'] is not None for r in rows)==5
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'figure.facecolor':'#f8fafc','axes.facecolor':'#f8fafc',
                         'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(17,10))
    for i,row in enumerate(rows):
        times,good=signals[i+1];observed=(times>=0)&good
        ax.plot([0,12],[i+.24,i+.24],color='#e1e6ed',lw=5,zorder=1)
        ax.scatter(times[observed],np.full(observed.sum(),i+.24),marker='|',s=15,color='#aab8c7',zorder=2)
        move=row['mouvement_s'];hold=row['stabilisation_s'];ret=row['retour_fenetre_12s']
        if move is not None:ax.scatter(move,i,s=70,color='#d29127',zorder=4)
        if hold is not None:
            duration=row['duree_stabilisation_s']
            ax.plot([hold,hold+duration],[i,i],color='#087f83',lw=10,solid_capstyle='butt',zorder=3)
            ax.text(hold+duration+.1,i-.16,f'{duration:.2f} s de maintien',fontsize=9,color='#126466')
        if ret is not None:
            ax.scatter(ret,i,s=75,marker='D',color='#4568b0',zorder=4)
            ax.text(ret+.12,i,f'{ret:.2f} s',va='center',fontsize=10,color='#304b89',fontweight='bold')
        elif hold is not None:
            ax.scatter(12,i,marker='>',color='#8b96a5',s=65,zorder=4)
        text=row['statut_retour']
        if hold is None:text+=f"\nDonnées valides : {row['couverture_bins_valides_0_5s_pct']:.0f} % sur 0–5 s"
        ax.text(12.5,i,text,va='center',fontsize=10,color='#526174')
    ax.set_xlim(0,17);ax.set_xticks([0,2,4,6,8,10,12]);ax.set_ylim(6.6,-.7)
    ax.set_yticks(range(7),[f'SUJ{n} · P{1 if n<=4 else 2}'+(' *' if n==3 else '') for n in range(1,8)])
    ax.set_xlabel('Temps depuis l’apparition annotée de FND (s)');ax.grid(axis='x',alpha=.12)
    fig.suptitle('ALERT_FND · Déplacement, maintien et retour du regard',x=.065,ha='left',fontsize=19,fontweight='bold',y=.98)
    fig.text(.065,.91,'Déplacement candidat, période de stabilité et retour observés après l’apparition annotée de l’alarme.\nLe retour signifie : position des yeux proche de celle d’avant l’alarme, sans confirmation du lieu regardé.',fontsize=12,color='#526174')
    handles=[Line2D([0],[0],marker='o',color='#d29127',lw=0,label='Déplacement candidat'),
        Line2D([0],[0],color='#087f83',lw=7,label='Maintien ≥ 300 ms'),
        Line2D([0],[0],marker='D',color='#4568b0',lw=0,label='Retour proche de la position initiale'),
        Line2D([0],[0],color='#aab8c7',lw=3,label='Données de regard valides')]
    fig.legend(handles=handles,loc='upper left',bbox_to_anchor=(.06,.855),frameon=False,ncol=2,fontsize=11)
    fig.text(.065,.045,'Maintien : dispersion p90 ≤ 2°, couverture ≥ 80 %, sans lacune > 50 ms. Retour : écart ≤ 5° pendant trois bins valides de 50 ms.\nSUJ6 : retour non observé avant +12 s, pas une preuve d’absence de retour ultérieur. SUJ4 : motif initial non retrouvé, données partielles.\n* SUJ3 : apparition approximative. SUJ6/7 : motif aussi présent avant l’alarme ; témoins SUJ1/2/5 non évaluables.\nAucun clic ou acquittement identifié. Rotations de tête non compensées ; analyse exploratoire, sans classement de performance.',fontsize=10,color='#526174')
    fig.subplots_adjust(left=.1,right=.98,top=.73,bottom=.18)
    for name in ['04_deplacement_maintien_retour_12s','05_deplacement_maintien_retour_epure']:
        for ext in ['png','svg']:fig.savefig(output/f'{name}.{ext}',dpi=170)
    for name in ['ALERT_FND_deplacement_maintien_retour_12s','ALERT_FND_deplacement_maintien_retour_epure']:
        with PdfPages(output/f'{name}.pdf') as pdf:pdf.savefig(fig)
    plt.close(fig)
    with (output/'retours_FND_5s_vs_12s.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    for row in rows:print(json.dumps(row,ensure_ascii=False))


if __name__=='__main__':main()
