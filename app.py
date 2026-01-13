from flask import Flask, render_template, request
from Player import *
from tirage import *
from Team import *
from tirage_foot import *
from draw_2026_WC import *
import matplotlib
matplotlib.use('Agg')
import io
import base64

######-----------Logique python---------------######

data_tennis = pd.read_csv('tennisATPRanking.csv')

list_players = total_players_list(data_tennis)
players_name = get_players_name(data_tennis)
index_players = total_players_index(list_players)
players_name.sort()

data_foot = pd.read_csv('football_ranking.csv')
list_teams = teams_list(data_foot)
teams_name = get_teams_name(data_foot)
######-----------Définition de l'app---------------######

app = Flask (__name__)

@app.route("/", methods=['GET', 'POST'])
def welcome():
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
                j1_name = str(request.form.get('joueur1'))
                j2_name = str(request.form.get('joueur2'))
                j3_name = str(request.form.get('joueur3'))
                j4_name = str(request.form.get('joueur4'))

                p1 = index_players[j1_name]
                p2 = index_players[j2_name]
                p3 = index_players[j3_name]
                p4 = index_players[j4_name]

                try:
                    if (p1 == p2 or p1 == p3 or p1 == p4 or p2 == p3 or p2 == p4 or p3 == p4):
                        raise (SamePlayersError)
                    
                    else:
                        manual_tirage([p1,p2,p3,p4], distributions, n)
                        img = io.BytesIO()
                        plt.savefig(img, format='png', bbox_inches='tight')
                        img.seek(0) # Revenir au début du fichier virtuel
                        plt.close()

                        image_a_afficher = base64.b64encode(img.getvalue()).decode('utf8')

                except SamePlayersError as e:
                    error = e.msg

                except : 
                    error = "Une erreur est survenue"

        elif sport == "football":
            choix_menu_foot = request.form.get('mode_jeu_foot')

            distributions_foot = run_simulation_foot(list_teams, n)
            real_draw = single_draw(pots)
            luckIndex = luck_index_foot(list_teams, distributions_foot, real_draw)
        
            if choix_menu_foot == "Aléatoire" :
                display_random_foot(distributions_foot, luckIndex, 3, n)
                
            elif choix_menu_foot == "Team of interest":
                team_name = str(request.form.get('team_of_interest'))
                if team_name.strip() in distributions_foot:
                    display_luck_index_foot(distributions_foot, luckIndex, team_name.strip())
                else :
                    print("ca flop")

            elif choix_menu_foot == "Pot of interest":
                pot_idx = int(request.form.get('pot_of_interest'))
                display_pot_luck(distributions_foot, luckIndex, pots[pot_idx], f"Chapeau {pot_idx + 1}")

            img = io.BytesIO()
            plt.savefig(img, format='png', bbox_inches='tight')
            img.seek(0)
            plt.close()
            image_a_afficher = base64.b64encode(img.getvalue()).decode('utf8')



    return render_template("welcome.html", plot_url=image_a_afficher, active_tab=active_tab, joueurs = players_name, teams = teams_name, valeue_n = n, err = error)



if __name__ == "__main__":
    app.run(debug=True, port=5001)
