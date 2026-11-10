# Vue globale : sept sujets, cinq alarmes, FND et ML

[Figure PNG](regard_7_sujets_5_alarmes_FND_ML_appuis.png) ·
[Figure SVG](regard_7_sujets_5_alarmes_FND_ML_appuis.svg)

Cette vue reprend l’organisation de la figure historique : sept lignes
(sujets) et cinq colonnes (types d’alarme). Elle utilise uniquement les
coordonnées mappées et la master liste sur photo, conformément à la
clarification d’Élie. Les AOI vidéo manuelles ne sont pas utilisées.

Les cases couvrent 0 à 18 secondes après les marqueurs manuels d’apparition.
Le bleu indique le FND hors ML, le violet la master liste (incluse dans le
FND), le jaune une position dans le FND sans statut ML renseigné. Le gris
reste indéterminé : absence de mapping, regard invalide ou absence de données
en fin d’enregistrement. Aucune catégorie « hors FND » n’est inventée.

Les valeurs ML 0/1 ne sont interprétées qu’avec un regard valide et une
coordonnée mappée dans les limites de la photo du FND. Les bandes sont
pondérées par les intervalles entre échantillons ; une lacune de plus de
50 ms n’est pas prolongée. Aucun point n’est interpolé. Les géométries de
ML entre projets restent à vérifier. La photo FND est le cadre global,
la master liste est une sous-zone : les catégories ne se chevauchent pas.

Les étoiles et traits roses indiquent les appuis connus pour SUJ5–7,
mesurés en secondes depuis l’apparition de l’alarme jusqu’à l’appui.
Leur placement suppose une concordance entre cette apparition et le
marqueur manuel Tobii, qui reste à vérifier. Ce ne sont pas des clics
extraits des Excel Tobii. En l’absence de marqueur, la durée d’appui est
écrite dans la case mais aucun regard ni appui n’est placé dans le temps.
Les numéros des formats ne sont pas utilisés pour inventer un ordre d’essais.

Les réserves de prétraitement sont conservées : publicité SUJ1/RED,
repères approximatifs ou à vérifier SUJ3, apparitions non datées.
Les durées fournies ne remplacent pas les marqueurs d’apparition manquants.
Une absence de bande ML ne prouve pas une absence de regard ML dans les
périodes sans mapping ni une absence de détection de l’alarme. Pour FND,
tout le FND clignote ; la master liste n’est pas la seule zone pertinente.

## Reproduction et traçabilité

```bash
python3 scripts/vue_globale_aoi_alarmes.py --sources /workspace/attachments
```

Le script conserve un cache local ignoré par Git et vérifie l’empreinte
SHA-256 de chaque source avant de le réutiliser. Seuls les résumés par
fenêtre, périodes mappées, paramètres et figures sont publiés. Le CSV des
fenêtres renseigne séparément les marqueurs et les durées d’appui disponibles.
Un champ vide indique une fenêtre non datable, pas une durée nulle.
Le JSON conserve le nombre de cases, de repères et d’appuis effectivement
placés. Aucun PDF n’est généré.
