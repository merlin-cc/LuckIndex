from Team import *
from tirage_foot import *
from draw_2026_WC import *

data = pd.read_csv('football_ranking.csv')
teams_list = teams_list(data, 1, len(data))

distributions = run_simulation(teams_list, 1)
real_draw = single_draw(pots)
luckIndex = luck_index_foot(teams_list, distributions, real_draw)

display_random_foot(distributions, luckIndex, teams_list, 3, 10)
plt.show()
