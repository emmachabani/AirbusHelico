# Correction prioritaire après clarification d’Élie

Élie a fourni une photo du FND à Tobii pour l’Automatic Gaze Mapping,
puis dessiné la master liste sur cette image de référence. Les coordonnées
mappées et l’AOI master liste sur image constituent le périmètre retenu.
Toutes les autres AOI ont seulement été commencées à la main et doivent
être exclues, même si leurs colonnes contiennent des valeurs chez SUJ1.
La photo de référence ne constitue pas en soi une AOI FND globale validée.

Conséquences : retirer les synthèses toutes AOI, les interprétations
route/tablette et les délais fondés sur les AOI vidéo. Les valeurs
0,79 s, 2,15 s, etc. ne doivent plus être présentées comme résultats
exploitables. Les figures historiques restent traçables, mais sont obsolètes.
Les positions mappées et les tiers géométriques peuvent être conservés.
Le motif déplacement/maintien/retour et ses fenêtres restent exploratoires :
sa référence SUJ1 doit être revalidée indépendamment des AOI exclues.
Les destinations route/FND et un acquittement ne sont pas confirmés.
Les temps du commentaire se rapportent au traitement automatique de mapping ;
ne pas les confondre avec un temps de détection ou d’acquittement.

Les notes historiques ci-dessous doivent être lues sous cette correction.

---

# Contexte à conserver pour le rapport après la réunion

Note de travail, pas le rapport final. L’utilisatrice prévoit de demander le
rapport après sa réunion de vendredi ; aucune date précise ni exécution
automatique n’est programmée ici. Intégrer alors les réponses de la réunion.

## But de la démonstration Airbus

Illustrer les possibilités de l’eye tracking à partir d’un montage exploratoire :
surveillance d’une route sur écran principal et alarmes sur une tablette FND.
Présenter des observations de regard, pas une évaluation de compétence pilote.
P1 = déclenchement manuel du clignotement, SUJ1–4 ; P2 = automatique, SUJ5–7.
La définition précise de chaque condition reste à confirmer.

## Figures à privilégier

- [Déplacement, maintien et retour, fenêtre étendue à 12 s](../../results/comparaison/mouvements_FND/04_deplacement_maintien_retour_12s.png).
- [Positions sur le FND, ordre et temps pour sept sujets](../../results/comparaison/positions_FND/positions_FND_7_sujets_ordre_temps.png).
- [Synthèse détaillée SUJ1](../../results/SUJ1/synthese/SUJ1_synthese_complete.pdf).
- [Consultation de plusieurs régions du FND chez SUJ1](../../results/SUJ1/synthese/04_sequence_zones_FND.png).

L’utilisatrice préfère la figure déplacement/maintien et les vues spatiales
numérotées/colorées. La liste de fixations Tobii en lignes n’est pas sa
représentation préférée pour la présentation.

## Ce que change la nouvelle figure des retours

L’ancienne recherche s’arrêtait à +5 s : seuls SUJ3 et SUJ5 avaient un retour.
En conservant la recherche du motif initial sur 0–5 s et le même critère de
retour, mais en observant jusqu’à +12 s : SUJ1 revient à environ 7,05 s,
SUJ2 à 5,20 s, SUJ3 à 2,65 s, SUJ5 à 3,80 s et SUJ7 à 11,00 s.
SUJ6 n’a pas de retour répondant au critère avant +12 s. SUJ4 n’a pas de
motif initial retenu et ses données sont partielles : le retour n’est pas évalué.

Il s’agit d’un retour proche de la position des yeux **dans le repère des
lunettes**, pas d’un retour à la route confirmé. La tête n’est pas compensée.
Seuil de retour : moins de 5° de la position médiane initiale pendant trois
bins valides consécutifs de 50 ms. L’absence de retour dans la fenêtre n’est
pas une absence de retour ultérieur. L’allongement de la fenêtre était une
analyse exploratoire, pas une hypothèse préenregistrée.

## Hypothèse d’action sur le bas du FND

L’utilisatrice pense que l’acquittement se faisait en bas de la tablette, mais
n’en est pas sûre. Conserver cette proposition comme hypothèse jusqu’à la réunion.
Ne pas créer une AOI de clic précise ni appeler une fixation « acquittement ».
Chez SUJ1 après FND : regard haut à +0,79 s, bref retour route +1,26 à +1,54 s,
milieu à +1,63 s, bas à +1,79 s, déplacement vers la droite dans le bas à +3,48 s.
Le maintien géométrique à +1,90 s est déjà dans la région basse.

## Captures reçues et divergence à vérifier

Les trois captures envoyées dans la conversation sont décrites dans
[l’inventaire des captures](captures/README.md). Les originaux PNG/JPG n’étaient
pas accessibles comme fichiers dans l’espace de travail ; ils ne sont donc
pas encore versionnés. Ne pas confondre cette description avec un archivage
des images. Les ajouter tels quels lorsque les fichiers seront joints.

