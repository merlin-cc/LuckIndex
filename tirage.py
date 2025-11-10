import random as rd
from collections import defaultdict
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

def createDraws(list_players):
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


def get_first_round_opponents_from_draw(draw):
    """From a bracket (ordered list of 128 players), create a map of player -> opponent."""
    opponents_map = {}
    for i in range(0, 128, 2):
        p1 = draw[i]
        p2 = draw[i+1]
        opponents_map[p1.name] = p2
        opponents_map[p2.name] = p1
    return opponents_map


def run_simulation(list_players, num_simulations=10000):
    """
    Runs N simulations of the draw to compute the distribution of first-round
    opponent strength for each player.
    Returns a dictionary mapping player names to a list of their opponents' ELOs.
    """
    print(f"Running {num_simulations} simulations...")
    # defaultdict simplifies appending to lists for new keys
    opponent_strength_dist = defaultdict(list)

    for _ in range(num_simulations):
        # 1. Create a valid random bracket
        draw = createDraws(list_players)
        
        # 2. Get the first-round pairings
        opponents_map = get_first_round_opponents_from_draw(draw)

        # 3. Record the strength (elo) of the opponent for each player
        for player_name, opponent in opponents_map.items():
            opponent_strength_dist[player_name].append(opponent.elo)

    print("Simulation complete.")
    return opponent_strength_dist