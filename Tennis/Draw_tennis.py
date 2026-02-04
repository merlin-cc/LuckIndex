import random as rd
from collections import defaultdict
import matplotlib.ticker as ticker
from scipy.stats import norm
from scipy.integrate import quad
from Tennis.Player import *
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde

### ---------------------------------------------------------------------------------------- Code Objective --------------------------------------------------------------------------------------- ###
###                               Creating a valid draw respecting the Roland Garros tournament rules and computing and ploting the luck index for tennis player                                    ###
#######################################################################################################################################################################################################


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


def win_probability(elo1: int , elo2: int ) -> float:
    """
    Calcule la probabilité que le joueur 1 gagne contre le joueur 2
    en se basant sur la formule ELO.
    """
    return 1 / (1 + 10**((elo2 - elo1) / 400)) #calcul proposé par le systeme elo


def get_opponents_from_draw(draw: dict[TennisPlayer, list[TennisPlayer]]) -> dict[TennisPlayer, list[TennisPlayer]]:
    """From a bracket (ordered list of 128 players), create a map of player -> opponent."""
    opponents_map = {}
    for seed in draw:
        p1 = seed
        p2 = draw[seed][0]
        p3 = draw[seed][1]
        p4 = draw[seed][2]
        #each player is paired with its direct opponent
        opponents_map[p1] = [p2]
        opponents_map[p2] = [p1]
        opponents_map[p3] = [p4]
        opponents_map[p4] = [p3]

        #computing the elo of the potential opponent of the second match
        opp_1_elo = p1.elo*win_probability(p1.elo, p2.elo) + p2.elo*win_probability(p2.elo, p1.elo)
        opp_bracket_1 = TennisPlayer(p1.name + p2.name, 
                                     max(p1.rank, p2.rank), opp_1_elo)
        opp_2_elo = p3.elo*win_probability(p3.elo, p4.elo) + p4.elo*win_probability(p4.elo, p3.elo)
        opp_bracket_2 = TennisPlayer(p3.name + p4.name, 
                                     max(p3.rank, p4.rank), opp_2_elo)
        #adding virtual player with the expected elo
        opponents_map[p1].append(opp_bracket_2)
        opponents_map[p2].append(opp_bracket_2)
        opponents_map[p3].append(opp_bracket_1)
        opponents_map[p4].append(opp_bracket_1)

    return opponents_map


def run_simulation(list_players: list[TennisPlayer], num_simulations=10000) -> dict[TennisPlayer, (float, float)]:
    print(f"Running {num_simulations} simulations...")
    opponent_strength_dist = defaultdict(list)

    for i in range(num_simulations):
        if i % 100 == 0 and i > 0:
            print(f"Completed {i} simulations...")
        
        draw = createDraws(list_players.copy())
        
        opponents_map = get_opponents_from_draw(draw)

        for player in opponents_map:
            strength = 0
            for opponent in opponents_map[player]:
                strength += opponent.elo
            opponent_strength_dist[player].append(strength/2)  #average strength

    distributions = {}
    for player in opponent_strength_dist:
        distributions[player] =  gaussian_kde(opponent_strength_dist[player])
    
    print("Simulation complete.")
    return distributions


### ----------------------------------------------------- This part contains useful functions to compute and plot the luck index of each player ----------------------------------------------------- ###
###                                                                                                                                                                                                 ###
#######################################################################################################################################################################################################


def luck_index(list_players: list[TennisPlayer], distributions: dict[TennisPlayer, gaussian_kde], draw: dict[TennisPlayer, list[TennisPlayer]]) -> dict[TennisPlayer, (float, float)]:
    """
    Calculates the Luck Index for each player by comparing their actual draw difficulty 
    (average opponent Elo) against their expected difficulty distribution derived from simulations.
    """
    luck_index = {}
    opponents_map = get_opponents_from_draw(draw)
    for player in list_players:
        avg_opponent_elo = 0
        for opponent in opponents_map[player]:
            avg_opponent_elo += opponent.elo/2

            luck_index[player] = luck_index[player] = (avg_opponent_elo, 1-distributions[player].integrate_box_1d(0, avg_opponent_elo))
    
    return luck_index


