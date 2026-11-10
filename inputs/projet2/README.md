# Temps de réaction déclarés — projet 2

Tableau fourni par l’utilisatrice pour SUJ5, SUJ6 et SUJ7 : 15 valeurs,
une par sujet et type d’alarme. La capture jointe donne la correspondance :

| Numéro | Type dans les exports | Présentation décrite/illustrée |
|---|---|---|
| 1 | ALERT_ML_LIGHT | ML Light, exemple CARGO FIRE sur la capture |
| 2 | ALERT_ML_LARGE | ML Large, exemple ENG 1 / FIRE sur la capture |
| 3 | ALERT_FND | Tout le FND clignote, confirmé par l’utilisatrice |
| 4 | ALERT_RED | RED, exemple FADEC FAIL sur fond rouge sur la capture |
| 5 | ALERT_TEXT | TEXT, exemple OVERSPEED sur la capture |

Les numéros identifient les formats dans ce tableau ; ils ne prouvent pas
l’ordre temporel de présentation pour chaque sujet.
Les différences exactes entre ML Light et ML Large (taille, intensité,
contour, clignotement, etc.) ne sont pas déduites des seuls noms.
La capture montre aussi des messages différents selon les formats :
la comparaison n’isole donc pas nécessairement le seul effet graphique.

## Statut des valeurs

Les valeurs sont transcrites sans modification dans
`temps_reaction_declares.csv`. L’utilisatrice confirme que les valeurs sont en secondes, entre
l’apparition de l’alarme et l’appui d’acquittement. Elles mesurent un délai
de réponse comportementale ; elles ne datent pas la détection consciente
ni l’acceptation de l’acquittement par le prototype. Aucun horodatage absolu des appuis
n’est fourni. Ces données sont externes aux exports Tobii et ne sont
pas des délais de premier regard.

Ne pas additionner ces durées aux marqueurs manuels Tobii pour créer des
horodatages d’acquittement avant validation de la correspondance
des essais, de l’équivalence des repères d’apparition et de la synchronisation. La présence de cinq durées par sujet
ne fournit pas les marqueurs d’apparition manquants dans les exports.
Les notes de prétraitement et leurs réserves sont conservées.

Les durées pourront servir à comparer les réponses comportementales aux
formats, puis à décomposer orientation visuelle et réponse si les repères
communs sont disponibles. Avec trois sujets et un essai par case, présenter
les valeurs individuelles et conserver les limites du protocole.

La capture inline n’est pas archivée comme fichier image dans le dépôt ;
la correspondance ci-dessus en conserve les informations fournies.
