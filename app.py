from flask import Flask, render_template, request
from tirage import *
from tirage_foot import *
import matplotlib
matplotlib.use('Agg')
import io
import os
import base64
######-----------Logique python---------------######


##TENNIS
data_tennis = pd.read_csv('tennisATPRanking.csv')
list_players = total_players_list(data_tennis)
players_name = get_players_name(data_tennis)
index_players = total_players_index(list_players)
players_name.sort()

## FOOTBALL
teams_name = [team.name for team in all_teams]
data_foot = pd.read_csv('football_ranking.csv')
data_foot = data_foot[data_foot['Team'].isin(teams_name)].reset_index(drop=True)
list_teams = teams_list(data_foot)

def get_distributions_foot_optimized(list_teams, n_input):
    """
    Charge les distributions depuis le CSV s'il existe,
    sinon recalcule tout (lent).
    """
    csv_path = 'simulations_distrib_foot.csv'
    
    if os.path.exists(csv_path):
        print("Chargement des simulations depuis le CSV (rapide)...")
        try:
            # 1. Lire le CSV
            df = pd.read_csv(csv_path)
            
            # 2. Reconstruire les KDE pour chaque équipe
            distributions = {}
            # df.columns contient les noms des équipes
            for team_name in df.columns:
                # On recrée l'objet gaussian_kde à partir des colonnes du CSV
                distributions[team_name] = gaussian_kde(df[team_name].values)
            
            print("Distributions reconstruites avec succès !")
            return distributions
            
        except Exception as e:
            print(f"Erreur lors de la lecture du CSV : {e}")
            print("Retour au calcul manuel...")

    # Si pas de CSV ou erreur, on fait la méthode lente
    print(f"Calcul en direct ({n_input} simulations)...")
    return run_simulation_foot(list_teams, n_input)


######-----------Définition de l'app---------------######

app = Flask (__name__)

@app.route("/", methods=['GET', 'POST'])
def welcome():
    image_draw = None
    image_a_afficher = None
    error = None
    n = 1000

    active_tab = 'tennis' # to remember where the user was

    if request.method == 'POST':
        sport = request.form.get('sport')
        active_tab = sport
        entree_nombre = request.form.get('nombre_simulations')
        
        try:
            n = int(entree_nombre)
        except (ValueError, TypeError):
            n = 1000

        ######-----------Logique python---------------######

        if sport == "tennis":
            choix_menu = request.form.get('mode_jeu')
            distributions = run_simulation(list_players, n)

            if choix_menu == "Aléatoire" :
                real_draw = createDraws(list_players)
                luckIndex = luck_index(list_players, distributions, real_draw)
                display_random(distributions, luckIndex, list_players, 3, n)
                img = io.BytesIO()
                plt.savefig(img, format='png', bbox_inches='tight')
                img.seek(0) # Revenir au début du fichier virtuel
                plt.close()

                image_a_afficher = base64.b64encode(img.getvalue()).decode('utf8')
            
            elif choix_menu == "Manuel":
                try:
                    j1_name = str(request.form.get('joueur1'))
                    j2_name = str(request.form.get('joueur2'))
                    j3_name = str(request.form.get('joueur3'))
                    j4_name = str(request.form.get('joueur4'))

                    p1 = index_players[j1_name]
                    p2 = index_players[j2_name]
                    p3 = index_players[j3_name]
                    p4 = index_players[j4_name]

                    
                    if (p1 == p2 or p1 == p3 or p1 == p4 or p2 == p3 or p2 == p4 or p3 == p4):
                        raise (SamePlayersError)

                    
                except SamePlayersError as e:
                    error = e.msg

                except KeyError:
                    error = "Veuillez sélectionner 4 joueurs."

                except  : 
                    error = "Une erreur est survenue"

                else:
                    manual_tirage([p1,p2,p3,p4], distributions, n)
                    img = io.BytesIO()
                    plt.savefig(img, format='png', bbox_inches='tight')
                    img.seek(0) # Revenir au début du fichier virtuel
                    plt.close()

                    image_a_afficher = base64.b64encode(img.getvalue()).decode('utf8')

        elif sport == "football":
            image_draw = None
            choix_menu_foot = request.form.get('mode_jeu_foot')

            distributions_foot = get_distributions_foot_optimized(list_teams, n)

            if choix_menu_foot == "Official Draw":
                real_draw = get_official_draw_2026()
            else:
                real_draw = single_draw(pots)
            
            luckIndex = luck_index_foot(list_teams, distributions_foot, real_draw)

            display_draw(real_draw)
            img0 = io.BytesIO()
            plt.savefig(img0, format='png', bbox_inches='tight')
            img0.seek(0)
            plt.close()
            image_draw = base64.b64encode(img0.getvalue()).decode('utf8')

            if choix_menu_foot == "Official Draw":
                display_random_foot(distributions_foot, luckIndex, 7, n)
        
            if choix_menu_foot == "Aléatoire" :
                display_random_foot(distributions_foot, luckIndex, 3, n)
                
            elif choix_menu_foot == "Team of interest":
                team_name = str(request.form.get('team_of_interest'))
                display_luck_index_foot(distributions_foot, luckIndex, team_name.strip())

            elif choix_menu_foot == "Pot of interest":
                pot_idx = int(request.form.get('pot_of_interest'))
                display_pot_luck(distributions_foot, luckIndex, pots[pot_idx], f"Chapeau {pot_idx + 1}")

            img = io.BytesIO()
            plt.savefig(img, format='png', bbox_inches='tight')
            img.seek(0)
            plt.close()
            image_a_afficher = base64.b64encode(img.getvalue()).decode('utf8')



    return render_template("welcome.html", plot_url=image_a_afficher, draw_url = image_draw, active_tab=active_tab, joueurs = players_name, teams = teams_name, valeue_n = n, err = error)



if __name__ == "__main__":
    app.run(debug=True, port=5001)
