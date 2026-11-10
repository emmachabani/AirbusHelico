"""PowerPoint modifiable : objets natifs pour graphiques, originaux en annexe.
python3 scripts/presentation_airbus.py
"""
import csv,json,hashlib,math
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE,MSO_CONNECTOR
from pptx.enum.text import MSO_ANCHOR
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'presentations'
C={'bg':'F5F8FB','ink':'243448','muted':'526174','teal':'087F83','blue':'168FA3','fnd':'63B6D1','ml':'9265B5','outside':'B8C6A2','gray':'E5E8ED','pink':'AE3F70','orange':'D29127','border':'D4DDE7','white':'FFFFFF','warn':'FFF0D3'}
COLORS=['356CA3','DA8635','4B9B70','9860AD','D45D76','927444','389DA4']
ALARMS=['ALERT_ML_LIGHT','ALERT_ML_LARGE','ALERT_FND','ALERT_RED','ALERT_TEXT']
LABELS=['ML LIGHT','ML LARGE','FND','RED','TEXT']
P=Presentation();P.slide_width=Inches(16);P.slide_height=Inches(9)
P.core_properties.title='Eye tracking et alarmes FND — Démonstration Airbus'
P.core_properties.subject='Support de discussion modifiable — données exploratoires'
P.core_properties.author='Projet AirbusHelico'
MANIFEST=[];SOURCES=set()

def rgb(color):return RGBColor.from_string(C.get(color,color))
def box(slide,x,y,w,h,fill='white',border=None,shape=MSO_SHAPE.RECTANGLE):
    s=slide.shapes.add_shape(shape,Inches(x),Inches(y),Inches(w),Inches(h));s.fill.solid();s.fill.fore_color.rgb=rgb(fill)
    if border:s.line.color.rgb=rgb(border);s.line.width=Pt(.7)
    else:s.line.fill.background()
    return s

def text(slide,content,x,y,w,h,size=18,color='ink',bold=False):
    s=slide.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=s.text_frame;tf.word_wrap=True
    tf.margin_left=Inches(.025);tf.margin_right=Inches(.025);tf.margin_top=0;tf.margin_bottom=0
    for i,line in enumerate(content.split('\n')):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line;p.font.name='Aptos';p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=rgb(color);p.space_after=Pt(7)
    return s

def line(slide,x1,y1,x2,y2,color='border',width=1):
    s=slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(x1),Inches(y1),Inches(x2),Inches(y2));s.line.color.rgb=rgb(color);s.line.width=Pt(width);return s

def dot(slide,x,y,color='blue',r=.055,kind='dot'):
    shape=MSO_SHAPE.STAR_5_POINT if kind=='star' else MSO_SHAPE.ISOSCELES_TRIANGLE if kind=='triangle' else MSO_SHAPE.OVAL
    return box(slide,x-r,y-r,2*r,2*r,color,shape=shape)

def notes(slide,content,sources=()):
    for src in sources:SOURCES.add(src)
    slide.notes_slide.notes_text_frame.text=content+'\n\nSources dans le dépôt :\n'+'\n'.join(sources)

def new(title,kicker='DÉMONSTRATION AIRBUS · EYE TRACKING',subtitle=''):
    slide=P.slides.add_slide(P.slide_layouts[6]);slide.background.fill.solid();slide.background.fill.fore_color.rgb=rgb('bg')
    box(slide,0,0,16,.09,'teal');text(slide,kicker,.55,.28,14,.3,10,'teal',True)
    text(slide,title,.55,.83,14.8,.8,28,'ink',True)
    if subtitle:text(slide,subtitle,.58,1.62,14.7,.52,14,'muted')
    line(slide,.55,8.52,15.45,8.52)
    text(slide,'Support de discussion · Données exploratoires · 10 novembre 2026',.58,8.65,13,.2,9,'muted')
    text(slide,str(len(P.slides)),15,8.62,.5,.25,10,'muted')
    MANIFEST.append({'diapositive':len(P.slides),'titre':title})
    return slide

def card(slide,x,y,w,title,body,color='teal',h=3.8):
    box(slide,x,y,w,h,'white','border',MSO_SHAPE.ROUNDED_RECTANGLE);box(slide,x,y,.07,h,color)
    text(slide,title,x+.22,y+.2,w-.4,.65,21,color,True);text(slide,body,x+.22,y+1,w-.42,h-1.15,17,'ink')

