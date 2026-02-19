import random as rd
from collections import defaultdict
from scipy.stats import norm
from scipy.stats import gaussian_kde
from scipy.integrate import quad
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from Football.Team import *
from Football.draw_2026_WC import *
import math

### ---------------------------------------------------------------------------------------- Code Objective --------------------------------------------------------------------------------------- ###
###                                                                      Run extensive simulations to compute the Luck Index                                                                        ###
#######################################################################################################################################################################################################


def get_teams_name(data: pd.DataFrame) -> list[str]:
    """
    Extracts and returns a list containing the names of all teams from the dataframe.
    """
    teams_list_ = teams_list(data)
    list_name = []
    for team in teams_list_:
        list_name.append(team.name)
    return list_name


def draw_to_teams(draw: dict[str, list[str]], list_teams: list[FootTeam]) -> dict[str, list[FootTeam]]:
    """
    Converts a draw dictionary (containing team names) into a dictionary mapping pots to lists of FootTeam objects.
    """
    teams_index = total_teams_index(list_teams) 
    res = {}
    for pot in draw:
        res[pot] = [teams_index[name] for name in draw[pot]]
    return res


def run_simulation_foot(list_teams: list[FootTeam], num_simulations=10000) -> dict[str, gaussian_kde]:
    """
    Runs a specified number of draw simulations to generate Gaussian KDE distributions 
    of average opponent strength for each team.
    """
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
        distributions[team] = gaussian_kde(opponent_strength_dist[team]) #kde object
    
    print("Simulation complete.")
    return distributions # opponent_strength_dist 


### ----------------------------------------------------- This part contains useful functions to compute and plot the luck index of each team ----------------------------------------------------- ###
###                                                                                                                                                                                                 ###
#######################################################################################################################################################################################################

def luck_index_foot(list_teams: list[FootTeam], distributions: dict[str, gaussian_kde], draw: dict[str, list[str]]) -> dict[str, (float,float)]:
    """
    Calculates the Luck Index for each team by comparing their actual draw difficulty 
    (average opponent Elo) against the simulated probability distributions.
    """
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
    
    return luck_index


def display_luck_index_foot(distributions: dict[str, (float, float)], luckIndex: dict[str, (float,float)], team: str, x: list[float]) -> None:
    """
    Plots the opponent strength distribution for a specific team, highlighting the 
    theoretical mean difficulty and the actual draw difficulty (Luck Index).
    """
    dist = distributions[team]

    y = dist(x)
    plt.plot(x, y, color='royalblue', linewidth=2.5)

    plt.axvline(x=np.mean(dist.dataset), color='blue', linestyle=':', linewidth=2.5, alpha=0.8)
    plt.axvline(x=luckIndex[team][0], color='black', linewidth=2.5)

    plt.xlabel(f"{team}\nLuck index = {100*luckIndex[team][1]:.1f}%", fontsize=12, fontweight='bold', labelpad=10)

    plt.title("")
    plt.xticks([])
    plt.yticks([])
    plt.ylim(0, y.max() * 1.1)
    plt.xlim(x[0], x[-1])

    ax = plt.gca()

    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=4))
    ax.tick_params(axis='x', labelsize=8, color='#888', labelcolor='#666')

    ax.text(0.02, 0.03, "← Easier", transform=ax.transAxes, color='#27ae60', fontsize=8, fontweight='bold', ha='left')
    ax.text(0.98, 0.03, "Harder →", transform=ax.transAxes, color='#c0392b', fontsize=8, fontweight='bold', ha='right')


def display_random_foot(distributions: dict[str, (float, float)], luckIndex: dict[str, (float,float)], N: int, num_simulations: int) -> None:
    """
    Selects N*N random teams and displays their Luck Index plots in a grid layout 
    to provide a quick overview of different outcomes.
    """
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


