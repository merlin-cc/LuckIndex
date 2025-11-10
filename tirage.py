import random as rd
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


def createDraws(list_players):
    """
    create 32 groups of 4 players with one top32 player in each groups
    """
    draw = {}
    try :
        len(list_players) == 128
    except ValueError:
        print("Not enough player to create 32 pull")
    other_players = list_players[32:]
    rd.shuffle(other_players)
    
    for i in range(32):
        player_2 = other_players.pop()
        player_3 = other_players.pop()
        player_4 = other_players.pop()
        
        draw[i] = [player_2, player_3, player_4]

    return draw

print(createDraws())