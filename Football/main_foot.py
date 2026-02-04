from Football.Team import *
from Football.tirage_foot import *
from Football.draw_2026_WC import *

data = pd.read_csv('football_ranking.csv')
list_teams = teams_list(data)

n_sim = 3

distributions = run_simulation_foot(list_teams, n_sim)
real_draw = single_draw(pots)
luckIndex = luck_index_foot(list_teams, distributions, real_draw)

teams_name = get_teams_name(data)
print(teams_name)

official_draw = get_official_draw_2026()
luckIndex_off = luck_index_foot(list_teams, distributions, official_draw)

display_random_foot(distributions, luckIndex_off, 7, n_sim)

plt.show()