def display_official_draw_luck(distributions: dict[str, gaussian_kde], luckIndex: dict[str, tuple[float, float]], draw: dict[str, list[str]]) -> None:
    """
    Self explanatory, it displays the luck index for the official 2026 WC draw
    """
    all_teams_in_draw = [team for group in draw.values() for team in group]
    relevant_dists = [distributions[t] for t in all_teams_in_draw if t in distributions]
    
    if not relevant_dists:
        return

    xmin = min([np.min(d.dataset) for d in relevant_dists]) - 100
    xmax = max([np.max(d.dataset) for d in relevant_dists]) + 100
    x = np.linspace(xmin, xmax, 1000)

    fig, axes = plt.subplots(12, 4, figsize=(24, 40))
    fig.suptitle("Luck Index - Official Draw 2026 World Cup", fontsize=20, fontweight='bold', y=0.95)
    
    plt.subplots_adjust(hspace=0.6, wspace=0.3)
    
    group_names = list(draw.keys())
    
    for g_idx, group_name in enumerate(group_names):
        teams = draw[group_name]
        
        row = g_idx
        
        for t_idx, team_name in enumerate(teams):
            ax = axes[row, t_idx]
            
            plt.axes(ax)
            
            if t_idx == 0:
                ax.text(-0.2, 0.5, group_name, transform=ax.transAxes, 
                       rotation=90, va='center', ha='right', fontsize=12, fontweight='bold', color='#333')

            if team_name in distributions:
                display_luck_index_foot(distributions, luckIndex, team_name, x)
            else:
                ax.text(0.5, 0.5, f"{team_name}\n(No data)", ha='center', va='center')
                ax.set_xticks([])
                ax.set_yticks([])


def display_pot_luck(distributions, luckIndex, pot, pot_idx):
    """
    Displays a grid of Luck Index plots for all teams contained in a specific pot.
    """
    num_teams = len(pot[pot_idx])
    # 12 teams -> 4 columns and 3 rows
    cols = 4
    rows = math.ceil(num_teams / cols)
    
    fig, axes = plt.subplots(rows, cols, figsize=(18, rows * 3.5))
    fig.suptitle(f'Analyse du Luck Index du pot - {pot_idx}', fontsize=20, fontweight='bold', y=0.95)
    
    plt.subplots_adjust(hspace=0.6, wspace=0.3)
    
    
    axes_flat = axes.flatten()
    
    for i, team_obj in enumerate(pot):
        ax = axes_flat[i]
        plt.axes(ax) 
        
        team_name = team_obj.name
        if team_name in distributions:
            display_luck_index_foot(distributions, luckIndex, team_name)
        else:
            ax.set_title(f"{team_name} (No data)")
            ax.axis('off')

    # hiding the empty axis if num_teams is not a multiple of 4
    for j in range(i + 1, len(axes_flat)):
        axes_flat[j].axis('off')


def display_draw(draw: dict[str, list[str]]) -> None:
    """
    Visualizes the official World Cup draw results in a stylized grid format, 
    displaying groups and their respective teams.
    """
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


def bar_luck_index(luckIndex: dict[str, (float,float)]) -> None:
    """
    Creates and displays a ranked horizontal bar chart comparing the Luck Index of all teams, 
    sorted from the luckiest (highest index) to the unluckiest.
    """
    data = {}
    for team in luckIndex:
        data[team] = 100*luckIndex[team][1]
    
    sorted_data = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))
    teams = list(sorted_data.keys())
    lucks = list(sorted_data.values())

    fig, ax = plt.subplots(figsize=(7, len(teams) * 0.25 + 1))
    
    ax.barh(range(len(teams)), lucks, color='black', height=0.7)
    
    ax.set_yticks([])
    ax.set_xticks([])
    ax.invert_yaxis()
    
    max_val = max(lucks)
    ax.set_xlim(0, max_val * 2.0) 

    for spine in ax.spines.values():
        spine.set_visible(False)

    col_team_x = -max_val * 0.8    
    col_index_x = -max_val * 0.1   
    
    for i, (team, luck) in enumerate(zip(teams, lucks)):
        ax.text(col_team_x, i, team, va='center', ha='left', fontsize=9)
        ax.text(col_index_x, i, f"{luck:.1f}", va='center', ha='right', fontfamily='monospace', fontsize=9)

    header_y = -1.5
    ax.text(col_team_x, header_y, 'Team', weight='bold', fontsize=10, ha='left')
    ax.text(col_index_x, header_y, 'Luck index', weight='bold', fontsize=10, ha='right')
    
    ax.plot([0, max_val], [header_y + 0.5, header_y + 0.5], color='black', linewidth=1, clip_on=False)
    plt.tight_layout()