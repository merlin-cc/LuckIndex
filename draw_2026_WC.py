import random
import pulp
from dataclasses import dataclass
from typing import List, Dict
import pandas as pd


###----------Objectif du code----------###
### Renvoie un dictionnaire {Pool X: [TEAM1, TEAM2, TEAM3, TEAM4]} ###

@dataclass
class Team:
    name: str
    confs: List[str]

n = 48
nb_groups = 12



pot1 = [
    Team("Mexico", ["CONCACAF"]),
    Team("Canada", ["CONCACAF"]),
    Team("United States", ["CONCACAF"]),
    Team("Spain", ["UEFA"]),
    Team("Argentina", ["CONMEBOL"]),
    Team("France", ["UEFA"]),
    Team("England", ["UEFA"]),
    Team("Brazil", ["CONMEBOL"]),
    Team("Portugal", ["UEFA"]),
    Team("Netherlands", ["UEFA"]),
    Team("Belgium", ["UEFA"]),
    Team("Germany", ["UEFA"])
]

pot2 = [
    Team("Croatia", ["UEFA"]),
    Team("Morocco", ["CAF"]),
    Team("Colombia", ["CONMEBOL"]),
    Team("Uruguay", ["CONMEBOL"]),
    Team("Switzerland", ["UEFA"]),
    Team("Japan", ["AFC"]),
    Team("Senegal", ["CAF"]),
    Team("Iran", ["AFC"]),
    Team("South Korea", ["AFC"]),
    Team("Ecuador", ["CONMEBOL"]),
    Team("Austria", ["UEFA"]),
    Team("Australia", ["AFC"])
]

pot3 = [
    Team("Norway", ["UEFA"]),
    Team("Panama", ["CONCACAF"]),
    Team("Egypt", ["CAF"]),
    Team("Algeria", ["CAF"]),
    Team("Scotland", ["UEFA"]),
    Team("Paraguay", ["CONMEBOL"]),
    Team("Tunisia", ["CAF"]),
    Team("Ivory Coast", ["CAF"]),
    Team("Uzbekistan", ["AFC"]),
    Team("Qatar", ["AFC"]),
    Team("Saudi Arabia", ["AFC"]),
    Team("South Africa", ["CAF"])
]

pot4 = [
    Team("Jordan", ["AFC"]),
    Team("Cape Verde", ["CAF"]),
    Team("Ghana", ["CAF"]),
    Team("Curaçao", ["CONCACAF"]),
    Team("Haiti", ["CONCACAF"]),
    Team("New Zealand", ["OFC"]),

    Team("Italy", ["UEFA"]),
    Team("Sweden", ["UEFA"]), 
    Team("Turkey", ["UEFA"]), 
    Team("Denmark", ["UEFA"]), 
    Team("DR Congo", ["CAF"]), 
    Team("Iraq", ["AFC"])

    #Team("UEFA 1", ["UEFA"]),
    #Team("UEFA 2", ["UEFA"]),
    #Team("UEFA 3", ["UEFA"]),
    #Team("UEFA 4", ["UEFA"]),
    #Team("FIFA 1", ["OFC", "CONCACAF", "CAF"]),
    #Team("FIFA 2", ["CONMEBOL", "AFC", "CONCACAF"])
]



##### ----- OFFICIAL DRAW ----- #####
#traiter les UEFA (pas indiqués comme il faut sur le dict + calculer les histoires de adversaire possible.)
official_draw = {
    'Poule A': ['Mexico', 'South Africa', 'South Korea', 'Winner Play-off D (CZE/DEN/IRL/MKD)'],
    'Poule B': ['Canada', 'Winner Play-off A (BIH/ITA/NIR/WAL)', 'Qatar', 'Switzerland'],
    'Poule C': ['Brazil', 'Morocco', 'Haiti', 'Scotland'],
    'Poule D': ['USA', 'Paraguay', 'Australia', 'Winner Play-off C (KOS/ROU/SVK/TUR)'],
    'Poule E': ['Germany', 'Curaçao', 'Ivory Coast', 'Ecuador'],
    'Poule F': ['Netherlands', 'Japan', 'Winner Play-off B (ALB/POL/SWE/UKR)', 'Tunisia'],
    'Poule G': ['Belgium', 'Egypt', 'IR Iran', 'New Zealand'],
    'Poule H': ['Spain', 'Cape Verde', 'Saudi Arabia', 'Uruguay'],
    'Poule I': ['France', 'Senegal', 'Winner Play-off 2 (BOL/IRQ/SUR)', 'Norway'],
    'Poule J': ['Argentina', 'Algeria', 'Austria', 'Jordan'],
    'Poule K': ['Portugal', 'Winner Play-off 1 (COD/JAM/NCL)', 'Uzbekistan', 'Colombia'],
    'Poule L': ['England', 'Croatia', 'Ghana', 'Panama']}
