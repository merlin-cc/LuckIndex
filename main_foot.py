from Team import *
from tirage_foot import *
from draw_2026_WC import *



distributions = run_simulation(teams_list, 100)
real_draw = single_draw(pots)
luckIndex = luck_index_foot(teams_list, distributions, real_draw)

display_random_foot(distributions, luckIndex, teams_list, 3)
plt.show()
