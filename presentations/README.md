# Présentation Airbus — eye tracking et alarmes FND

[PowerPoint modifiable](Presentation_Airbus_eye_tracking_modifiable.pptx)

22 diapositives au format 16:9 :

- 1–2 : objectif, tâche, conditions et cinq formats d’alarme.
- 3–5 : synchronisation Figma/Tobii, ajout d’une zone écran principal,
  pistes d’analyse dans l’environnement Airbus ou ailleurs.
- 6 : définition des états et des mesures.
- 7–8 : comportements après les cinq alarmes, séparés par projet.
- 9–10 : premier point FND et appui, sans règle de fixation.
- 11–12 : variante avec fixation mappée continue ≥100 ms.
- 13 : boîtes descriptives et sujets individuels.
- 14–15 : origine et illustration du motif déplacement/maintien/retour.
- 16–17 : possibilités pour Airbus et questions à trancher.
- 18–22 : les cinq figures originales demandées, pour consultation en zoom.

## Ce qui est modifiable

Dans les diapositives 1 à 17, les textes, lignes, points, bandes, boîtes et
légendes sont des objets natifs PowerPoint : ils peuvent être sélectionnés,
déplacés, recolorés et réécrits. Les graphiques ne sont pas des captures
aplaties. Ils sont composés de formes, pas de graphiques liés à une feuille
Excel : les changements de données se font de préférence via le script
pour conserver l’échelle et la cohérence. Les objets peuvent être groupés
ou sélectionnés via le volet de sélection de PowerPoint.

Les diapositives 18 à 22 contiennent les images PNG originales : elles sont
déplaçables/redimensionnables, mais leur contenu interne n’est pas éditable.
Les figures sont reconstruites avec les mêmes mesures dans le corps de la
présentation ; les graphiques temporels denses sont répartis sur plusieurs
diapos pour rester lisibles. Les notes du présentateur conservent les
sources, méthodes et limites. Les cinq originaux restent la référence pour
les détails complets, notamment la validité par échantillon.

## Points de méthode préservés

- La photo entière correspond au FND ; ML est incluse dans le FND.
  Les AOI vidéo manuelles exclues ne sont pas réutilisées.
- Hors FND présumé = regard valide non mappé ; ce n’est pas une destination
  hors FND confirmée. Une erreur de mapping reste possible.
- Premier point, fixation ≥100 ms et appui sont trois mesures distinctes.
- Les appuis externes ne sont pas des clics retrouvés dans les Excel Tobii.
  Leur placement suppose des apparitions concordantes, à vérifier.
- Les boîtes reposent sur de petits effectifs variables. Les différences de
  sujets, projets, messages et disponibilités empêchent un classement d’efficacité.
- Le motif géométrique déplacement/maintien/retour reste exploratoire ;
  sa référence SUJ1 doit être revalidée indépendamment des AOI manuelles.
  La direction oculaire n’est pas une localisation dans la scène.
- Gemini sur le poste Airbus et le suivi de repères autour de l’écran sont
  des pistes, pas des capacités testées. La pseudonymisation n’est pas une
  garantie d’anonymat. Les possibilités de traitement doivent être vérifiées.

## Reproduction et vérification

```bash
python3 -m pip install -r requirements-presentation.txt
python3 scripts/presentation_airbus.py
```

Le script lit seulement les résultats agrégés et les figures existants.
Aucun Excel brut ni cache individuel n’est nécessaire. Le manifeste conserve
la liste des diapositives et les SHA-256 des sources. La structure ZIP,
les notes et les limites de page des objets ont été vérifiées ; les graphiques
ont été comparés aux résultats sources. Le contrôle de mise en page utilise
un aperçu géométrique ; aucun moteur Microsoft PowerPoint/LibreOffice n’est
disponible ici pour valider son rendu exact. Aucun nouveau PDF n’est généré.
