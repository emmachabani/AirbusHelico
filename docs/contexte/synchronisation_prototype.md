# Proposition : repère visuel et journal d’événements du prototype

Proposition pour de futures acquisitions, non implémentée ni testée dans Figma.

## Principe

Afficher sur la tablette un repère unique qui apparaît à la fois dans le
journal de l’application et dans la vidéo des lunettes. Il sert à relier
l’horloge du prototype et le temps de l’enregistrement Tobii. Ce repère ne
remplace pas l’enregistrement des apparitions d’alarmes et des appuis.

Éviter de compter sur une unique image très brève : elle peut être manquée
par la caméra, cachée ou illisible. Prévoir un code de session et un compteur
ou un motif à contraste élevé, maintenu assez longtemps pour être visible
sur plusieurs images (par exemple 200–500 ms, à vérifier avec la cadence
réelle de la vidéo). Tester sa lisibilité avec le cadrage et l’exposition.

Afficher des repères identifiables **au début et à la fin**, idéalement aussi
entre blocs : un seul repère estime un décalage mais ne permet pas de vérifier
la dérive. Éviter des signaux supplémentaires saillants pendant les essais,
qui pourraient attirer le regard et modifier la mesure de détection.

## Journal à enregistrer

Une ligne par événement, avec identifiants pseudonymisés :

| Champ | Rôle |
| --- | --- |
| session_id, participant_id, project_id | Relier les bonnes acquisitions |
| trial_id, alarm_type, event_id | Identifier chaque essai et occurrence |
| event_name | SYNC_MARKER, ALARM_ONSET, BUTTON_DOWN, ACK_ACCEPTED, ALARM_OFFSET |
| t_monotonic_ms | Temps précis relatif à une même horloge d’exécution |
| t_unix_ms | Repérage global complémentaire ; ne pas dépendre de lui seul |
| sync_code | Faire correspondre le repère visuel et le journal |
| target_id | Identifier la zone ou le bouton touché |
| timestamp_basis | Callback applicatif, estimation de rendu ou mesure externe |
| state_before, state_after | Vérifier l’effet de l’appui et le changement de l’alarme |

`BUTTON_DOWN` et `ACK_ACCEPTED` sont distincts : un toucher peut ne pas être
accepté, viser une autre zone ou ne pas produire l’effet attendu. Conserver
les appuis erronés, répétitions et annulations, sans écraser les événements.
Définir ce que signifie « apparition » : demande de changement d’état,
estimation de rendu ou première image effectivement visible. Un callback
ou requestAnimationFrame n’est pas une preuve de l’apparition physique à l’écran.

## Mise en œuvre avec les maquettes Figma

Vérifier que le mode de lecture du prototype permet réellement de conserver
et d’exporter ces événements horodatés. Un compteur dessiné sur une frame
ne crée pas à lui seul un journal de présentation et d’interactions.
Si le lecteur n’offre pas le logging nécessaire, prévoir un lecteur instrumenté
ou une maquette web équivalente avec les mêmes visuels et comportements.
Ne pas annoncer un export automatique Figma avant de l’avoir testé.

## Alignement et contrôle

1. Enregistrer les repères de session dans le prototype et les identifier
   dans la vidéo Tobii, avec leur temps d’apparition observé.
2. Ajuster le décalage et, avec plusieurs repères, vérifier une dérive :
   `t_Tobii = a + b × t_prototype` après conversion dans la même unité.
3. Examiner les écarts des repères, la cadence vidéo, les pertes d’images,
   les latences d’affichage et les changements d’horloge. Au moins trois
   repères permettent de contrôler les résidus plutôt que faire passer
   exactement une droite par seulement deux points.
4. Valider sur quelques essais filmés : apparition, doigt au contact,
   appui accepté et changement de l’interface doivent être cohérents.
5. Documenter l’incertitude temporelle ; ne pas annoncer une précision
   meilleure que la vidéo et la validation ne le permettent.

## Analyses alors possibles

- Apparition → premier regard vers l’instrument.
- Apparition → première fixation dans l’AOI propre à l’alarme.
- Premier regard/fixation → appui, puis appui → acquittement accepté.
- Maintien et exploration du FND, puis retour à la tâche principale.
- Comparaisons intra-sujet avec plusieurs répétitions, ordre contrôlé et
  même protocole ; comparaisons entre participants ensuite.

Le regard, le toucher et l’effet de l’interface restent trois mesures
distinctes. Même un appui accepté ne prouve pas à lui seul la compréhension.
