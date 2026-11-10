"""Assembler un support de réunion commenté, en conservant les figures PDF.

python3 scripts/support_reunion.py --date 2026-11-10
Les figures publiées suffisent : aucun Excel ni cache individuel requis.
"""
import argparse
import csv
import hashlib
import io
import json
import os
import tempfile
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

os.environ.setdefault('MPLCONFIGDIR',str(Path(tempfile.gettempdir())/'tobii-matplotlib'))
import matplotlib
from pypdf import PdfReader,PdfWriter,Transformation
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3,landscape
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.lib.styles import ParagraphStyle

ROOT=Path(__file__).resolve().parents[1]
W,H=landscape(A3)
INK='#243448';MUTED='#526174';TEAL='#087f83';BG='#f8fafc'
FONTDIR=Path(matplotlib.get_data_path())/'fonts'/'ttf'
pdfmetrics.registerFont(TTFont('DV',str(FONTDIR/'DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('DV-Bold',str(FONTDIR/'DejaVuSans-Bold.ttf')))
STYLES={
    'body':ParagraphStyle('body',fontName='DV',fontSize=12,leading=18,textColor=HexColor(INK)),
    'small':ParagraphStyle('small',fontName='DV',fontSize=10.5,leading=15,textColor=HexColor(MUTED)),
    'big':ParagraphStyle('big',fontName='DV',fontSize=17,leading=25,textColor=HexColor(INK)),
    'title':ParagraphStyle('title',fontName='DV-Bold',fontSize=23,leading=29,textColor=HexColor(INK)),
}


def para(c,text,x,y,width,style='body'):
    p=Paragraph(text,STYLES[style]);_,height=p.wrap(width,H)
    p.drawOn(c,x,y-height)
    return y-height


def shell(number,title,stamp,subtitle=''):
    stream=io.BytesIO();c=canvas.Canvas(stream,pagesize=(W,H))
    c.setFillColor(HexColor(BG));c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(HexColor(TEAL));c.rect(0,H-10,W,10,fill=1,stroke=0)
    c.setFont('DV-Bold',9);c.setFillColor(HexColor(TEAL))
    c.drawString(38,H-35,'EYE TRACKING · ALARMES FND · SUPPORT DE DISCUSSION')
    y=para(c,escape(title),38,H-53,W-76,'title')
    if subtitle:para(c,subtitle,38,y-12,W-76,'body')
    c.setStrokeColor(HexColor('#dbe2ea'));c.line(38,32,W-38,32)
    c.setFillColor(HexColor(MUTED));c.setFont('DV',9)
    c.drawString(38,18,f'Préparé le {stamp} · Résultats exploratoires · Identifiants pseudonymisés')
    c.drawRightString(W-38,18,f'{number} / 19')
    return stream,c


def finish(stream,c):
    c.showPage();c.save();stream.seek(0)
    return PdfReader(stream).pages[0]


def table(c,rows,x,y,widths,font_size=11):
    styled=[]
    style=ParagraphStyle('cell',parent=STYLES['body'],fontSize=font_size,leading=font_size+5)
    for row in rows:styled.append([Paragraph(str(value),style) for value in row])
    t=Table(styled,colWidths=widths,hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),HexColor('#dcebea')),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),
        ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),
        ('LINEBELOW',(0,0),(-1,0),.7,HexColor('#b7c9c9')),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[HexColor('#ffffff'),HexColor('#eef2f6')]),
    ]))
    _,height=t.wrap(sum(widths),H);t.drawOn(c,x,y-height)
    return y-height