def read(src):
    SOURCES.add(src)
    with (ROOT/src).open(encoding='utf-8-sig') as f:return list(csv.DictReader(f))

MEASURE='results/comparaison/delais_durees_FND_7_sujets/mesures_FND_et_appuis.csv'
FIX='results/comparaison/fixations_FND_100ms/premieres_fixations_FND_100ms.csv'
PERIODS='results/comparaison/vue_globale_AOI_alarmes/trois_etats/periodes_AOI_alarmes.csv'
WINDOWS='results/comparaison/vue_globale_AOI_alarmes/trois_etats/fenetres_AOI_alarmes.csv'
REACTION='inputs/projet2/temps_reaction_declares.csv'
RETURNS='results/comparaison/mouvements_FND/retours_FND_5s_vs_12s.csv'
BOXSTATS='results/comparaison/boites_5_alarmes_sans_fixation/statistiques_boites.csv'
BOXPOINTS='results/comparaison/boites_5_alarmes_sans_fixation/observations_representees.csv'
measure=read(MEASURE);fix=read(FIX);periods=read(PERIODS);windows=read(WINDOWS);reaction=read(REACTION);returns=read(RETURNS);stats=read(BOXSTATS);points=read(BOXPOINTS)
ACK={(r['sujet'],r['type_alerte']):float(r['temps_declare']) for r in reaction}

s=new('Eye tracking et alarmes FND','AIRBUS · PREMIÈRE DÉMONSTRATION', 'Ce que ce montage permet déjà de montrer — et comment rendre la prochaine acquisition plus informative')
text(s,'Observer → comprendre → améliorer le protocole',.65,2.55,14,1,31,'teal',True)
for x,big,label in [(1,'7','sujets'),(5.8,'5','formats d’alarme'),(10.6,'2','projets d’acquisition')]:
    box(s,x,4,4.25,1.7,'white','border',MSO_SHAPE.ROUNDED_RECTANGLE);text(s,big,x+.25,4.2,1.3,.7,38,'teal',True);text(s,label,x+1.35,4.6,2.65,.65,19)
text(s,'Montage exploratoire : une démonstration des possibilités, sans classement des personnes ni des alarmes.',.8,6.5,14.2,.9,21,'muted')
notes(s,'Support préparatoire à la discussion avec Élie et Airbus. Ce n’est pas un rapport de validation ou une évaluation de compétence pilote. Les graphiques principaux sont reconstruits avec des objets PowerPoint modifiables ; les images originales sont en annexe.')

s=new('Le contexte et les cinq formats',subtitle='Tâche : surveiller la route sur l’écran principal et repérer l’alarme sur la tablette représentant le FND.')
card(s,.65,2.5,4.5,'Deux conditions','Projet 1 · SUJ1–4\nClignotement déclenché manuellement.\n\nProjet 2 · SUJ5–7\nClignotement automatisé dans Figma.',h=4.9)
card(s,5.65,2.5,4.65,'Cinq formats','1 · ML LIGHT\n2 · ML LARGE\n3 · FND entier clignotant\n4 · RED\n5 · TEXT',h=4.9)
card(s,10.8,2.5,4.5,'Ce qui est disponible','Regard Tobii et mapping sur photo FND.\n\nMarqueurs manuels d’apparition.\n\nTemps apparition → appui pour SUJ5–7.',h=4.9)
notes(s,'Les numéros identifient les formats, sans garantir leur ordre de présentation. Tout le FND clignote pour ALERT_FND. La capture présente des messages différents selon les formats : on n’isole pas nécessairement le seul effet visuel. La géométrie et la définition précise de ML LIGHT/LARGE restent à confirmer.',[REACTION,'inputs/projet2/README.md'])

