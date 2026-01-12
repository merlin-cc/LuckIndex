from Team import *
from tirage_foot import *
from draw_2026_WC import *

data = pd.read_csv('football_ranking.csv')
list_teams = teams_list(data)

distributions = run_simulation(list_teams, 3)
real_draw = single_draw(pots)
luckIndex = luck_index_foot(list_teams, distributions, real_draw)

display_random_foot(distributions, luckIndex, 3, 10)
plt.show()
