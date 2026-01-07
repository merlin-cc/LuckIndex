import random as rd
from collections import defaultdict
from scipy.stats import norm
from scipy.integrate import quad
from Player import TennisPlayer
import matplotlib.pyplot as plt
import numpy as np

"""
Here we create random draws that are allowed by Roland Garros rules
A quick remind of how it works : 
The main tournament has 128 players.

The top 32 ranked players are called "seeds".

The goal of the draw is to keep the seeds apart so they don't play each other in the first rounds.

How the Draw Works

Seed #1 is placed at the very top of the bracket.

Seed #2 is placed at the very bottom of the bracket.

This means they can only play each other in the Final.

Seeds #3 and #4 are randomly drawn to be placed in the other two halves.

This means they can only play Seed #1 or #2 in the Semi-Finals.

Seeds #5 to #8 are randomly drawn to be placed in the different quarters.

This means they are set to play Seeds #1-4 in the Quarter-Finals.

Seeds #9 to #32 are then randomly placed in the remaining protected spots.

All other players (the 96 unseeded players, qualifiers, and wild cards) are drawn completely randomly to fill the empty slots.
"""

#Create the draws

def createDraws(list_players: list[TennisPlayer]) -> dict[TennisPlayer, list[TennisPlayer]]:
    """
    create 32 groups of 4 players with one top32 player in each groups
    """
    draw = {}
    try :
        len(list_players) == 128
    except ValueError:
        print("Not enough player to create 32 pull")
    best_players = list_players[:32]
    other_players = list_players[32:]
    rd.shuffle(other_players)
    
    for i in range(32):
        seed = best_players[i]
        player_2 = other_players.pop()
        player_3 = other_players.pop()
        player_4 = other_players.pop()
        
        draw[seed] = [player_2, player_3, player_4]

    return draw


# Construction of the density of probability using the LLN

def win_probability(elo1 : int , elo2: int ) -> float:
    """
    Calcule la probabilité que le joueur 1 gagne contre le joueur 2
    en se basant sur la formule ELO.
    """
    return 1 / (1 + 10**((elo2 - elo1) / 400)) #calcul proposé par le systeme elo


def get_opponents_from_draw(draw : dict[TennisPlayer, list[TennisPlayer]]) -> dict[TennisPlayer, list[TennisPlayer]]:
    """From a bracket (ordered list of 128 players), create a map of player -> opponent."""
    opponents_map = {}
    for seed in draw:
        p1 = seed
        p2 = draw[seed][0]
        p3 = draw[seed][1]
        p4 = draw[seed][2]
        #chaque joueur affronte son adversaire direct 
        opponents_map[p1] = [p2]
        opponents_map[p2] = [p1]
        opponents_map[p3] = [p4]
        opponents_map[p4] = [p3]

        #calcul des adversaires potentiels au 2e round
        opp_1_elo = p1.elo*win_probability(p1.elo, p2.elo) + p2.elo*win_probability(p2.elo, p1.elo)
        opp_bracket_1 = TennisPlayer(p1.name + p2.name, p1.country + p2.country, 
                                     max(p1.rank, p2.rank), opp_1_elo)
        opp_2_elo = p3.elo*win_probability(p3.elo, p4.elo) + p4.elo*win_probability(p4.elo, p3.elo)
        opp_bracket_2 = TennisPlayer(p3.name + p4.name, p3.country + p4.country, 
                                     max(p3.rank, p4.rank), opp_2_elo)
        #ajout des joueurs potentiels au 2e round
        opponents_map[p1].append(opp_bracket_2)
        opponents_map[p2].append(opp_bracket_2)
        opponents_map[p3].append(opp_bracket_1)
        opponents_map[p4].append(opp_bracket_1)

    return opponents_map

# Calcul de la loi de probabilité en utilisant le TLC
def run_simulation(list_players : list[TennisPlayer], num_simulations=10000) -> dict[TennisPlayer, (float, float)]:
    print(f"Running {num_simulations} simulations...")
    opponent_strength_dist = defaultdict(list)

    for i in range(num_simulations):
        if i % 100 == 0 and i > 0:
            print(f"Completed {i} simulations...")
        
        draw = createDraws(list_players.copy())
        
        opponents_map = get_opponents_from_draw(draw)

        for player in opponents_map:
            for opponent in opponents_map[player]:
                opponent_strength_dist[player].append(opponent.elo)

    distributions = {}
    for player in opponent_strength_dist:
        distributions[player] = norm.fit(opponent_strength_dist[player]) #mu and sigma of normal distibution
    
    print("Simulation complete.")
    return distributions