s=new('Limite 1 · Dater l’apparition et l’appui dans le même repère',subtitle='Objectif : séparer apparition, orientation du regard, appui et réponse de l’interface.')
for x,title,body in [(0.65,'Aujourd’hui','L’apparition est annotée manuellement dans Tobii.\n\nLes durées d’appui proviennent d’une autre source.'),(5.65,'À instrumenter','Afficher un code visuel commun dans la vidéo et le journal du prototype.\n\nRépéter des repères au début, à la fin et entre blocs.'),(10.65,'À enregistrer','Apparition de l’alarme.\nAppui sur le bouton.\nAcquittement accepté.\nDisparition de l’alarme.')]:card(s,x,2.55,4.6,title,body,h=4.65)
text(s,'Plusieurs repères servent à vérifier le décalage et la dérive des horloges. Un repère visuel seul n’enregistre pas les clics.',.75,7.55,14.5,.6,17,'teal',True)
notes(s,'La synchronisation Figma/Tobii n’est pas acquise. Vérifier les possibilités de logging/export du lecteur Figma ou utiliser une maquette instrumentée. Une frame portant un code doit rester visible plusieurs images ; la durée devra être validée. Conserver des temps monotones et des identifiants session/essai.', ['docs/contexte/synchronisation_prototype.md'])

s=new('Limite 2 · Ajouter une zone « écran principal »',subtitle='La photo de référence du FND permet le mapping ; le contenu de l’écran route change en permanence.')
card(s,.7,2.55,6.9,'Piste proposée','Définir la surface physique de l’écran.\n\nTester des repères visuels autour de l’écran ou un suivi de ses quatre coins.\n\nClasser le point de regard dans cette surface, indépendamment du contenu affiché.',h=4.8)
card(s,8,2.55,7.25,'Points à vérifier avec Tobii','Compatibilité du matériel, du logiciel et de l’export.\n\nRobustesse aux mouvements de tête, angles et occultations.\n\nPossibilité de récupérer les contours ou transformations image par image.',h=4.8)
text(s,'Il s’agit d’une limite de notre méthode actuelle sur photo, pas d’une impossibilité générale démontrée de Tobii.',.8,7.65,14.3,.55,17,'teal',True)
notes(s,'Les Excel reçus ne contiennent pas les quatre coins du FND dans la vidéo ni l’homographie frame par frame. Ils fournissent les points dans la vidéo, les points mappés, les dimensions de la photo et les indicateurs ML. La piste des repères autour de l’écran doit être testée ; elle n’est pas déclarée prise en charge par le matériel actuel. Ne pas réutiliser les AOI vidéo manuelles commencées puis exclues.', ['docs/contexte/point_reunion_et_rapport.md'])

s=new('Analyser les données depuis l’ordinateur Airbus',subtitle='Deux pistes à étudier pour disposer d’un calcul reproductible et de figures faciles à régénérer.')
card(s,.7,2.55,6.95,'1 · Dans l’environnement Airbus','Explorer Gemini et les fonctionnalités disponibles : lecture des exports, exécution de code, production de graphiques.\n\nVérifier les outils réellement accessibles et la possibilité d’exécuter les scripts.',h=4.8)
card(s,8,2.55,7.25,'2 · Dans un environnement externe autorisé','Préparer des exports pseudonymisés et limités aux colonnes utiles.\n\nAnalyser avec une autre IA et des scripts conservés.\n\nVérifier les conditions de sortie des données et de réidentification.',h=4.8)
text(s,'Dans les deux cas : conserver le code, les paramètres, les sources et les figures ; l’IA aide à écrire le code, le calcul doit être vérifiable.',.8,7.65,14.4,.6,17,'teal',True)
notes(s,'Aucune capacité Gemini sur un ordinateur Airbus n’a été testée ici. Les étiquettes SUJ sont une pseudonymisation ; elles ne garantissent pas l’anonymat. Les vidéos, dates et métadonnées peuvent rester identifiantes. Les Excel bruts sont exclus du dépôt dans ce travail. Les choix d’environnement et de transfert doivent être validés dans le contexte Airbus, sans présumer d’un accès autorisé ou d’une politique donnée.')

