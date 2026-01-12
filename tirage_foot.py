import random as rd
from collections import defaultdict
from scipy.stats import norm
from scipy.integrate import quad
from Player import TennisPlayer
import matplotlib.pyplot as plt
import numpy as np
from Team import *
from draw_2026_WC import *


###---------Objectif du code---------###
### Faire tourner de nombreuses simulations de sorte a créer le luck index ###

def draw_to_teams(draw, list_teams):
    teams_index = total_teams_index(list_teams) 
    res = {}
    for pot in draw:
        res[pot] = [teams_index[name] for name in draw[pot]]

    return res


def run_simulation(list_teams : list[FootTeam], num_simulations=10000) -> dict[str, (float, float)]:
    print(f"Running {num_simulations} simulations...")
    opponent_strength_dist = defaultdict(list)

    for i in range(num_simulations):
        if i % 100 == 0 and i > 0:
            print(f"Completed {i} simulations...")
        
        draw = draw_to_teams(single_draw(pots),  list_teams)

        for pool in draw:
            for team in draw[pool]:
                strenght = 0
                for opponent in draw[pool]:
                    if opponent != team:
                        strenght += opponent.elo
                opponent_strength_dist[team.name].append(strenght/(len(draw[pool])-1))

    distributions = {}
    for team in opponent_strength_dist:
        distributions[team] = norm.fit(opponent_strength_dist[team]) #mu and sigma of normal distibution
    
    print("Simulation complete.")
    return distributions


# Calcul du luck index

def luck_index_foot(list_teams : list[FootTeam], distributions : dict[str, (float, float)], draw) -> dict[str, float]:
    luck_index = {}
    real_draw = draw_to_teams(draw,  list_teams)

    for pool in real_draw:
            for team in real_draw[pool]:
                elo = 0
                for opponent in real_draw[pool]:
                    if opponent != team:
                        elo += opponent.elo
                average_opponent_elo = elo/(len(real_draw[pool])-1)

                mu, sigma = distributions[team.name]
                luck_index[team.name] = 1-quad(lambda s: norm.pdf(s, mu, sigma), 0, average_opponent_elo)[0]

    # trie des joueurs
    """
    sorted_by_luck = sorted(luck_index.items(), key=lambda item: item[1])
    print("\n--- Top 5 des teams les plus 'malchanceux' (adversaire le plus fort) ---")
    for team, luck in sorted_by_luck[:5]:
        print(f"{team.name}: {luck:.2f} luck index")

    print("\n--- Top 5 des teams les plus 'chanceux' (adversaire le plus faible) ---")
    for team, luck in sorted_by_luck[-5:]:
        print(f"{team.name}: {luck:.2f} luck index")
        """
    
    return luck_index


def display_luck_index_foot(distributions: dict[str, (float, float)], luckIndex: dict[str, float], team: str) -> None:
    mu, sigma = distributions[team]

    x_min = mu - 5 * sigma
    x_max = mu + 5 * sigma

    val_calculee = norm.ppf(1 - luckIndex[team], loc=mu, scale=sigma)
    X = np.linspace(x_min, x_max, 1000)
    Y = norm.pdf(X, mu, sigma)

    plt.plot(X, Y, color='royalblue', linewidth=2.5)

    plt.axvline(x=mu, color='blue', linestyle=':', linewidth=2.5, alpha=0.8)
    plt.axvline(x=val_calculee, color='black', linewidth=2.5)

    plt.xlabel(f"{team}\nLuck index = {100*luckIndex[team]:.1f}", fontsize=12, fontweight='bold', labelpad=10)

    plt.title("")
    plt.xticks([])
    plt.yticks([])
    plt.ylim(0, Y.max() * 1.1)
    plt.xlim(x_min, x_max)

def display_random_foot(distributions : dict[str, (float, float)], luckIndex : dict[str, float], N : int, num_simulations : int) -> None:
    teams = list(distributions.keys())
    rd.shuffle(teams)
    fig, axes = plt.subplots(N, N, figsize=(15, 7))
    fig.suptitle(f'{N*N} tirages aléatoires de joueurs (avec {num_simulations} simulations)', fontsize=16)
    plt.subplots_adjust(hspace=0.6, wspace=0.3)
    
    for i, ax in enumerate(axes.flat):
        if i < len(teams) and i < N*N:
            team = teams[i]
            plt.axes(ax)
            ax.set_xticks([])
            ax.set_yticks([])
            display_luck_index_foot(distributions, luckIndex, team)