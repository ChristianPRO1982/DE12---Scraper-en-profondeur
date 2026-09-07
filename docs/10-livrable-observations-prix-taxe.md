# 10 - Livrable - Observations prix et taxe

Partie du brief liee : livrable final, note d'observation sur les champs de
prix et de taxe.

Cette note sera enrichie apres la collecte complete. Une premiere observation a
ete faite pendant la validation du collecteur de fiches produit.

Points verifies sur l'echantillon :

- valeur du prix hors taxe ;
- valeur du prix TTC ;
- montant de taxe ;
- coherence ou incoherence entre ces champs.

## Premiere observation

Sur les fiches observees pendant le crawl d'echantillon, les trois champs de
prix sont presents dans la table `Product Information`.

Constat provisoire :

- `Price (excl. tax)` est egal au prix affiche sur la page de liste ;
- `Price (incl. tax)` est egal a `Price (excl. tax)` ;
- `Tax` vaut `0.00` ;
- le nombre d'avis vaut `0` sur les fiches observees.

Conclusion provisoire :

- les champs doivent quand meme etre extraits separement, car le brief les
  demande explicitement ;
- il ne faut pas hardcoder l'egalite entre prix HT, prix TTC et prix de liste ;
- l'analyse finale devra etre confirmee apres collecte complete des 1 000
  fiches.
