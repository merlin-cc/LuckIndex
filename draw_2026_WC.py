import random
import time
from dataclasses import dataclass
from typing import List, Dict
import pulp

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
    Team("UEFA 1", ["UEFA"]),
    Team("UEFA 2", ["UEFA"]),
    Team("UEFA 3", ["UEFA"]),
    Team("UEFA 4", ["UEFA"]),
    Team("FIFA 1", ["OFC", "CONCACAF", "CAF"]),
    Team("FIFA 2", ["CONMEBOL", "AFC", "CONCACAF"])
]

pots = [pot1, pot2, pot3, pot4]
all_teams = [team for pot in pots for team in pot]

spain_idx = 3
argentina_idx = 4
france_idx = 5
england_idx = 6

def feasibility_check(assigned, pots, spain_idx, argentina_idx, france_idx, england_idx):
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

def draw(pots, logger, nb_draws):
    results = [None] * nb_draws
    initial_time = time.time()

    for N in range(nb_draws):
        assigned = [[0] * n for _ in range(nb_groups)]
        shuffled_indices = [None] * len(pots)

        for p_idx in range(len(pots)):
            if p_idx == 0:
                fixed = list(range(3))
                to_shuffle = list(range(3, len(pots[p_idx])))
                random.shuffle(to_shuffle)
                shuffled_indices[p_idx] = fixed + to_shuffle
            else:
                indices = list(range(len(pots[p_idx])))
                random.shuffle(indices)
                shuffled_indices[p_idx] = indices

        pot_ranges = []
        idx = 0
        for p_idx in range(len(pots)):
            pot_ranges.append(list(range(idx, idx + len(pots[p_idx]))))
            idx += len(pots[p_idx])

        logger.write("==============================\n")
        logger.write("=== POT 1 (special rules) ===\n")
        logger.write("==============================\n\n")

        logger.write("\nMexico (CONCACAF)\nGroup A\n")
        assigned[0][0] = 1
        logger.write("\nCanada (CONCACAF)\nGroup B\n")
        assigned[1][1] = 1
        logger.write("\nUnited States (CONCACAF)\nGroup D\n")
        assigned[3][2] = 1

        for k in shuffled_indices[0][3:]:
            i = pot_ranges[0][k]
            team = all_teams[i]
            logger.write(f"\n{team.name} ({','.join(team.confs)})\n")
            for g in range(nb_groups):
                if sum(assigned[g][j] for j in pot_ranges[0]) < 1:
                    logger.write(f"Group {chr(65 + g)}\n")
                    assigned[g][i] = 1
                    if feasibility_check(assigned, pots, spain_idx, argentina_idx, france_idx, england_idx):
                        logger.write(" Yes\n")
                        break
                    else:
                        logger.write(" No\n")
                        assigned[g][i] = 0

        for p_idx in range(1, len(pots)):
            logger.write("\n==============================\n")
            logger.write(f"=== POT {p_idx + 1} ===\n")
            logger.write("==============================\n\n")
            for k in shuffled_indices[p_idx]:
                i = pot_ranges[p_idx][k]
                team = all_teams[i]
                logger.write(f"\n{team.name} ({','.join(team.confs)})\n")
                for g in range(nb_groups):
                    if sum(assigned[g][j] for j in pot_ranges[p_idx]) < 1:
                        logger.write(f"Group {chr(65 + g)}\n")
                        assigned[g][i] = 1
                        if feasibility_check(assigned, pots, spain_idx, argentina_idx, france_idx, england_idx):
                            logger.write(" Yes\n")
                            break
                        else:
                            logger.write(" No\n")
                            assigned[g][i] = 0

        pairs = []
        for g in range(nb_groups):
            team_indices = [idx for idx in range(n) if assigned[g][idx] == 1]
            for i_idx in range(len(team_indices)):
                for j_idx in range(i_idx + 1, len(team_indices)):
                    pairs.append(f"({team_indices[i_idx]+1}, {team_indices[j_idx]+1})")
        results[N] = " ".join(pairs)

        with open("draw_example.txt", "w") as groupfile:
            for g in range(nb_groups):
                groupfile.write("====================\n")
                groupfile.write(f"Group {chr(65 + g)}\n")
                groupfile.write("====================\n")
                for i_team in range(n):
                    if assigned[g][i_team] == 1:
                        team = all_teams[i_team]
                        groupfile.write(f"{team.name} ({','.join(team.confs)})\n")
                groupfile.write("\n")

    with open("draw_results.txt", "a") as f:
        for r in results:
            f.write(r + "\n")

    final_time = time.time() - initial_time
    print(f"Execution time for {nb_draws} draws: {round(final_time, 1)}s")
    return 0

if __name__ == "__main__":
    nb_draws = 2
    with open("draw_log.txt", "w") as logger:
        draw(pots, logger, nb_draws)