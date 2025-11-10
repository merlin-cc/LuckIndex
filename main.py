from Player import *
from tirage import *

data = pd.read_csv('tennisATPRanking.csv')

list_players = total_players_list(data)

run_simulation(list_players, 100)