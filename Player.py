import pandas as pd

class TennisPlayer():
    def __init__(self, name : str, country : str, rank : int , elo : int ):
        self.name = name
        self.country = country
        self.rank = rank
        self.elo = elo
    
data = pd.read_csv('tennisATPRanking.csv')


def list_players(data, max_rank):
    res = []
    for rank in range(1, max_rank + 1):
        res.append(TennisPlayer(data.loc[rank-1]['Name'], data.loc[rank-1]['Country'], data.loc[rank-1]['Rank'], data.loc[rank-1]['Points']))

    return res

L = list_players(data, 104)

#vérif
show = [p.name for p in L]
print(show)