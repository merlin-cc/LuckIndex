import pandas as pd
import numpy as np
from Team import *
from draw_2026_WC import * 
from tirage_foot import run_simulation_foot

def generate_simulation_data():
    print("Chargement des données équipes...")
    data = pd.read_csv('football_ranking.csv')
    teams_list_obj = teams_list(data) 

    num_simulations = 25000
    print(f"Lancement de la simulation lourde ('{num_simulations}' itérations)...")
    distributions = run_simulation_foot(teams_list_obj, num_simulations)

    print("Extraction des données brutes...")
    raw_data = {}
    for team_name, kde_obj in distributions.items():
        raw_data[team_name] = kde_obj.dataset[0]

    df_results = pd.DataFrame(raw_data)

    csv_filename = 'simulations_distrib_foot.csv'
    df_results.to_csv(csv_filename, index=False)
    
    print(f"Succès ! Les données sont sauvegardées dans '{csv_filename}'.")
    print("N'oublie pas de faire un 'git add simulations_data.csv' !")

if __name__ == "__main__":
    generate_simulation_data()