Point nouveau : les captures P2 / Recording 10 montrent un événement
`ALERT_ML_LIGHT` à 01:37.432. L’export SUJ6 indique `Project2`, `Recording 10`,
durée 210208 ms et un événement `ALERT_ML_LARGE` à 97,431977 s. La concordance
du nom d’enregistrement et du temps rend cette différence importante à vérifier.
Elle ne prouve pas à elle seule l’origine de la divergence. Ne pas renommer
les événements dans les résultats sans clarification de la version et de
la correspondance capture/export.

## Questions de protocole pour la réunion

1. Où apparaît chaque type d’alarme ? Que signifient exactement FND, ML_LARGE,
   ML_LIGHT, RED et TEXT, et quelles sont les AOI correspondantes ?
2. Où fallait-il toucher pour acquitter : zone précise, bouton ou tout le FND ?
   Que déclenche l’appui : disparition, arrêt du clignotement, changement de page ?
3. Les marqueurs d’apparition manuels sont-ils à la première image visible ?
   Confirmer les réserves de SUJ3 et la divergence ML_LIGHT/ML_LARGE ci-dessus.
4. P1 et P2 diffèrent-ils seulement par l’automatisation ou aussi par les timings,
   les images, l’ordre et le comportement des alarmes ? Même participants ou non ?
5. Quels temps d’apparition et d’appui Justine a-t-elle conservés, avec quel
   identifiant de session, quelle horloge et quelle précision ?
6. À quel projet se rattachent les notes initiales SUJ5–7 ?
7. Peut-on fournir les images de référence isolées et les vidéos pour valider
   les destinations du regard et les contacts visibles ?
8. À quoi correspondent les sorties SyncPortOutHigh/Low ? Ne pas les traiter
   comme des clics tant que leur signification n’est pas documentée.

## Synchronisation proposée pour une prochaine acquisition

Voir [la proposition d’instrumentation](synchronisation_prototype.md).
Le repère visuel et un journal horodaté d’événements doivent être conçus ensemble.
Les données pourront ensuite distinguer apparition, regard, appui et réponse
effective de l’interface. Aucun mécanisme de logging Figma n’est encore implémenté.

## Complément : exploration entre maintien et retour

L’utilisatrice demande de retirer les références à l’ancienne fenêtre sur
la figure. La version épurée conserve les mêmes événements sans afficher
cette histoire de traitement. Une nouvelle figure
[cartographie temporelle haut/milieu/bas](../../results/comparaison/regions_FND/FND_maintien_exploration_retour.png)
montre les régions de l’image FND visibles entre la fin du maintien et le
retour. Le cadre noir indique cet intervalle et le gris reste « non
attribuable », jamais « regard ailleurs ».

Résultats descriptifs à confronter à la vidéo : chez SUJ1, les observations
comprennent bas, milieu, de nouveau bas et haut avant le retour, avec
des lacunes ; seuls 35 % de cet intervalle sont attribuables à une région
selon le critère retenu. SUJ5 montre essentiellement le bas sur la partie
attribuable (69 % de l’intervalle). SUJ7 a des observations dans plusieurs
hauteurs mais seulement 44 % de l’intervalle est attribuable. Ne pas
présenter les régions séparées par du gris comme une trajectoire continue.

Les limites des tiers sont géométriques (1/3 et 2/3 de l’image), sans
correspondance fonctionnelle validée. À la réunion, demander les zones
exactes de l’alarme et de réponse avant de remplacer ces tiers par des
AOI « alarme » / « bouton » et avant de nommer des étapes de détection
ou d’acquittement.

## Précision sur les formats d’alarme

L’utilisatrice précise que, pour ALERT_FND, **tout le FND clignote**.
Les autres formats concernent notamment une alarme dans la master liste,
une présentation rouge ou du texte. Faire confirmer la correspondance précise
ML_LARGE / ML_LIGHT / RED / TEXT avec les zones et changements visuels.
Ne pas supposer que la master liste est la cible de ALERT_FND ni utiliser
l’absence de point ML comme un critère de non-détection de cette alarme.

## Nouvelle correspondance des alarmes et durées externes P2

L’utilisatrice fournit une capture identifiant les formats :
1 = ML_LIGHT, 2 = ML_LARGE, 3 = FND, 4 = RED, 5 = TEXT.
Les numéros ne sont pas assimilés à un ordre temporel des essais.
Un tableau donne 15 temps de réaction pour SUJ5–7 ; voir
[les données transcrites et leur statut](../../inputs/projet2/README.md).
L’utilisatrice confirme : secondes, de l’apparition de l’alarme à
l’appui d’acquittement. Il reste à vérifier la correspondance des essais
et des repères d’apparition avant de placer les appuis sur la timeline Tobii. Ces durées externes ne changent pas
le constat d’absence de clic identifiable dans les exports Tobii seuls.
