# Trois bandes distinctes après les alarmes

[Figure PNG](regard_7_sujets_5_alarmes_trois_bandes_appuis.png)
· [SVG](regard_7_sujets_5_alarmes_trois_bandes_appuis.svg)

Chaque case reprend le principe de la figure historique :
- bande haute violette : dans ML ;
- bande médiane bleue : hors ML, dans le FND ;
- bande basse vert clair : hors FND **présumé**, défini comme un regard
  déclaré valide par au moins un œil, sans position mappée dans le FND ;
- absence de bande sur fond gris : regard invalide/absent ou absence de
  données. Un regard dans le FND avec statut ML inconnu est indiqué en jaune.

Une seule bande est active par instant. La troisième catégorie reste une
hypothèse : un échec de mapping avec regard valide peut aussi l’expliquer.
Elle ne doit pas être présentée comme une AOI hors FND mesurée ou confirmée.
L’indicateur utilisé est la validité oculaire exportée, pas un contour du
FND dans la vidéo. Les trois bandes servent à distinguer explicitement
absence de mapping et absence de suivi valide.

Les marqueurs d’appui sont externes et conditionnellement alignés sur les
apparitions manuelles Tobii. Aucune chronologie n’est inventée si le repère
manque. Les réserves de prétraitement et l’exclusion des AOI vidéo manuelles
restent appliquées. Aucun PDF généré.

```bash
python3 scripts/vue_globale_trois_etats.py
```

Réutilise le cache local de `vue_globale_aoi_alarmes.py`, après vérification
de l’empreinte des Excel. Les CSV et l’audit correspondent à cette version.