def main(doc_date):
    stamp=date.fromisoformat(doc_date).strftime('%d/%m/%Y')
    output=ROOT/'reports'/f'Support_reunion_Elie_eye_tracking_{doc_date}.pdf'
    output.parent.mkdir(exist_ok=True)
    writer=PdfWriter();readers={};manifest=[]

    def add(page,title,source=None,index=None):
        writer.add_page(page);writer.add_outline_item(title,len(writer.pages)-1)
        item={'page':len(writer.pages),'titre':title}
        if source:item.update(source=str(source),page_source_zero_base=index,
            source_sha256=hashlib.sha256((ROOT/source).read_bytes()).hexdigest())
        manifest.append(item)

    def merge_figure(page,source,index,box):
        source=Path(source)
        if source not in readers:readers[source]=PdfReader(ROOT/source)
        original=readers[source].pages[index]
        sw,sh=float(original.mediabox.width),float(original.mediabox.height)
        x,y,bw,bh=box;scale=min(bw/sw,bh/sh)
        tx=x+(bw-sw*scale)/2;ty=y+(bh-sh*scale)/2
        page.merge_transformed_page(original,Transformation().scale(scale).translate(tx,ty),over=True)

    def figure_page(title,subtitle,source,index,reading,meaning):
        stream,c=shell(len(writer.pages)+1,title,stamp,subtitle)
        para(c,'<b>Comment lire</b><br/>'+reading,40,137,(W-104)/2,'small')
        para(c,'<b>Interprétation pour la démonstration</b><br/>'+meaning,W/2+12,137,(W-104)/2,'small')
        page=finish(stream,c)
        merge_figure(page,source,index,(32,158,W-64,H-315))
        add(page,title,source,index)

    stream,c=shell(1,'Eye tracking et alarmes FND',stamp)
    para(c,'Support de réunion avec Élie',45,H-145,W-90,'big')
    para(c,'Première démonstration avec un montage exploratoire<br/>Figures commentées, observations et questions de protocole',45,H-194,W-90,'big')
    cards=[('7','sujets analysés'),('2','projets à distinguer'),('5','formats d’alarme'),('Manuels','repères d’apparition')]
    for k,(value,label) in enumerate(cards):
        x=45+k*(W-90)/4
        c.setFillColor(HexColor('#e1ecee'));c.roundRect(x,H-380,(W-120)/4,105,8,fill=1,stroke=0)
        c.setFont('DV-Bold',27);c.setFillColor(HexColor(TEAL));c.drawString(x+16,H-315,value)
        para(c,escape(label),x+16,H-335,(W-150)/4,'body')
    y=H-425
    for text in [
        '<b>Objectif :</b> illustrer comment décrire la répartition du regard, sa réorientation et l’exploration du FND autour d’une alarme.',
        '<b>Contexte :</b> les participants surveillent une route sur un écran principal et doivent repérer une alarme sur une tablette représentant le FND.',
        '<b>Périmètre :</b> SUJ1–4, projet 1 (clignotement manuel) ; SUJ5–7, projet 2 (automatique). Les différences exactes de protocole restent à préciser.',
        '<b>Statut :</b> document de travail avant validation du protocole. Les résultats illustrent des possibilités ; ils ne classent ni les participants ni l’efficacité des alarmes.',
    ]:y=para(c,text,45,y,W-110,'body')-20
    add(finish(stream,c),'Présentation et objectif')

    stream,c=shell(2,'Repères de lecture et parcours du document',stamp)
    y=H-115
    y=table(c,[['Pages','Contenu','Utilisation'],
        ['3','Disponibilité des données des sept sujets','Situer la qualité et les limites du montage.'],
        ['4–6','SUJ1 : ensemble, alarmes, délais du premier regard','Exemple détaillé, avec plusieurs AOI renseignées.'],
        ['7–9','ALERT_FND : maintien, exploration, positions sur le FND','Comparer des observations, en gardant les lacunes visibles.'],
        ['10','Questions pour Élie et proposition de synchronisation','Préparer une acquisition et une interprétation plus solides.'],
        ['11–12','Annexes : regard autour des cinq alarmes, sept sujets','Figures prévues pour le mail, conservées pour consultation.'],
        ['13–19','Annexes : une page de positions numérotées par sujet','Zoomer et examiner l’ordre des positions mappées.'],
    ],40,y,[60,400,W-540],11)-30
    y=para(c,'<b>Quatre notions à garder distinctes</b>',45,y,W-90,'big')-15
    for text in [
        '<b>Premier regard observé :</b> premier échantillon valide dans une zone après le repère d’alarme. Cela ne prouve pas que l’alarme est comprise.',
        '<b>Fixation Tobii et maintien géométrique :</b> deux traitements différents. Un regard relativement stable dans le repère des lunettes n’est pas nécessairement une fixation unique sur le même objet dans la pièce.',
        '<b>Mapping :</b> report des points de regard sur une image de référence du FND. Une lacune de mapping ne signifie pas une absence de regard vers le FND.',
        '<b>Acquittement :</b> aucun clic n’est identifiable dans les sept exports reçus. Regarder le bas du FND ne permet pas de dater un appui.',
    ]:y=para(c,text,45,y,W-110,'body')-13
    add(finish(stream,c),'Repères de lecture et sommaire')

    figure_page('1 · Quelles données avons-nous pour les sept sujets ?',
        'La qualité du suivi des yeux et la possibilité d’interpréter une alarme sont deux questions distinctes.',
        'results/comparaison/comparaison_7_sujets.pdf',0,
        'Les barres comparent le suivi oculaire déclaré valide et les périodes délimitées pour le mapping. Le tableau indique les apparitions annotées et les réserves de prétraitement.',
        'Le montage fournit des données exploitables, mais de façon inégale selon les sujets et événements. Les périodes de mapping ne sont pas le temps passé à regarder le FND. Cette figure ne mesure pas une performance.')
    figure_page('2 · SUJ1 : vue d’ensemble du regard',
        'SUJ1 est le seul export avec des mesures renseignées pour les AOI vidéo de l’écran principal et de la tablette.',
        'results/SUJ1/synthese/SUJ1_synthese_complete.pdf',0,
        'Suivre le temps de gauche à droite. Chaque piste représente une AOI. Couleur : regard dans la zone ; bleu-gris : hors de la zone avec mesure valide ; gris clair : mesure absente ou invalide.',
        'La figure illustre les passages entre la surveillance de la route et l’instrument. Les pourcentages sont calculés sur les échantillons valides où chaque AOI est renseignée. Les zones peuvent se chevaucher : ne pas additionner les pourcentages. Rectangle reste à identifier.')
    figure_page('3 · SUJ1 : le regard autour des cinq types d’alarme',
        'Les cinq alarmes sont examinées chez le même sujet : FND, ML_LARGE, ML_LIGHT, RED et TEXT.',
        'results/SUJ1/synthese/SUJ1_synthese_complete.pdf',1,
        'Chaque panneau est centré sur l’apparition ajoutée manuellement par Élie : le trait rouge correspond à t = 0. Les couleurs indiquent les AOI regardées avant et après ce repère.',
        'On peut décrire des différences de séquence visuelle entre ces essais. RED est perturbé par une publicité. Avec une seule occurrence par format et un seul sujet, les différences ne démontrent pas qu’une alarme est meilleure.')
    figure_page('4 · SUJ1 : rapidité d’orientation du regard',
        'Comparer le premier regard vers la tablette FND et le premier regard vers la zone ML vidéo.',
        'results/SUJ1/synthese/SUJ1_synthese_complete.pdf',2,
        'Le délai commence au marqueur d’apparition manuel et se termine au premier échantillon valide dans l’AOI. La recherche porte sur les dix secondes suivantes. Une absence d’entrée observée ne reçoit pas un délai artificiel de dix secondes.',
        'Vers la tablette : FND 0,79 s ; ML_LARGE 2,15 s ; ML_LIGHT 0,72 s ; TEXT 1,58 s. RED 2,73 s est grisé. Ce sont des délais de regard observé, pas des temps de détection confirmée. La zone FND ne désigne pas forcément l’élément exact de l’alarme.')
    figure_page('5 · ALERT_FND : déplacement, maintien et retour',
        'Rechercher une séquence du regard chez les sept sujets, avec les critères exploratoires documentés.',
        'results/comparaison/mouvements_FND/ALERT_FND_deplacement_maintien_retour_epure.pdf',0,
        'Orange : déplacement candidat ressemblant à la référence SUJ1. Vert : maintien géométrique retenu, au moins 300 ms. Bleu : retour proche de la position oculaire initiale. Les traits gris indiquent les données de regard disponibles.',
        'Cinq retours sont observés avant +12 s. SUJ6 n’a pas de retour répondant au critère dans cette fenêtre ; SUJ4 n’a pas de motif initial retenu. Le retour est défini dans le repère des lunettes, sans compensation de tête : sa destination dans la scène n’est pas confirmée.')
    figure_page('6 · Entre le maintien et le retour : quelles régions du FND ?',
        'Cette cartographie complète la figure précédente : elle montre les parties visibles de l’exploration de l’instrument.',
        'results/comparaison/regions_FND/FND_maintien_exploration_retour.pdf',0,
        'Les couleurs représentent les tiers haut, milieu et bas de l’image FND. Le cadre noir délimite la fin du maintien jusqu’au retour, ou jusqu’à +12 s. La barre à droite conserve la part de région non attribuable en gris.',
        'Chez SUJ1, on observe successivement bas, milieu, bas puis haut avec des lacunes ; seuls 35 % de cet intervalle sont attribuables. Chez SUJ5, la partie attribuable est surtout basse. Ces tiers sont géométriques, sans fonction alarme/bouton validée. Aucun trajet n’est reconstruit à travers le gris.')
    figure_page('7 · ALERT_FND : positions sur le FND et ordre du regard',
        'Une vue spatiale commune, avec couleurs du temps et numéros pour suivre les positions disponibles.',
        'results/comparaison/positions_FND/positions_FND_7_sujets_ordre_temps.pdf',0,
        '1, 2, 3… indiquent l’ordre des segments mappés retenus. Violet : plus tôt ; jaune : plus tard, sur une échelle commune de zéro à huit secondes après FND. Les coordonnées sont rapportées à chaque image de référence.',
        'Les numéros ne représentent pas les mêmes actions entre sujets. Pour SUJ2, SUJ5 et SUJ6, un seul segment est retenu ; cela ne signifie pas un seul regard dans toute la scène. Les images et AOI entre projets ne sont pas supposées géométriquement équivalentes. Pages individuelles en annexe.')

    stream,c=shell(10,'Points à clarifier avec Élie et prochaine acquisition',stamp)
    y=H-120
    y=para(c,'<b>Protocole et interprétation</b>',42,y,W-84,'big')-18
    questions=[
        'Où apparaît chaque alarme, et où fallait-il toucher pour acquitter ? Le bas du FND comme zone d’action reste une hypothèse.',
        'Les annotations manuelles correspondent-elles à la première image visible ? Confirmer les réserves de SUJ3 et les éventuels rejeux.',
        'Les captures P2 / Recording 10 montrent ML_LIGHT vers 97,432 s ; l’export SUJ6 / Recording 10 porte ML_LARGE au même instant. Vérifier session, version et libellé avant de renommer quoi que ce soit.',
        'Quelles différences exactes entre projets : clignotement, timings, ordre, visuels, participants et répétitions ? À quel projet se rattachent les notes initiales SUJ5–7 ?',
        'Quels temps d’apparition et d’acquittement Justine peut-elle fournir, avec quelle horloge et quel repère commun ? Que signifient les signaux SyncPortOutHigh/Low ?',
    ]
    for k,q in enumerate(questions,1):y=para(c,f'<b>{k}.</b> '+q,45,y,W-90,'body')-12
    y-=10;y=para(c,'<b>Synchronisation proposée pour la maquette</b>',42,y,W-84,'big')-17
    for text in [
        'Afficher un code visuel identifiable dans la vidéo et le journal du prototype, au début et à la fin, éventuellement entre blocs. Le maintenir sur plusieurs images pour éviter qu’il soit manqué ; vérifier sa lisibilité et la dérive des horloges.',
        'Enregistrer séparément : apparition de l’alarme, appui sur le bouton, acquittement accepté et disparition de l’alarme, avec identifiants de session/essai et temps monotones.',
        'Le repère visuel n’enregistre pas les clics à lui seul. Vérifier que le lecteur Figma permet le logging et l’export ; sinon prévoir une maquette instrumentée. Valider les temps de rendu sur la vidéo et documenter leur incertitude.',
    ]:y=para(c,text,45,y,W-90,'body')-12
    para(c,'<b>Suite :</b> intégrer les réponses de la réunion avant de rédiger le rapport final. Les captures du montage sont décrites dans le dépôt ; leurs originaux n’étaient pas disponibles comme fichiers pour ce PDF.',45,y-6,W-90,'small')
    add(finish(stream,c),'Questions de protocole et synchronisation')

    figure_page('Annexe A · Sept sujets, cinq alarmes : regard vers ML',
        'Figure prévue pour le mail initial : même alignement sur les événements, avec la zone ML disponible.',
        'results/comparaison/regard_7_sujets_5_alarmes.pdf',0,
        'Une ligne par sujet et une colonne par alarme. Vert : regard dans ML ; bleu : hors ML avec mesure valide. Les repères absents sont indiqués et les périodes sans mesure restent visibles.',
        'Hors ML ne signifie pas regard vers la route. ML ne correspond pas nécessairement à l’emplacement de chacune des cinq alarmes. Dix-neuf des trente-cinq cases possèdent un repère d’apparition. Cette vue montre les observations disponibles, sans estimer un taux de détection.')
    figure_page('Annexe B · Sept sujets, cinq alarmes : toutes les AOI exportées',
        'Figure détaillée prévue pour le mail : consulter en zoom pour lire les pistes de chaque sujet et alarme.',
        'results/comparaison/regard_7_sujets_5_alarmes_toutes_AOI.pdf',0,
        'Chaque case contient cinq pistes : FND vidéo, écran route vidéo, ML vidéo, ML sur l’image FND et Rectangle vidéo. Non renseignée : colonne présente mais vide pour ce sujet. Non exportée : colonne absente de cet export.',
        'Seul SUJ1 a des mesures dans les AOI vidéo. Les autres sujets fournissent surtout les coordonnées et l’AOI ML de l’image FND. Les données manquantes ne sont pas des regards absents. La fonction de Rectangle et la géométrie des zones restent à confirmer.')

    base=ROOT/'results'/'comparaison'/'positions_FND'
    audits=json.loads((base/'audit_positions_FND.json').read_text())
    with (base/'positions_FND_ordre_temps.csv').open(encoding='utf-8-sig') as f:
        positions=list(csv.DictReader(f))
    for n in range(1,8):
        subject=f'SUJ{n}';audit=next(a for a in audits if a['sujet']==subject)
        points=[r for r in positions if r['sujet']==subject]
        title=f'Annexe C{n} · {subject} : positions numérotées sur le FND'
        stream,c=shell(len(writer.pages)+1,title,stamp,
            'Coordonnées mappées présentes dans l’export ; une position peut manquer avant, entre ou après les points représentés.')
        x=535;y=H-145
        y=para(c,f"<b>Projet {audit['projet']} · {len(points)} segment(s) représenté(s)</b><br/>Couverture mappage sur 0–8 s : {audit['couverture_mappage_pct']:.1f} % des échantillons oculaires. Cette couverture n’est pas du temps de regard vers le FND.",x,y,W-x-45,'body')-22
        y=para(c,'<b>Repères des numéros</b>',x,y,W-x-45,'body')-12
        values=[['Point','Début après FND','Position médiane (% image)']]
        for r in points:
            xx=100*float(r['x_median_px'])/audit['largeur_px'];yy=100*float(r['y_median_px'])/audit['hauteur_px']
            values.append([r['ordre_visible'],f"{float(r['debut_relatif_s']):.2f} s",f'x {xx:.1f} % · y {yy:.1f} %'])
        y=table(c,values,x,y,[55,135,W-x-235],10)-20
        note='Le repère FND de SUJ3 est approximatif selon les notes de prétraitement.' if n==3 else 'Aucun clic ni acquittement n’est déduit de cette vue.'
        para(c,note+'<br/><br/>Les numéros indiquent uniquement l’ordre des segments mappés retenus. Un même index de fixation Tobii peut être séparé en plusieurs segments par une lacune de mapping. Le bas de l’image comme zone de réponse reste une hypothèse.',x,y,W-x-45,'small')
        page=finish(stream,c)
        src='results/comparaison/positions_FND/positions_FND_7_sujets_ordre_temps.pdf'
        merge_figure(page,src,n,(25,55,480,H-190))
        add(page,title,src,n)

    if len(writer.pages)!=19:raise ValueError('Pagination inattendue.')
    writer.add_metadata({'/Title':'Eye tracking et alarmes FND — Support de réunion avec Élie',
        '/Author':'Projet AirbusHelico','/Subject':'Figures commentées et questions de protocole — analyse exploratoire',
        '/Keywords':'Tobii, FND, regard, démonstration, protocole'})
    for page in writer.pages:page.compress_content_streams()
    with output.open('wb') as f:writer.write(f)
    (output.with_suffix('.manifest.json')).write_text(json.dumps({'date_document':doc_date,'pages':manifest,
        'description':'Support de discussion ; pas un rapport final ni une évaluation de performance.'},ensure_ascii=False,indent=2))
    print(f'{output} · {len(writer.pages)} pages · {output.stat().st_size/1e6:.2f} Mo')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--date',required=True,help='Date documentaire YYYY-MM-DD')
    main(parser.parse_args().date)