def display_luck_index(distributions: dict[TennisPlayer, gaussian_kde], luckIndex: dict[TennisPlayer, (float, float)], player: TennisPlayer, x: np.ndarray) -> None:
    """
    Plots the probability density function (KDE) of draw difficulty for a specific player,
    marking the theoretical mean and the actual difficulty encountered.
    """
    dist = distributions[player]
    y = dist(x)

    color_curve = 'forestgreen'
    color_mean = 'green'

    plt.plot(x, y, color=color_curve, linewidth=2.5)

    plt.axvline(x=np.mean(dist.dataset), color=color_mean, linestyle=':', linewidth=2.5, alpha=0.8)
    plt.axvline(x=luckIndex[player][0], color='black', linewidth=2.5)

    plt.xlabel(f"{player.name}\nLuck index = {100*luckIndex[player][1]:.1f}", fontsize=11, fontweight='bold', labelpad=15)

    plt.title("")
    plt.yticks([])
    plt.ylim(0, y.max() * 1.1)
    plt.xlim(x[0], x[-1])

    ax = plt.gca()
    
    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=4))
    ax.tick_params(axis='x', labelsize=8, color='#888', labelcolor='#666')

    ax.text(0.02, 0.03, "← Easier", transform=ax.transAxes, color='green', fontsize=8, fontweight='bold', ha='left')
    ax.text(0.98, 0.03, "Harder →", transform=ax.transAxes, color='red', fontsize=8, fontweight='bold', ha='right')


def display_random(distributions: dict[TennisPlayer, (float, float)], luckIndex: dict[TennisPlayer, float], list_players: list[TennisPlayer], N: int, num_simulations: int) -> None:
    """
    Generates a grid of Luck Index plots for the top N seeded players to visualize 
    the outcomes of a random draw simulation.
    """
    players = list_players
    displayed_players = players[:N]
    dists = [distributions[team] for team in displayed_players]
    xmin = min([np.min(dist.dataset) for dist in dists]) - 100
    xmax = max([np.max(dist.dataset) for dist in dists]) + 100
    x = np.linspace(xmin, xmax, 1000)
    fig, axes = plt.subplots(int(N/4), int(N/8), figsize=(20, 24))
    fig.suptitle(f'Luck index des {N} têtes de série (avec {num_simulations} simulations pour un tirage aléatoire)', fontsize=16)
    plt.subplots_adjust(hspace=0.6, wspace=0.3)
    
    for i, ax in enumerate(axes.flat):
        if i < len(players) and i < N*N:
            player = players[i]
            plt.axes(ax)
            ax.set_xticks([])
            ax.set_yticks([])
            display_luck_index(distributions, luckIndex, player, x)


def manual_tirage(players: list[TennisPlayer], distributions: dict[TennisPlayer, (float, float)], num_simulations: int) -> None:
    """
    Simulates and visualizes the Luck Index for a specific scenario where 4 players 
    are manually selected by the user.
    """
    draw = {players[0] : [players[1], players[2], players[3]]}
    luckIndex = luck_index(players, distributions, draw)
    dists = [distributions[team] for team in players]
    xmin = min([np.min(dist.dataset) for dist in dists]) - 100
    xmax = max([np.max(dist.dataset) for dist in dists]) + 100
    x = np.linspace(xmin, xmax, 10000)
    fig, axes = plt.subplots(2, 2, figsize=(15, 7))
    fig.suptitle(f'tirages de joueurs (avec {num_simulations} simulations)', fontsize=16)
    plt.subplots_adjust(hspace=0.6, wspace=0.3)
    for i, ax in enumerate(axes.flat):
        player = players[i]
        plt.axes(ax)
        ax.set_xticks([])
        ax.set_yticks([])
        display_luck_index(distributions, luckIndex, player, x)


def bar_luck_index_tennis(luckIndex: dict[TennisPlayer, tuple[float, float]]) -> None:
    """
    Creates and displays a ranked horizontal bar chart comparing the Luck Index of all players, 
    sorted from the luckiest (highest index) to the unluckiest.
    """
    data = {}
    for player in luckIndex:
        data[player.name] = 100*luckIndex[player][1]
    
    sorted_data = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))
    players = list(sorted_data.keys())
    lucks = list(sorted_data.values())

    fig, ax = plt.subplots(figsize=(10, len(players) * 0.25 + 1))
    
    ax.barh(range(len(players)), lucks, color='black', height=0.7)
    
    ax.set_yticks([])
    ax.set_xticks([])
    ax.invert_yaxis()
    
    max_val = max(lucks)
    ax.set_xlim(0, max_val * 2.0) 

    for spine in ax.spines.values():
        spine.set_visible(False)

    col_team_x = -max_val * 0.8    
    col_index_x = -max_val * 0.1   
    
    for i, (player, luck) in enumerate(zip(players, lucks)):
        ax.text(col_team_x, i, player, va='center', ha='left', fontsize=9)
        ax.text(col_index_x, i, f"{luck:.1f}", va='center', ha='right', fontfamily='monospace', fontsize=9)

    header_y = -1.5
    ax.text(col_team_x, header_y, 'Player', weight='bold', fontsize=10, ha='left')
    ax.text(col_index_x, header_y, 'Luck index', weight='bold', fontsize=10, ha='right')
    
    ax.plot([0, max_val], [header_y + 0.5, header_y + 0.5], color='black', linewidth=1, clip_on=False)
    plt.tight_layout()