#---------------------
pots = [pot1, pot2, pot3, pot4]
all_teams = [team for pot in pots for team in pot]

spain_idx = 3
argentina_idx = 4
france_idx = 5
england_idx = 6

def feasibility_check(assigned, pots, spain_idx, argentina_idx, france_idx, england_idx):
    """
    Check feasibility of a team-to-group assignment under draw constraints.

    Args:
        assigned: a matrix indicating already fixed assignments
            assigned[g][i] == 1 means team i is already assigned to group g.
        pots: a list of pots, where each pot is a list of teams.
        spain_idx: index of Spain.
        argentina_idx: index of Argentina.
        france_idx: index of France.
        england_idx: index of England.

    Returns:
        Bool: true if a feasible assignment exists given the already assigned teams.
    """
    model = pulp.LpProblem("Draw_Feasibility", pulp.LpMinimize)
    
    x = pulp.LpVariable.dicts("x", (range(nb_groups), range(n)), cat=pulp.LpBinary)

    pot_of = {}
    idx = 0
    for p_idx, pot in enumerate(pots):
        for _ in pot:
            pot_of[idx] = p_idx
            idx += 1

    for g in range(nb_groups):
        for i in range(n):
            if assigned[g][i] == 1:
                model += x[g][i] == 1

    for i in range(n):
        model += pulp.lpSum([x[g][i] for g in range(nb_groups)]) == 1

    for g in range(nb_groups):
        for p_idx in range(len(pots)):
            teams_from_pot = [i for i in range(n) if pot_of[i] == p_idx]
            model += pulp.lpSum([x[g][i] for i in teams_from_pot]) == 1

    confs = ["UEFA", "AFC", "CAF", "CONMEBOL", "CONCACAF", "OFC"]
    for g in range(nb_groups):
        for c in confs:
            relevant = [i for i in range(n) if c in all_teams[i].confs]
            upper_limit = 2 if c == "UEFA" else 1
            lower_limit = 1 if c == "UEFA" else 0
            model += pulp.lpSum([x[g][i] for i in relevant]) <= upper_limit
            model += pulp.lpSum([x[g][i] for i in relevant]) >= lower_limit

    left_groups = [3, 4, 5, 6, 7, 8]
    right_groups = [0, 1, 2, 9, 10, 11]
    
    model += pulp.lpSum([x[g][argentina_idx] + x[g][spain_idx] for g in left_groups]) <= 1
    model += pulp.lpSum([x[g][argentina_idx] + x[g][spain_idx] for g in right_groups]) <= 1
    model += pulp.lpSum([x[g][france_idx] + x[g][england_idx] for g in left_groups]) <= 1
    model += pulp.lpSum([x[g][france_idx] + x[g][england_idx] for g in right_groups]) <= 1

    model.solve(pulp.PULP_CBC_CMD(msg=0))
    return pulp.LpStatus[model.status] == 'Optimal'

def single_draw(pots) -> dict[str, list[str]]:
    assigned = [[0] * n for _ in range(nb_groups)]
    shuffled_indices = []
    for p_idx in range(len(pots)):
        if p_idx == 0:
            fixed = list(range(3))
            to_shuffle = list(range(3, len(pots[p_idx])))
            random.shuffle(to_shuffle)
            shuffled_indices.append(fixed + to_shuffle)
        else:
            indices = list(range(len(pots[p_idx])))
            random.shuffle(indices)
            shuffled_indices.append(indices)
    pot_ranges = []
    idx = 0
    for pot in pots:
        pot_ranges.append(list(range(idx, idx + len(pot))))
        idx += len(pot)
    assigned[0][0], assigned[1][1], assigned[3][2] = 1, 1, 1
    for p_idx, indices in enumerate(shuffled_indices):
        start_idx = 3 if p_idx == 0 else 0
        for k in indices[start_idx:]:
            i = pot_ranges[p_idx][k]
            for g in range(nb_groups):
                if sum(assigned[g][j] for j in pot_ranges[p_idx]) < 1:
                    assigned[g][i] = 1
                    if feasibility_check(assigned, pots, spain_idx, argentina_idx, france_idx, england_idx):
                        break
                    else:
                        assigned[g][i] = 0
    result_dict = {}
    for g in range(nb_groups):
        group_name = f"Poule {chr(65 + g)}"
        result_dict[group_name] = [all_teams[i].name for i in range(n) if assigned[g][i] == 1]
    return result_dict


# ------------------------------------------------------------
# Execution
# ------------------------------------------------------------

if __name__ == "__main__":
    pousles_dict = single_draw(pots)
    print(pousles_dict)


