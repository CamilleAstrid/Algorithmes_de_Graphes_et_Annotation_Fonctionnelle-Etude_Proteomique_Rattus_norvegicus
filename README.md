# Algorithmes de Graphes et Annotation Fonctionnelle : Etude Proteomique de _Rattus norvegicus_
Ce dépôt contient le code, les données et les résultats associés à l'analyse bioinformatique du protéome de _Rattus norvegicus_.
Ce projet a été réalisé dans le cadre du Master 1 Bioinformatique et Biologie des Systèmes à l'Université Paul Sabatier Toulouse III, année universitaire 2024-2025.

## Description
Ce répertoire contient des outils Python pour l'analyse et la manipulation des données de la Gene Ontology (GO), avec une application spécifique à l'organisme _Rattus norvegicus_.
Il fournit des fonctionnalités pour charger, explorer et analyser les relations entre GeneProducts et GOTerms à partir de fichiers au format OBO et GAF/GOA.

## Fonctionnalités
* Chargement des données GO à partir des fichiers OBO et GAF/GOA.
* Représentation des graphes GO avec une structure en listes d’adjacence.
* Exploration des relations entre GeneProducts et GOTerms (directes et récursives).
* Calcul de la profondeur maximale d’un graphe (diamètre).
* Vérification de l’acyclicité et tri topologique des graphes.
* Tests unitaires pour garantir la robustesse des outils.

## Structure du projet

Algorithmes_de_Graphes_et_Annotation_Fonctionnelle-Etude_Proteomique_Rattus_norvegicus
* `README.md` : Documentation du projet
* `LICENSE` : License appliquée à l'ensemble du projet
* `rapport_projet_Graph_R.norvegicus_RODRIGUES.pdf` : Rapport d'ingénierie sur les outils développés.
* **scripts/** : Dossier abritant l'ensemble des fichiers python
  * `geneontology.py` : Code pour les analyses spécifiques à la Gene Ontology
  * `graphmaster.py` : Bibliothèque générique de manipulation de graphes
  * `test_graphmaster.py` : Tests unitaires pour la bibliothèque `graphmaster.py`
* **data/** : Dossier regroupant les données utilisées pour l'analyse de _Rattus norgevicus_ et pour les tests effectués.
  * `go-basic.obo` : Exemple de fichier OBO pour la Gene Ontology
  * `122.R_norvegicus.txt` : Fichier contenant un lien vers le fichier GOA pour les annotations de _Rattus norvegicus_
  * `test_protein_51145.txt` : Fichier contenant les informations pour créer un graphe à partir des données de la protéine 51145.
  * `directed.graph.with.cycle.tsv` : Fichier contenant les informations pour charger le graphe simple figurant sur la représentation graphique `directed.graph.with.cycle.png`
  * `uniprot_sars-cov-2.gaf` : Fichier au format GAF permettant de tester sur un jeu de données plus petit les programmes développés

## Prérequis
* Python >= 3.8
* Bibliothèques Python standards (aucune dépendance externe requise)

## Installation et utilisation
1. Clonez ce repository et placez-vous dans le répertoire du projet :
  ```bash
  git clone https://github.com/CamilleAstrid/Algorithmes_de_Graphes_et_Annotation_Fonctionnelle-Etude_Proteomique_Rattus_norvegicus.git
  cd Algorithmes_de_Graphes_et_Annotation_Fonctionnelle-Etude_Proteomique_Rattus_norvegicus
  ```
2. Assurez-vous d'avoir Python et les dépendances nécessaires installés.
3. Exécutez les scripts pour reproduire les analyses :
  ```bash
  python scripts/geneontology.py <input_file.GOA>
  ```
  /!\ Si le fichier en input n'est pas renseigné, le fichier `122.R_norvegicus.goa` sera utilisé. S'il n'est pas présent à l'emplacement du programme, il sera téléchargé depuis l'url figurant dans le fichier `122.R_norvegicus.txt`.
  
## Tests
Pour exécuter les tests unitaires et vérifier la robustesse des outils :
  ```bash
python test_graphmaster.py
  ```

## Licence

Ce projet et donc l'ensemble des éléments de ce répertoire est sous licence [GPL-v3](LICENSE) (sauf cas précisé).

## Auteurs

Copyright (c) 2023 BARRIOT Roland

Copyright (c) 2025 CamilleAstrid

Inspiré des travaux sur la Gene Ontology pour _Rattus norvegicus_.
