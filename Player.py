import pandas as pd
import numpy as np

class TennisPlayer():
    def __init__(self, name : str, country : str, rank : int , elo : int ):
        self.name = name
        self.country = country
        self.rank = rank
        self.elo = elo

def players_list(data, min_rank, max_rank):
    assert min_rank>0, "the minimal rank must be >= 1"
    res = []
    for rank in range(min_rank, max_rank + 1):
        res.append(TennisPlayer(data.loc[rank-1]['Name'], data.loc[rank-1]['Country'], data.loc[rank-1]['Rank'], data.loc[rank-1]['Points']))

    return res


def total_players_list(data):
    best_104_players = players_list(data,1, 104)

    players_105_to_200 = players_list(data,105, 200)
    elos_105_to_200 = [player.elo for player in players_105_to_200]
    #we consider that the player is french and his rank is 105 
    #qualified_player = TennisPlayer("Qualified", "France", 105, np.mean(elos_105_to_200)) 
    total_players = best_104_players + [TennisPlayer("Qualified", "France", 105, np.mean(elos_105_to_200))]*24

    return total_players