# Calcul du luck index

def luck_index(list_players : list[TennisPlayer], distributions : dict[TennisPlayer, (float, float)], draw : dict[TennisPlayer, list[TennisPlayer]]) -> dict[TennisPlayer, float]:
    luck_index = {}
    opponents_map = get_opponents_from_draw(draw)
    for player in list_players:
        average_opponent_elo = 0
        for opponent in opponents_map[player]:
            average_opponent_elo += opponent.elo/2

        mu, sigma = distributions[player]

        luck_index[player] = 1-quad(lambda s: norm.pdf(s, mu, sigma), 0, average_opponent_elo)[0]

    # trie des joueurs
    sorted_by_luck = sorted(luck_index.items(), key=lambda item: item[1])
    print("\n--- Top 5 des joueurs les plus 'malchanceux' (adversaire le plus fort) ---")
    for player, luck in sorted_by_luck[:5]:
        print(f"{player.name}: {luck:.2f} luck index")

    print("\n--- Top 5 des joueurs les plus 'chanceux' (adversaire le plus faible) ---")
    for player, luck in sorted_by_luck[-5:]:
        print(f"{player.name}: {luck:.2f} luck index")
    
    return luck_index


def display_luck_index(distributions: dict[TennisPlayer, (float, float)], luckIndex: dict[TennisPlayer, float], player: TennisPlayer) -> None:
    mu, sigma = distributions[player]

    x_min = mu - 5 * sigma
    x_max = mu + 5 * sigma

    val_calculee = norm.ppf(1 - luckIndex[player], loc=mu, scale=sigma)
    X = np.linspace(x_min, x_max, 1000)
    Y = norm.pdf(X, mu, sigma)

    plt.plot(X, Y, color='royalblue', linewidth=2.5)

    plt.axvline(x=mu, color='blue', linestyle=':', linewidth=2.5, alpha=0.8)
    plt.axvline(x=val_calculee, color='black', linewidth=2.5)

    plt.xlabel(f"{player.name}\nLuck index = {100*luckIndex[player]:.1f}", fontsize=12, fontweight='bold', labelpad=10)

    plt.title("")
    plt.xticks([])
    plt.yticks([])
    plt.ylim(0, Y.max() * 1.1)
    plt.xlim(x_min, x_max)

def display_random(distributions : dict[TennisPlayer, (float, float)], luckIndex : dict[TennisPlayer, float], list_players : list[TennisPlayer], N : int, num_simulations : int) -> None:
    players = list_players
    rd.shuffle(players)
    fig, axes = plt.subplots(N, N, figsize=(15, 7))
    fig.suptitle(f'{N*N} tirages aléatoires de joueurs (avec {num_simulations} simulations)', fontsize=16)
    plt.subplots_adjust(hspace=0.6, wspace=0.3)
    
    for i, ax in enumerate(axes.flat):
        if i < len(players) and i < N*N:
            player = players[i]
            plt.axes(ax)
            ax.set_xticks([])
            ax.set_yticks([])
            display_luck_index(distributions, luckIndex, player)

def manual_tirage(players : list[TennisPlayer], distributions : dict[TennisPlayer, (float, float)], num_simulations : int) -> None:
    draw = {players[0] : [players[1], players[2], players[3]]}
    luckIndex = luck_index(players, distributions, draw)
    fig, axes = plt.subplots(2, 2, figsize=(15, 7))
    fig.suptitle(f'tirages de joueurs (avec {num_simulations} simulations)', fontsize=16)
    plt.subplots_adjust(hspace=0.6, wspace=0.3)
    for i, ax in enumerate(axes.flat):
        player = players[i]
        plt.axes(ax)
        ax.set_xticks([])
        ax.set_yticks([])
        display_luck_index(distributions, luckIndex, player)