s=new('Lire les figures : quatre états, trois mesures',subtitle='La master liste est une sous-zone du FND ; les autres AOI vidéo commencées à la main sont exclues.')
for x,title,body,col in [(.7,'Dans ML','Regard valide mappé dans la master liste.','ml'),(4.5,'FND hors ML','Regard mappé dans la photo, en dehors de ML.','fnd'),(8.3,'Hors FND présumé','Regard valide sans mapping FND : une hypothèse, pas une AOI extérieure confirmée.','outside'),(12.1,'Pas de données','Regard invalide, absent ou données indisponibles.','muted')]:card(s,x,2.45,3.25,title,body,col,h=3.35)
text(s,'Premier point mappé ≠ fixation soutenue ≠ appui d’acquittement',.8,6.2,14.4,.65,25,'teal',True)
text(s,'Une absence de mapping peut aussi provenir d’un échec de reconnaissance du FND. Un point ou une fixation ne prouve pas la compréhension.',.8,7.1,14.3,.8,18,'muted')
notes(s,'Le nom hors FND présumé est défini opérationnellement par la validité oculaire et l’absence de position mappée dans le FND. Il inclut potentiellement des échecs de mapping avec regard valide. Les valeurs d’AOI ML sont utilisées uniquement lorsque le point est mappé dans l’image. Les limites de la photo correspondent au FND selon l’utilisatrice.',[PERIODS,WINDOWS])

# Bandes temporelles, une diapositive par projet pour rester lisible.
for subjects,project in [([1,2,3,4],1),([5,6,7],2)]:
    s=new(f'Comportements après les alarmes · Projet {project}',subtitle='Une case par sujet et alarme · Bandes séparées : ML / FND hors ML / hors FND présumé · 0–18 secondes')
    x0=1.2;cellw=2.75;gap=.13;y0=2.8;rowh=1.13 if project==1 else 1.4
    for j,label in enumerate(LABELS):text(s,label,x0+j*(cellw+gap),2.35,cellw,.35,14,'ink',True)
    for i,n in enumerate(subjects):
        subject=f'SUJ{n}';y=y0+i*rowh;text(s,subject,.58,y+.25,.6,.35,12,'ink',True)
        for j,alarm in enumerate(ALARMS):
            x=x0+j*(cellw+gap);row=next(r for r in windows if r['sujet']==subject and r['alarme']==alarm)
            box(s,x,y,cellw,rowh-.12,'gray')
            if row['repere_s']=='':
                text(s,'Repère absent',x+.08,y+.15,cellw-.16,.25,10,'muted')
                if (subject,alarm) in ACK:text(s,f"Appui : {ACK[(subject,alarm)]:g} s",x+.08,y+.48,cellw-.16,.25,10,'pink')
                continue
            lane={'ML':y+.16,'FND_hors_ML':y+.37,'hors_FND_presume':y+.58,'FND_ML_inconnu':y+.37}
            cols={'ML':'ml','FND_hors_ML':'fnd','hors_FND_presume':'outside','FND_ML_inconnu':'orange'}
            for r in periods:
                if r['sujet']==subject and r['alarme']==alarm:
                    a,b=float(r['debut_s']),float(r['fin_s']);box(s,x+cellw*a/18,lane[r['etat']],max(.004,cellw*(b-a)/18),.14,cols[r['etat']])
            if (subject,alarm) in ACK:dot(s,x+cellw*ACK[(subject,alarm)]/18,y+.83,'pink',.055,'star')
    for j in range(5):
        xx=x0+j*(cellw+gap)
        line(s,xx,7.28,xx+cellw,7.28,'border',.6)
        for tick in [0,6,12,18]:
            tx=xx+cellw*tick/18
            text(s,str(tick),tx-.06,7.31,.35,.18,8,'muted')
    text(s,'Violet : ML   •   Bleu : FND hors ML   •   Vert clair : hors FND présumé   •   Fond gris : pas de regard valide / pas de données',.65,7.65,14.6,.35,12,'muted')
    text(s,'Étoiles roses : appuis externes ; alignement sur le marqueur Tobii à vérifier. Sans repère, aucune chronologie n’est inventée.',.65,8.03,14.6,.3,12,'muted')
    notes(s,'Graphique reconstruit en rectangles PowerPoint modifiables. Les petites bandes sont les périodes agrégées du CSV, sans interpolation. Il ne faut pas lire le vert comme une localisation hors FND prouvée. Les marqueurs disponibles ne couvrent que 19 des 35 couples sujet/alarme. SUJ1/RED : publicité. Repères SUJ3 incertains. La divergence ML_LARGE/ML_LIGHT de SUJ6 avec la capture Recording 10 reste à vérifier.',[PERIODS,WINDOWS,REACTION])

