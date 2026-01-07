from Player import *
from tirage import *

data = pd.read_csv('tennisATPRanking.csv')

list_players = total_players_list(data)

distributions = run_simulation(list_players, 100)
real_draw = createDraws(list_players)
luckIndex = luck_index(list_players, distributions, real_draw)

display_random(distributions, luckIndex, list_players, 3)
