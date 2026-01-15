# LuckIndex

Maths et sports : Construire un site internet "luck index" : pour divers tirages au sort de compétitions sportives (football, rugby, tennis, basketball, handball, etc), on classe les joueurs ou les équipes du plus chanceux au moins chanceux lors du tirage, de manière objective et scientifique. Pour cela, on construit pour chaque joueur la distribution de proba de la force de l'adversaire (ou force moyenne des adversaires), on regarde la force de l'adversaire tiré au sort lors du vrai tirage, on calcule la p-valeur : probabilité d'avoir eu un tirage plus difficile. On classe alors les joueurs par ordre de p-valeur. La force d'un joueur peut être un Elo rating, classement ATP, etc. Le but est de créer un site internet qui enregistre et illustre le luck index.
Voir section 5.1.2 "luck index" dans ce papier : https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5413142
et voir aussi https://driven-by-data.net/2014/06/06/luckydraw
Construire la distribution de proba de la force de l'adversaire n'est pas toujours facile, ça dépend de la procédure de tirage au sort.


# Que faire en ce moment ?

- Traitement des données (classement des joueurs avec leurs ATP...)
- Création du tirage selon les règles de Rolland Garros
- Simulation pour avoir la distribtion de probas et la force selon les tirages
- Calcul du luck index pour un tirage donné. (fictif ou réel)
- Pour compléter le tirage (24 autres joueurs), on cree un joueur "qualilfié" dont la force est la moyenne de la force des joueurs rank 105 à 208.
- Passer de pyscript à Flask.
- Présenter les courbes.
- Permettre de creer une poule.
- Permettre à l'utilisateur de choisir un nom parmi une liste défilante.
- Faire une analyse sur le site pour que des novices puissent comprendre les résultats.

- Regle Tournoi Roland Garros
- Display le classement ATP utilisé
- regle de Roland Garros
- Ajout des exceptions pour eviter des tirages interdits
- foot :
- fonctionnement du luck index
- heritage
- adapter les fonctions de tirage.py

- si on ne choisi pas les joueurs dans le manual  OK
- ajouter les signatures des fonctions
- plot le tirage
- mettre uniquement les pays particpant a la cdm dans les options lors de 'choisir l'equipe' OK
- enregister les distributions de foot et juste les exploiter, les faire en live est bcp trop long
- pour le tirage officiel : #traiter les UEFA (pas indiqués comme il faut sur le dict + calculer les histoires de adversaire possible.) [dans draw_2026_WC]
- essayer d'avoir un api atp