# Délais et appuis, graphiques natifs ; deux diapositives par méthode.
def latency_slide(alarms,sustained=False):
    title='Avec une règle de fixation · au moins 100 ms' if sustained else 'Temps observés · Premier point FND et appui'
    subtitle='Le point marque le début de la première fixation Tobii mappée en continu ≥100 ms.' if sustained else 'Premier point valide mappé dans le FND, sans durée minimale ni règle de fixation.'
    s=new(title,subtitle=subtitle);dataset=fix if sustained else measure;key='delai_premiere_fixation_FND_s' if sustained else 'delai_premier_point_FND_s'
    panelw=4.65 if len(alarms)==3 else 6.95
    for j,alarm in enumerate(alarms):
        px=.7+j*(panelw+.25);text(s,LABELS[ALARMS.index(alarm)],px,2.35,panelw,.4,19,'teal',True)
        axx=px+.63;plotw=panelw-.95;top=3;rh=.53
        for k in [0,4,8,12,16,18]:
            xx=axx+plotw*k/20;line(s,xx,top-.12,xx,top+6*rh+.24,'border',.5);text(s,str(k),xx-.08,6.62,.35,.25,9,'muted')
        for i in range(7):
            subject=f'SUJ{i+1}';r=next(r for r in dataset if r['sujet']==subject and r['alarme']==alarm);yy=top+i*rh;text(s,subject,px,yy-.1,.6,.3,10,'ink',True)
            val=r[key];present=r['apparition_Tobii_s']!=''
            if val!='':
                v=float(val);xx=axx+plotw*v/20;col='muted' if subject=='SUJ1' and alarm=='ALERT_RED' else 'blue';line(s,axx,yy-.04,xx,yy-.04,col,2);dot(s,xx,yy-.04,col,.045);text(s,f'{v:.2f}',xx+.07,yy-.17,.65,.28,10,col,True)
            else:text(s,'Repère absent' if not present else 'Non observé ≥100 ms' if sustained else 'Non observé',axx+.04,yy-.19,plotw-.1,.25,9,'muted')
            press=r['appui_declare_s']
            if press!='':
                v=float(press);xx=axx+plotw*v/20;dot(s,xx,yy+.13,'pink',.06,'star');text(s,f'{v:g}',xx+.06,yy+.03,.7,.25,10,'pink')
        text(s,'Secondes depuis l’apparition',axx,7.02,plotw,.35,11,'muted')
    text(s,'Bleu : regard mappé sur le FND entier (ML incluse)   •   Rose : apparition → appui fourni pour SUJ5–7',.75,7.6,14.4,.35,13,'muted')
    text(s,'Appuis externes : concordance avec les apparitions Tobii à vérifier. Les repères manquants ne sont pas remplacés par un délai inventé.',.75,8.02,14.5,.3,12,'muted')
    notes(s,('Critère : type Fixation, même index Tobii, regard valide et mappé sans point manquant. Tout point invalide, non mappé ou non Fixation casse le segment ; écart >25 ms également. Au moins 100 ms réellement observées après le repère. Une fixation déjà en cours peut recevoir zéro. ' if sustained else 'Aucune durée minimale n’est exigée. Un point peut appartenir à une saccade. ')+ 'Recherche limitée à 10 s, arrêtée avant l’alarme suivante ou la fin de l’essai. Ce n’est pas une mesure de détection consciente. Absence de fixation observée chez SUJ4 avec le seuil de 100 ms ne signifie pas absence de regard réel : mapping fragmenté. SUJ1/RED perturbé par publicité. Repères SUJ3 incertains et libellé SUJ6 à vérifier. Appuis affichés même sans repère Tobii, leur durée relative étant fournie séparément.',[FIX if sustained else MEASURE,REACTION])
for sustained in [False,True]:
    latency_slide(ALARMS[:3],sustained);latency_slide(ALARMS[3:],sustained)

