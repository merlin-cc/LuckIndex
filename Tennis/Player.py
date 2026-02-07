import pandas as pd
import numpy as np

### ---------------------------------------------------------------------------------------- Code Objective --------------------------------------------------------------------------------------- ###
###                                                 Defining the structure of the object 'TennisPlayer' and several functions to get the list of players                                            ###
#######################################################################################################################################################################################################



class TennisPlayer():
    def __init__(self, name : str, rank : int , elo : int ):
        self.name = name
        self.rank = rank
        self.elo = elo


def players_list(data : pd.DataFrame, min_rank : int, max_rank : int) -> list[TennisPlayer]:
    """
    Returns a list that contains the data of the DataFrame stored a TennisPlayer per
    player
    """
    assert min_rank>0, "the minimal rank must be >= 1"
    res = []
    for rank in range(min_rank, max_rank + 1):
        res.append(TennisPlayer(data.loc[rank-1]['Player'], data.loc[rank-1]['ATP_Rank'], data.loc[rank-1]['cElo']))
    return res


def total_players_index(list_players : list[TennisPlayer]) -> dict[str, TennisPlayer]:
    """
    Create a dictionnary that associate each player name to the TennisPlayer
    that contains the data of the player
    """
    res = {}
    for p in list_players:
        res[p.name] = p

    return res


def get_players_name(data : pd.DataFrame) -> list[str]:
    """
    Returns a list with the names of all the players
    """
    players_list = total_players_list(data)
    list_name = []
    for player in players_list:
        list_name.append(player.name)
    return list_name


def total_players_list(data : pd.DataFrame) -> list[TennisPlayer]:
    """
    Returns a list with the 104 best players (according to the ATP ranking)
    that will participate the tournament
    """
    best_104_players = players_list(data,1, 104)

    players_105_to_300 = players_list(data,105, 300)
    elos_105_to_300 = [player.elo for player in players_105_to_300]
    #we consider that the player is french and his rank is 105 
    #qualified_player = TennisPlayer("Qualified", 105, np.mean(elos_105_to_200)) 
    total_players = best_104_players + [TennisPlayer("Qualified " + str(i+1), 105, np.mean(elos_105_to_300)) for i in range(24)]
    return total_players


### ------ Errors ------ ###
class SamePlayersError(Exception):
    def __init__(self):
        super().__init__()
        self.msg = "Un joueur ne peut pas être choisi deux fois, tous les joueurs choisis doivent être différents."