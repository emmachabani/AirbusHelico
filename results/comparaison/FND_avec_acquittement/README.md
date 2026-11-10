# ALERT_FND : comportement visuel et appui d’acquittement

[Figure déplacement, maintien, retour et appui](FND_comportement_visuel_acquittement.png).
[Planche directions H/V et points FND avec appui](directions_positions/7_sujets_directions_positions_FND.png).

Les appuis externes, en secondes depuis l’apparition de l’alarme, sont :
SUJ5 3,68 s, SUJ6 3,61 s, SUJ7 7,99 s. Aucun temps n’est attribué à SUJ1–4.
Leur placement sur les figures suppose que l’apparition utilisée pour ces
durées correspond au marqueur manuel Tobii. Cet alignement reste à vérifier ;
il ne s’agit pas d’une synchronisation mesurée. Aucun clic retrouvé dans
Tobii ni aucune position spatiale d’appui n’est inventé.

L’étoile rose représente l’appui sur la synthèse. Les traits roses pointillés
le représentent sur les courbes de direction, pas dans le plan spatial du FND.
L’appui n’est assimilé ni à la première détection visuelle ni à l’acceptation
par le prototype. Aucune différence appui/retour n’est interprétée avant
validation de l’alignement.

Le motif déplacement/maintien/retour conserve les anciens paramètres
exploratoires pour continuité de lecture. Sa référence SUJ1 doit être
revalidée indépendamment des AOI vidéo manuelles exclues ; ses destinations
ne sont pas confirmées. La stabilité dans le repère des lunettes n’est
pas une preuve de fixation du bouton ou d’une zone précise du FND.
Les directions H/V et positions mappées sont les observations récentes,
sans utilisation de ces AOI manuelles. Pour ALERT_FND, tout le FND clignote.

```bash
python3 scripts/figures_acquittement_fnd.py
```

Requiert les caches locaux créés par `extraire_fnd.py` et
`regard_fnd_7_sujets.py`. Les sorties publiées sont des figures et résumés,
sans Excel ni données par échantillon. Aucun PDF généré.

## Version avec les zones mappées

[Comportement visuel, AOI et appui](FND_comportement_visuel_acquittement_AOI.png).
Sous chaque ligne, la bande encode FND hors ML (bleu), ML incluse dans le
FND (violet), FND avec statut ML inconnu (jaune) et position indéterminée
(gris clair). Ce gris inclut les absences de mapping et mesures invalides ;
il n’est pas une AOI hors FND. Les lignes et symboles du comportement visuel
sont conservés, ainsi que les appuis externes conditionnellement alignés.
Le CSV fournit les périodes effectivement mappées ; le JSON leurs durées.
Les intervalles sont pondérés par les écarts entre échantillons, limités
aux 12 secondes, sans prolonger une lacune de plus de 50 ms.

```bash
python3 scripts/comportement_fnd_aoi.py
```
