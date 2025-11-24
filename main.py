from Player import *
from tirage import *

data = pd.read_csv('tennisATPRanking.csv')

list_players = total_players_list(data)

distributions = run_simulation(list_players, 100)

real_draw = createDraws(list_players)
luckIndex = luck_index(list_players, distributions, real_draw)


#n_player = 30
#mu, sigma = distributions[list_players[n_player]]

#print(mu, sigma)
#print(luckIndex[list_players[n_player]])
#print(list_players[n_player].name)
#print([real_draw[list_players[n_player]][k].name for k in range(3)])

#X = np.linspace(-500 ,2000, 10000)

#plt.plot(X, norm.pdf(X,mu, sigma))
#plt.axvline(x=(1-luckIndex[list_players[n_player]]) * 2000, ymin=0, ymax=1, color = 'red')

display_random(distributions, luckIndex, list_players, 3)

plt.show()