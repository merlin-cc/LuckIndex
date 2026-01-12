import pandas as pd
import numpy as np

class FootTeam():
    def __init__(self, name : str, rank : int , elo : int ):
        self.name = name
        self.rank = rank
        self.elo = elo


def teams_list(data : pd.DataFrame, min_rank : int, max_rank : int) -> list[FootTeam]:
    assert min_rank>0, "the minimal rank must be >= 1"
    res = []
    for rank in range(min_rank, max_rank + 1):
        res.append(FootTeam(data.loc[rank-1]['Team'], data.loc[rank-1]['Rank'], data.loc[rank-1]['Rating']))
    return res

def total_teams_index(list_players : list[FootTeam]) -> dict[str, FootTeam]:
    res = {}
    for p in list_players:
        res[p.name] = p
    return res
