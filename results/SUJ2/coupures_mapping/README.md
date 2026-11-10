# SUJ2 — examen des coupures de mapping

Même méthode et mêmes seuils exploratoires que SUJ1. Aucune AOI vidéo
manuelle utilisée, aucun point interpolé, aucun PDF généré.

## Disponibilité sur tout l’enregistrement

| État | Durée |
|---|---:|
| Regard valide mappé dans le FND | 15,62 s |
| Mapping absent et regard vidéo valide | 78,06 s |
| Mapping absent et regard indisponible/invalide | 10,00 s |
| Total observé | 103,68 s |

Aucun point mappé valide n’est situé hors des limites de la photo.
21 coupures sont recensées, extrémités de l’enregistrement comprises.
Les absences de mapping ne sont pas automatiquement des regards hors FND.

## Autour de ALERT_FND

Le marqueur manuel est à 60,218640 s.

- Avant +0,96 s : pas de mapping disponible dans le zoom depuis −2 s.
- De +0,96 à +2,20 s : regard mappé dans le FND pendant environ 1,24 s.
  Il se situe principalement dans la partie basse de la photo et remonte
  rapidement à la fin. La hauteur seule n’identifie pas un appui ou une action.
- De +2,20 à +12,09 s : coupure de mapping de 9,89 s, avec regard valide
  pendant 95,0 % de cette coupure. La direction et les coordonnées vidéo
  changent nettement à plusieurs reprises ; ce n’est pas une simple
  interruption observable pendant un regard immobile.
- Vers +5,2 s, les traces se rapprochent de la position oculaire et vidéo
  précédant l’alarme. Un retour à la route reste une hypothèse, car la
  géométrie du FND dans la vidéo et les mouvements de tête ne sont pas connus.
- Le mapping reprend à +12,09 s, juste après le zoom limité à +12 s.

Voir [les traces autour de FND](traces_autour_ALERT_FND.png).
Fond bleuté : mapping absent. Premier panneau : regard vidéo valide ;
deuxième : direction de l’œil gauche dans le repère des lunettes ; troisième :
hauteur effectivement mappée sur la photo du FND. Ces repères sont distincts.

## Classement prudent des coupures

Aucune coupure ne remplit tous les critères de continuité dans le FND,
ni ceux d’excursion avec retour de direction. Cela ne démontre pas
l’absence de ces comportements : les critères exigent des ancrages avant
et après et des seuils restrictifs, qui ne sont pas validés par la vidéo.
15 coupures restent non tranchées ; 6 ont un regard majoritairement invalide.
Leurs durées entières ne sont pas à confondre avec le total exact de temps
invalide, qui comprend aussi les pertes de regard dans les autres coupures.

Cette méthode met en évidence les mouvements pendant les absences de mapping,
mais ne permet pas encore de transformer ces périodes en une AOI « hors FND »
confirmée. Aucun temps de détection ni acquittement n’est déduit.

## Reproduction et contrôle

```bash
python3 scripts/coupures_mapping_suj1.py --sources /workspace/attachments --subject SUJ2
```

Le script conserve sa compatibilité avec SUJ1 (valeur par défaut).
Le CSV contient les résumés par coupure ; le JSON contient les seuils,
l’empreinte de la source et les statistiques. Les durées utilisent les
intervalles entre échantillons, avec une période médiane pour la dernière
mesure. Les durées des coupures et du mapping ont été vérifiées comme
complémentaires, et les paramètres sont identiques à ceux de SUJ1.

## Distinction FND et master liste

Sur la fenêtre −2 à +12 s autour de ALERT_FND, aucun point valide mappé
n’est indiqué dans l’AOI ML. Les points sont distingués par l’indicateur
AOI exporté : rose = ML (incluse dans le FND), bleu-vert = FND hors ML.
La hauteur dans la photo ne suffit pas à identifier la master liste.
L’absence de point ML observé ne démontre pas une absence de regard ML
pendant les périodes sans mapping.