s=new('Comparer les cinq alarmes · Boîtes et sujets individuels',subtitle='Retour au premier point mappé, sans règle de fixation · Comparaison descriptive avec de très petits effectifs')
for j,(metric,title,maxval) in enumerate([('delai_premier_point_FND_s','Premier point FND',5.3),('appui_declare_s','Appui d’acquittement',18.5)]):
    x=.85+j*7.65;y=3.05;w=6.9;h=3.7;text(s,title,x,2.45,w,.4,19,'teal',True)
    def yy(v):return y+h-h*v/maxval
    for tick in ([0,1,2,3,4,5] if j==0 else [0,5,10,15]):
        line(s,x,yy(tick),x+w,yy(tick),'border',.5);text(s,str(tick),x-.32,yy(tick)-.1,.3,.25,9,'muted')
    for k,alarm in enumerate(ALARMS):
        xx=x+.65+k*1.26;r=next(r for r in stats if r['mesure']==metric and r['alarme']==alarm);q1,q3,med,low,high=[float(r[key]) for key in ['q1_s','q3_s','mediane_s','moustache_basse_s','moustache_haute_s']]
        line(s,xx,yy(low),xx,yy(high),'muted',1);line(s,xx-.15,yy(low),xx+.15,yy(low),'muted',1);line(s,xx-.15,yy(high),xx+.15,yy(high),'muted',1)
        box(s,xx-.22,yy(q3),.44,max(.015,yy(q1)-yy(q3)),'DCE6EF','muted');line(s,xx-.22,yy(med),xx+.22,yy(med),'ink',2)
        for p in points:
            if p['mesure']==metric and p['alarme']==alarm:
                n=int(p['sujet'][3:]);dot(s,xx+(n-4)*.055,yy(float(p['valeur_s'])),COLORS[n-1],.045,'triangle' if n>4 else 'dot')
        text(s,f"n={r['n']}",xx-.28,2.92,.6,.25,9,'muted');text(s,LABELS[k],xx-.46,7.03,1.05,.3,10,'ink',True)
for n in range(1,8):
    xx=.85+(n-1)*2.05
    dot(s,xx,7.48,COLORS[n-1],.045,'triangle' if n>4 else 'dot');text(s,f'SUJ{n}',xx+.1,7.36,1.4,.25,10,'muted')
text(s,'Boîte : quartiles 25–75 % ; trait : médiane ; moustaches : 1,5 × IQR. Les points montrent chaque sujet.',.75,7.65,14.4,.35,13,'muted')
text(s,'Les effectifs et sujets diffèrent selon l’alarme pour le regard. Les trois mêmes sujets P2 sont disponibles pour les appuis. Aucun classement d’efficacité.',.75,8.03,14.5,.32,12,'muted')
notes(s,'Les boîtes sont reconstruites en formes natives : quartiles et moustaches proviennent du CSV statistique. Chaque point peut être déplacé et recoloré. Le calcul de boîte exclut SUJ1/RED à cause de la publicité. Les graphiques de regard mélangent P1 et P2, avec n=4,3,7,2,2 selon les alarmes ; ils ne constituent pas une comparaison appariée complète. Les appuis ont n=3 par alarme. Avec de tels effectifs, les formes de distribution sont fragiles. Les messages, projets, sujets et disponibilités diffèrent : ne pas attribuer les différences au seul format graphique. Pas de test de significativité. La figure originale en annexe montre la croix SUJ1/RED exclue.',[BOXSTATS,BOXPOINTS])

s=new('Explorer un comportement sans s’appuyer sur les AOI',subtitle='Une autre entrée possible : rechercher une séquence de mouvements après un événement de référence.')
steps=[('1 · Aligner','Prendre ALERT_FND comme repère temporel, chez SUJ1 puis les autres sujets.'),('2 · Décrire','Choisir un déplacement de référence sur SUJ1 et comparer la direction des yeux dans le repère des lunettes.'),('3 · Rechercher','Identifier un déplacement candidat, puis un maintien géométrique ≥300 ms.'),('4 · Observer','Rechercher ensuite un retour proche de la position oculaire initiale, jusqu’à +12 s.')]
for j,(title,body) in enumerate(steps):card(s,.65+j*3.87,2.65,3.55,title,body,h=3.65)
text(s,'Ce que cela apporte : comparer une organisation temporelle du regard, même lorsque les zones sont mal documentées.',.75,6.85,14.4,.6,21,'teal',True)
text(s,'À revalider : le choix de la référence SUJ1, les seuils, les témoins avant alarme et les destinations dans la scène.',.75,7.75,14.4,.4,17,'muted')
notes(s,'Origine de l’analyse : partir de la séquence observée autour de FND chez SUJ1 pour chercher un motif ressemblant chez les autres. Une première qualification route→FND avait utilisé des AOI vidéo manuelles, depuis exclues : cette référence doit être revalidée indépendamment. Les chiffres actuels restent exploratoires. Déplacement candidat : amplitude 50–200 % de la référence, direction dans un cône de 45°, deux bins adjacents de 50 ms. Maintien : ≥300 ms, dispersion p90 ≤2°, validité ≥80 %, aucune lacune >50 ms. Retour : ≤5° de la position initiale sur trois bins valides de 50 ms. Les mouvements de tête ne sont pas compensés et les destinations route/FND ne sont pas confirmées. Le motif est aussi retrouvé avant alarme chez SUJ6/7 ; témoins SUJ1/2/5 non évaluables.',[RETURNS,'results/comparaison/mouvements_FND/methode_et_audit.json'])

