# SUJ1 — examen des coupures de mapping

Analyse exploratoire des 131,06 secondes disponibles, sans AOI vidéo manuelles,
sans interpolation du regard et sans nouvelle génération de PDF.

## Résultats directement observés

- Regard valide et mappé dans le FND : **16,27 s**.
- Mapping absent mais regard vidéo valide : **111,57 s**.
- Mapping absent et regard indisponible/invalide : **3,22 s**.
- Aucun point mappé valide hors des limites de la photo dans cet export.
- 42 séquences sans mapping, y compris aux extrémités de l’enregistrement.

La plupart des absences de mapping ne sont donc pas une perte de mesure des yeux.
Cela ne démontre pas leur cause ni leur destination dans la scène.

## Autour du marqueur ALERT_FND (67,873922 s)

| Intervalle relatif | Observation |
|---|---|
| +0,80 à +1,01 s environ | Regard valide mappé dans le FND, en haut de la photo. |
| +1,01 à +1,60 s | Coupure de 0,59 s, regard valide sur toute la coupure ; déplacement important puis reprise du mapping. Compatible avec une excursion, destination hors FND non confirmée. |
| +1,60 à +3,76 s environ | Mapping disponible, déplacement vers la partie basse puis regard principalement en bas. |
| +3,76 à +5,25 s | Coupure de 1,49 s, regard valide environ 99 % du temps ; changements importants dans les coordonnées vidéo et la direction oculaire. Ce n’est pas un simple maintien immobile observable. Destination inconnue. |
| +7 s environ | Le regard rejoint une position vidéo proche de celle précédant l’alarme ; absence de mapping ensuite. Sans contour vidéo, la destination route reste une hypothèse. |

Voir [les traces](traces_autour_ALERT_FND.png). Fond bleuté : mapping absent.
Le premier panneau montre les coordonnées vidéo, le deuxième les directions
oculaires (œil gauche, degrés), le troisième uniquement les hauteurs réellement
mappées sur la photo. Les repères sont différents ; aucun contour du FND dans
la vidéo n’est déduit de ces courbes.

## Recherche automatique prudente sur l’ensemble de SUJ1

Les seuils exploratoires sont consignés dans `audit_SUJ1.json`. Ancrages :
au moins cinq points mappés dans les 150 ms avant et après chaque coupure.
Continuité compatible : coupure ≤250 ms, regard valide ≥90 %, direction du
même œil disponible ≥90 %, faible déplacement angulaire et vidéo, positions
mappées proches avant/après. Cette règle ne retient **aucune coupure** ici.
Cela ne prouve pas qu’aucune coupure ne correspond à un maintien : la règle
est restrictive et les fenêtres d’ancrage peuvent inclure des mouvements.

Deux coupures sont candidates à un déplacement suivi d’un retour de direction :
22,642–22,692 s et 105,372–108,968 s. La première est très brève (50 ms) et
particulièrement fragile ; la seconde dure 3,60 s. Aucune n’est une sortie du
FND confirmée. Un retour de direction des yeux ne garantit pas un retour à la
même zone physique et les ancrages sur la photo peuvent différer.

Les 39 autres coupures restent non tranchées ; une coupure de 40 ms a un
regard entièrement indisponible/invalide. Les catégories sont appliquées à
la coupure entière : les périodes invalides contenues dans des coupures plus
longues sont incluses dans le total de 3,22 s, pas seulement dans ces 40 ms.

## Limites et reproduction

Aucun seuil n’est validé par vidéo ou vérité terrain. Une saccade peut rester
dans le FND ; un mouvement peut aussi être lié à la tête ou à un artefact.
Les directions sont mesurées par rapport aux lunettes, sans compensation de
tête. Les catégories ne sont pas des preuves de « hors FND » et ne doivent
pas servir à calculer un temps de détection confirmé. Les durées sont
pondérées par les intervalles entre échantillons ; la dernière mesure est
prolongée d’une période médiane. Les coordonnées par échantillon ne sont pas
publiées : seuls les résumés de coupures, figures et paramètres le sont.

```bash
python3 scripts/coupures_mapping_suj1.py --sources /workspace/attachments
```

Le CSV décrit chaque coupure ; le JSON contient les seuils, l’empreinte de
la source et les statistiques. La figure d’ensemble conserve les coupures
non tranchées et ne remplit aucune période manquante.
