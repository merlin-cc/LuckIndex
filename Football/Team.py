import pandas as pd
import numpy as np


### ---------------------------------------------------------------------------------------- Code Objective --------------------------------------------------------------------------------------- ###
###                                                           The object representing a FootTeam and the list of FootTeam are defined here                                                          ###
#######################################################################################################################################################################################################

class FootTeam():
    def __init__(self, name : str, rank : int , elo : int ):
        self.name = name
        self.rank = rank
        self.elo = elo

def teams_list(data : pd.DataFrame) -> list[FootTeam]:
    res = []
    for k in range(len(data)):
        res.append(FootTeam(data.loc[k]['Team'], data.loc[k]['Rank'], data.loc[k]['Rating']))
    return res

def total_teams_index(list_teams : list[FootTeam]) -> dict[str, FootTeam]:
    res = {}
    for p in list_teams:
        res[p.name] = p
    return res