s=new('ALERT_FND · Déplacement, maintien, retour et appui',subtitle='Une illustration exploratoire de séquence visuelle — sans localisation confirmée dans la scène')
x=2;w=11.8;top=2.95;rh=.59
for tick in range(0,13,2):
    xx=x+w*tick/12;line(s,xx,top-.2,xx,top+6*rh+.24,'border',.5);text(s,str(tick),xx-.06,7.03,.3,.25,10,'muted')
for i,r in enumerate(returns):
    yy=top+i*rh;text(s,f"{r['sujet']} · P{r['projet']}",.7,yy-.12,1.15,.3,13,'ink',True);line(s,x,yy,x+w,yy,'border',2)
    if r['mouvement_s']:dot(s,x+w*float(r['mouvement_s'])/12,yy,'orange',.055)
    if r['stabilisation_s']:
        a=float(r['stabilisation_s']);b=a+float(r['duree_stabilisation_s']);box(s,x+w*a/12,yy-.07,w*(b-a)/12,.14,'teal')
    else:text(s,'Motif non retrouvé',x+.12,yy-.28,3,.3,10,'muted')
    if r['retour_fenetre_12s']:dot(s,x+w*float(r['retour_fenetre_12s'])/12,yy,'3567B0',.065)
    if (r['sujet'],'ALERT_FND') in ACK:
        value=ACK[(r['sujet'],'ALERT_FND')];xx=x+w*value/12;dot(s,xx,yy,'pink',.085,'star');text(s,f'Appui {value:g} s',xx+.12,yy-.3,2,.3,11,'pink',True)
text(s,'Orange : déplacement candidat   •   Vert : maintien ≥300 ms   •   Bleu : retour proche de la position initiale   •   Rose : appui externe',.7,2.35,14.4,.4,12,'muted')
text(s,'Secondes depuis l’apparition annotée de FND',x,7.45,w,.35,13,'muted')
text(s,'Référence SUJ1 à revalider sans les AOI manuelles exclues. Appuis conditionnellement alignés. Aucun retour confirmé à la route.',.7,8.05,14.5,.32,12,'muted')
notes(s,'Les lignes fines sont ici un axe temporel de lecture, pas un indicateur de validité par échantillon. Les valeurs des événements sont celles des résultats exploratoires existants. Aucun retour répondant au critère avant +12 s chez SUJ6 ; motif initial non retrouvé chez SUJ4. Aucun appui disponible SUJ1–4. La présence du maintien géométrique n’est ni une fixation sur le bouton ni une détection. Les appuis sont fournis séparément et la concordance des apparitions reste à vérifier.',[RETURNS,REACTION])

s=new('Ce que ces visuels peuvent apporter à Airbus',subtitle='Des idées d’analyse pour une acquisition mieux instrumentée, plutôt qu’une conclusion sur le meilleur format.')
card(s,.7,2.6,4.55,'Répartition du regard','Quand l’instrument est-il consulté ?\n\nQuelles alternances entre la tâche principale, le FND et la master liste ?',h=4.55)
card(s,5.7,2.6,4.55,'Chaîne de réponse','Combien de temps avant la première consultation ?\n\nQuelle relation entre consultation, maintien et appui ?',h=4.55)
card(s,10.7,2.6,4.55,'Comparaison des formats','Comparer plusieurs essais chez les mêmes personnes.\n\nSéparer effet du visuel, message, ordre de présentation et condition de clignotement.',h=4.55)
text(s,'Priorités : synchroniser les événements, ajouter la zone écran, valider les zones et répéter les essais.',.75,7.6,14.4,.6,20,'teal',True)
notes(s,'Les questions sur l’écran principal sont des possibilités futures, pas des résultats déjà obtenus avec les AOI vidéo exclues. La comparaison des formats devrait s’appuyer sur davantage d’essais, des conditions documentées et des sujets comparables. Les données actuelles sont une démonstration de faisabilité descriptive.')

