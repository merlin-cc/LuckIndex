import pandas as pd
import numpy as np
from Football.Team import *
from Football.Draw_2026_WC import * 
from Football.Draw_foot import run_simulation_foot
from scipy.stats import gaussian_kde
import os

### ---------------------------------------------------------------------------------------- Code Objective --------------------------------------------------------------------------------------- ###
###                                                     Building a CSV file containing the distribution and extracting these distributions if needed                                                ###
#######################################################################################################################################################################################################



def generate_simulation_data(input_csv: str = 'Football/football_ranking.csv', 
                             output_csv: str = 'Football/simulations_distrib_foot.csv', 
                             n_simulations: int = 25000) -> None:
    """
    Generates and saves Monte Carlo simulation data to a CSV file.
    
    This pre-computation allows the main application to load distributions 
    instantly instead of recalculating them at runtime.

    Args:
        input_csv (str): Path to the source CSV file containing team rankings.
        output_csv (str): Destination path for the generated simulation data.
        n_simulations (int): Number of iterations for the simulation (higher is more accurate but slower).
    """
    
    print(f"Loading team data from '{input_csv}'...")
    try:
        data = pd.read_csv(input_csv)
    except FileNotFoundError:
        print(f"Error: File '{input_csv}' not found. Please check the path.")
        return

    teams_list_obj = teams_list(data)

    # Run the heavy simulation process
    print(f"Starting heavy simulation ({n_simulations} iterations)...")
    distributions = run_simulation_foot(teams_list_obj, n_simulations)

    # Extract raw data points from the KDE objects
    raw_data = {}
    for team_name, kde_obj in distributions.items():
        raw_data[team_name] = kde_obj.dataset[0]

    # Create DataFrame and save to CSV
    df_results = pd.DataFrame(raw_data)
    df_results.to_csv(output_csv, index=False)
    
    print(f"Success! Data saved to '{output_csv}'.")



def get_distributions_foot(list_teams: list[FootTeam], n_input : int) -> dict[str, gaussian_kde]:
    """
    Loading distributions for football from the csv file to imporve speed computation
    """
    csv_path = 'Football/simulations_distrib_foot.csv'
    
    if os.path.exists(csv_path):
        print("Loading the simulations using the CSV file...")
        try:
            df = pd.read_csv(csv_path)
            distributions = {}

            for team_name in df.columns:
                distributions[team_name] = gaussian_kde(df[team_name].values)
            
            print("Distributions has been succesfully extracted")
            return distributions
            
        except Exception as e:
            print(f"Error while reading the CSV file: {e}")

    print(f"Live computation, warning this can take up to several hours (roughly 1 sim/sec) ({n_input} simulations)...")
    return run_simulation_foot(list_teams, n_input)

# ------------------------------------------------------------
# Execution
# ------------------------------------------------------------


if __name__ == "__main__":
    generate_simulation_data()