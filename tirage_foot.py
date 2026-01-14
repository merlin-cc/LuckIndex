import random as rd
from collections import defaultdict
from scipy.stats import norm
from scipy.stats import gaussian_kde
from scipy.integrate import quad
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from Team import *
from draw_2026_WC import *


###---------Objectif du code---------###
### Faire tourner de nombreuses simulations de sorte a créer le luck index ###



def get_teams_name(data : pd.DataFrame) -> list[str]:
    """
    Returns a list with the names of all the players
    """
    teams_list_ = teams_list(data)
    list_name = []
    for team in teams_list_:
        list_name.append(team.name)
    return list_name


def draw_to_teams(draw, list_teams):
    teams_index = total_teams_index(list_teams) 
    res = {}
    for pot in draw:
        res[pot] = [teams_index[name] for name in draw[pot]]

    return res


def run_simulation_foot(list_teams : list[FootTeam], num_simulations=10000) -> dict[str, (float, float)]:
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
        distributions[team] = gaussian_kde(opponent_strength_dist[team]) #kde
    
    print("Simulation complete.")
    return distributions


# Calcul du luck index

def luck_index_foot(list_teams : list[FootTeam], distributions : dict[str, (float, float)], draw) -> dict[str, (float,float)]:
    luck_index = {}
    real_draw = draw_to_teams(draw,  list_teams)

    for pool in real_draw:
            for team in real_draw[pool]:
                elo = 0
                for opponent in real_draw[pool]:
                    if opponent != team:
                        elo += opponent.elo
                average_opponent_elo = elo/(len(real_draw[pool])-1)
                
                luck_index[team.name] = (average_opponent_elo, 1-distributions[team.name].integrate_box_1d(0, average_opponent_elo))

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


def display_luck_index_foot(distributions: dict[str, (float, float)], luckIndex: dict[str, float], team: str, x : list[float]) -> None:
    dist = distributions[team]

    y = dist(x)
    plt.plot(x, y, color='royalblue', linewidth=2.5)

    plt.axvline(x=np.mean(dist.dataset), color='blue', linestyle=':', linewidth=2.5, alpha=0.8)
    plt.axvline(x=luckIndex[team][0], color='black', linewidth=2.5)

    plt.xlabel(f"{team}\nLuck index = {100*luckIndex[team][1]:.1f}", fontsize=12, fontweight='bold', labelpad=10)

    plt.title("")
    plt.xticks([])
    plt.yticks([])
    plt.ylim(0, y.max() * 1.1)
    plt.xlim(x[0], x[-1])

def display_random_foot(distributions : dict[str, (float, float)], luckIndex : dict[str, float], N : int, num_simulations : int) -> None:
    teams = list(distributions.keys())
    rd.shuffle(teams)
    displayed_teams = teams[:N*N]
    dists = [distributions[team] for team in displayed_teams]
    xmin = min([np.min(dist.dataset) for dist in dists]) - 200
    xmax = max([np.max(dist.dataset) for dist in dists]) + 200
    x = np.linspace(xmin, xmax, 10000)
    fig, axes = plt.subplots(N, N, figsize=(15, 7))
    fig.suptitle(f'{N*N} tirages aléatoires d\'équipes (avec {num_simulations} simulations)', fontsize=16)
    plt.subplots_adjust(hspace=0.6, wspace=0.3)
    
    for i, ax in enumerate(axes.flat):
        if i < len(displayed_teams):
            team = displayed_teams[i]
            plt.axes(ax)
            ax.set_xticks([])
            ax.set_yticks([])
            display_luck_index_foot(distributions, luckIndex, team, x)

import math

def display_pot_luck(distributions, luckIndex, pot, pot_idx):
    """
    Affiche une grille de graphiques représentant le Luck Index 
    pour toutes les équipes d'un pot spécifique.
    """
    num_teams = len(pot[pot_idx])
    # Calcul automatique de la grille (ex: 12 équipes -> 3 lignes, 4 colonnes)
    cols = 4
    rows = math.ceil(num_teams / cols)
    
    fig, axes = plt.subplots(rows, cols, figsize=(18, rows * 3.5))
    fig.suptitle(f'Analyse du Luck Index du pot - {pot_idx}', fontsize=20, fontweight='bold', y=0.95)
    
    plt.subplots_adjust(hspace=0.6, wspace=0.3)
    
    # On aplatit les axes pour itérer facilement dessus
    axes_flat = axes.flatten()
    
    for i, team_obj in enumerate(pot):
        ax = axes_flat[i]
        plt.axes(ax) # Définit l'axe courant pour display_luck_index_foot
        
        team_name = team_obj.name
        if team_name in distributions:
            display_luck_index_foot(distributions, luckIndex, team_name)
        else:
            ax.set_title(f"{team_name} (No data)")
            ax.axis('off')

    # Cacher les axes vides si le pot n'est pas un multiple de 4
    for j in range(i + 1, len(axes_flat)):
        axes_flat[j].axis('off')

def display_draw(draw):
    fig, axes = plt.subplots(3, 4, figsize=(18, 10))
    bg_color = '#0e1a5a'
    fig.patch.set_facecolor(bg_color)
    axes = axes.flatten()

    box_color = "white"
    team_text_color = "#0e1a5a"
    header_color = "#49afff"

    for i, (poule_name, teams) in enumerate(draw.items()):
        ax = axes[i]
        ax.set_facecolor(bg_color)
        

        ax.text(0.5, 0.95, poule_name.upper(), color=header_color, 
                fontsize=12, fontweight='black', ha='center', transform=ax.transAxes)

        y_starts = [0.75, 0.53, 0.31, 0.09]
        
        for y, team in zip(y_starts, teams):
            rect = patches.FancyBboxPatch(
                (0.05, y), 0.9, 0.16, 
                boxstyle="round,pad=0.01", 
                edgecolor="none", facecolor=box_color,
                transform=ax.transAxes
            )
            ax.add_patch(rect)
            
            ax.text(0.5, y + 0.08, team.upper(), 
                    color=team_text_color, fontweight='bold', 
                    fontsize=10, ha='center', va='center', 
                    transform=ax.transAxes)

        ax.axis('off')

    plt.subplots_adjust(left=0.05, right=0.95, top=0.92, bottom=0.05, wspace=0.3, hspace=0.4)
    plt.suptitle("OFFICIAL DRAW - WORLD CUP", color='white', fontsize=22, fontweight='bold', y=0.98)