# LuckIndex

Maths et sports : Construire un site internet "luck index" : pour divers tirages au sort de compétitions sportives (football, rugby, tennis, basketball, handball, etc), on classe les joueurs ou les équipes du plus chanceux au moins chanceux lors du tirage, de manière objective et scientifique. Pour cela, on construit pour chaque joueur la distribution de proba de la force de l'adversaire (ou force moyenne des adversaires), on regarde la force de l'adversaire tiré au sort lors du vrai tirage, on calcule la p-valeur : probabilité d'avoir eu un tirage plus difficile. On classe alors les joueurs par ordre de p-valeur. La force d'un joueur peut être un Elo rating, classement ATP, etc. Le but est de créer un site internet qui enregistre et illustre le luck index.
Voir section 5.1.2 "luck index" dans ce papier : https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5413142
et voir aussi https://driven-by-data.net/2014/06/06/luckydraw
Construire la distribution de proba de la force de l'adversaire n'est pas toujours facile, ça dépend de la procédure de tirage au sort.
