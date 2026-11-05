# Démonstration eye tracking — FND

Analyse exploratoire de **SUJ1 et SUJ2, projet 1** (clignotement manuel).
Le participant surveille une route sur l'écran principal et doit détecter les
alertes sur la tablette représentant le FND. Le projet 2 (automatisation Figma)
n'est pas encore analysé. Aucun résultat ne constitue une évaluation de compétence pilote.

## Figures déjà générées

![Chronologie](results/SUJ1/01_chronologie.png)
![Autour des alertes](results/SUJ1/02_fenetres_alertes.png)
![Indicateurs](results/SUJ1/03_indicateurs_AOI.png)

Les versions SVG sont disponibles pour les présentations. Les CSV agrégés et
`resume.json` donnent les valeurs numériques et les dénominateurs.

## Premiers constats

- Durée : 131,058 s ; 12 956 échantillons oculaires, pas médian 10,027 ms.
- Au moins un œil déclaré valide : 97,55 % des échantillons oculaires.
- Huit intervalles annotés de mapping du FND : 41,846 s, soit environ 31,9 %
  de l'enregistrement. Ce chiffre ne mesure pas directement la visibilité du FND.
- Cinq annotations d'alerte présentes. Les apparitions réelles et acquittements
  restent à synchroniser avec Figma ; aucun délai de détection n'est calculé.
- `ALERT_RED` : publicité signalée dans les notes de prétraitement.

## Méthode et limites

Seules les lignes `Sensor = Eye Tracker` servent aux indicateurs du regard :
les lignes gyroscope/accéléromètre ne doivent pas gonfler les effectifs.
Un échantillon est retenu si au moins un œil est `Valid`. Pour chaque AOI,
les valeurs 0 et 1 sont interprétées comme hors/dans l'AOI ; -1 et les cellules
vides comme non renseignées. Le pourcentage est calculé sur les échantillons
oculaires valides pour lesquels **cette AOI** est renseignée. La couverture
rapporte ce dénominateur à tous les échantillons oculaires.

Les AOI vidéo FND, Main screen et ML sont distinctes de l'AOI ML sur l'image
mappée `HLX FND1`. Elles peuvent être imbriquées ; ne pas additionner leurs
pourcentages ni assimiler les référentiels. L'AOI `Rectangle`, de signification
inconnue, n'est pas analysée. `HLX FND1` est aussi un nom de média/mapping dans
cet export : il n'est pas traité comme une colonne AOI supplémentaire.

Les graphiques représentent des échantillons de regard, pas des fixations
identifiées. Aucun temps de fixation n'est déduit du nombre de lignes.
Les traits gris regroupent données invalides et AOI non renseignées ; ils ne
permettent pas d'affirmer que le FND était hors champ. Les intervalles de mapping
ne constituent pas non plus une preuve de visibilité continue ou de fixation.
Regarder une zone ne prouve ni détection consciente ni compréhension.

Un seul sujet ne permet aucune comparaison manuel/auto ou généralisation.
Les notes de prétraitement des autres sujets seront intégrées quand leurs
exports seront disponibles. Les événements de synchronisation exportés sont
conservés dans le fichier source mais ne sont pas associés à Figma sans preuve.

## Relancer sans Python sur son ordinateur

Demander à l'assistant de lancer l'analyse dans le cloud en fournissant l'Excel,
ou ouvrir `notebooks/analyse_colab.ipynb` dans Google Colab et exécuter les cellules.
L'utilisation de Colab implique un transfert de données à ce service : utiliser
uniquement des données dont le transfert est autorisé par Airbus.

Pour l'environnement cloud :

```bash
cd /workspace/AirbusHelico
python3 -m pip install -r requirements.txt
python3 scripts/analyse_tobii.py /chemin/SUJ1.xlsx --output results/SUJ1
```

Le script attend le schéma des exports SUJ1/SUJ2, un seul sujet/enregistrement et une seule
feuille ; les futurs exports nécessiteront une vérification des noms d'AOI.
La réserve « publicité » est spécifique à SUJ1 et ne doit pas être propagée aux
autres sujets. Ne pas réutiliser ce script sans adaptation pour un autre sujet.

## Gestion des données

L'Excel original n'est pas versionné. `data/`, les Excel, vidéos et les CSV
échantillon par échantillon sont exclus de Git. Les sorties suivies contiennent
uniquement des temps relatifs, SUJ1 et des indicateurs descriptifs, sans noms,
dates d'acquisition ou captures. Il s'agit de pseudonymisation et non d'une
garantie d'anonymat. Conserver la correspondance des participants chez Airbus.
Vérifier les règles Airbus et la visibilité du dépôt avant d'ajouter des données
brutes ou d'autres données de participants.

## Suite attendue

Récupérer les temps Figma d'affichage et d'acquittement avec identifiants de
session/alerte et un repère commun à Tobii. Examiner ensuite la synchronisation,
la couverture autour de chaque événement et les réserves des essais avant
de calculer des délais. Pas de carte de chaleur sans image de référence et
validation des coordonnées mappées.

## SUJ2 — données disponibles

- 103,687 s ; 10 124 échantillons oculaires ; au moins un œil valide : 90,22 %.
- Six intervalles de mapping : 20,216 s (19,5 % de l’enregistrement).
- Une seule annotation : ALERT_FND à 60,219 s. Les quatre autres alertes sont
  absentes de l’export et signalées hors champ dans les notes de prétraitement.
  Ne pas les interpréter comme des alertes non détectées ou non présentées.
- Les colonnes AOI vidéo « Recording 5 » sont non renseignées pour SUJ2 ; ce
  sont des colonnes présentes dans l’export, sans données exploitables ici.
- Seule ML sur l’image mappée fournit des valeurs : 727 échantillons dans l’AOI
  parmi 1 870 valides et renseignés (38,88 %), couvrant seulement 18,47 % des
  échantillons oculaires. Ce résultat conditionnel ne mesure pas le regard
  sur l’ensemble de l’essai et ne permet pas une comparaison de performance.

![SUJ2 chronologie](results/SUJ2/01_chronologie.png)
![SUJ2 autour du marqueur FND](results/SUJ2/02_fenetres_alertes.png)
![SUJ2 indicateurs](results/SUJ2/03_indicateurs_AOI.png)

```bash
python3 scripts/analyse_tobii.py /chemin/SUJ2.xlsx --subject SUJ2 --output results/SUJ2
```

`qualite_alertes.csv` distingue les marqueurs présents et les réserves connues
pour chacune des cinq alertes attendues. Les heures des alertes absentes ne
sont pas reconstruites. Les réserves sont propres au sujet : la publicité ne
concerne que SUJ1. Les fichiers source et échantillons individuels restent exclus de Git.