s=new('Points à trancher pendant la discussion',subtitle='Les réponses permettront de préparer un rapport et un protocole de prochaine acquisition plus solides.')
items=[('Apparition / appui','Quels événements Figma sont disponibles ? Avec quelle horloge et quels identifiants d’essai ?'),('Zone de réponse','Où fallait-il toucher ? Appui, acquittement accepté et disparition sont-ils distingués ?'),('Zones et visuels','Peut-on récupérer la photo FND, le contour ML et tester des repères autour de l’écran principal ?'),('Conditions / libellés','Confirmer ML LIGHT/LARGE, les différences P1/P2 et la divergence de libellé sur SUJ6.'),('Environnement d’analyse','Quels outils sont utilisables sur le poste Airbus ? Quel périmètre de données peut être traité ailleurs ?')]
for i,(title,body) in enumerate(items):
    y=2.45+i*1.04;box(s,.7,y,14.6,.87,'white','border',MSO_SHAPE.ROUNDED_RECTANGLE);text(s,title,.95,y+.15,3.15,.5,18,'teal',True);text(s,body,4.3,y+.15,10.6,.6,16)
notes(s,'Le bas de la tablette comme zone d’acquittement reste une hypothèse utilisateur à confirmer. Dans la capture P2 Recording 10, ALERT_ML_LIGHT est visible vers 97,432 s ; l’export SUJ6 indique ALERT_ML_LARGE au même instant. Ne pas renommer les événements sans clarification.', ['docs/contexte/point_reunion_et_rapport.md'])

originals=[
('Comportements après les cinq alarmes','results/comparaison/vue_globale_AOI_alarmes/trois_etats/regard_7_sujets_5_alarmes_trois_bandes_appuis.png'),
('Temps : premier point FND et appui','results/comparaison/delais_durees_FND_7_sujets/grande_figure_5_zones_alarmes_7_sujets.png'),
('Variante : fixation mappée ≥100 ms','results/comparaison/fixations_FND_100ms/grande_figure_5_alarmes_fixations_100ms_appuis.png'),
('Comparaison descriptive en boîtes','results/comparaison/boites_5_alarmes_sans_fixation/boites_5_alarmes_premier_point_FND_appui.png'),
('Motif déplacement / maintien / retour','results/comparaison/FND_avec_acquittement/FND_comportement_visuel_acquittement.png')]
from PIL import Image
for title,src in originals:
    s=new(title,kicker='ANNEXE · FIGURE ORIGINALE',subtitle='Figure source conservée pour consultation ; zoomer pour les détails. Les graphiques précédents sont modifiables.')
    with Image.open(ROOT/src) as im:iw,ih=im.size
    scale=min(14.7/iw,6.05/ih);ww,hh=iw*scale,ih*scale
    s.shapes.add_picture(str(ROOT/src),Inches((16-ww)/2),Inches(2.2+(6.05-hh)/2),width=Inches(ww),height=Inches(hh))
    notes(s,'Image PNG originale, déplaçable et redimensionnable, mais ses éléments internes ne sont pas modifiables dans PowerPoint. Utiliser les graphiques natifs du corps de présentation pour modifier les points, lignes, bandes et textes. Les notes des diapositives précédentes précisent les limites méthodologiques.',[src])

OUT.mkdir(exist_ok=True)
path=OUT/'Presentation_Airbus_eye_tracking_modifiable.pptx';P.save(path)
source_manifest=[{'fichier':src,'sha256':hashlib.sha256((ROOT/src).read_bytes()).hexdigest()} for src in sorted(SOURCES)]
(OUT/'Presentation_Airbus_eye_tracking_modifiable.manifest.json').write_text(json.dumps({'diapositives':MANIFEST,'sources':source_manifest,'modification':'textes et graphiques principaux = objets PowerPoint natifs ; annexes = PNG originaux','date':'2026-11-10'},ensure_ascii=False,indent=2))
print(f'{path} : {len(P.slides)} diapositives, {path.stat().st_size/1e6:.2f} Mo')
