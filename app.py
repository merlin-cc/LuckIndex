from flask import Flask, render_template, request
from Player import *
from tirage import *
import matplotlib
matplotlib.use('Agg')
import io
import base64

######-----------Logique python---------------######

data = pd.read_csv('tennisATPRanking.csv')

list_players = total_players_list(data)
players_name = get_players_name(data)
players_name.sort()

######-----------Définition de l'app---------------######

app = Flask (__name__)

@app.route("/", methods=['GET', 'POST'])
def welcome():
    image_a_afficher = None
    error = None
    n = 100
    if request.method == 'POST':
        entree_nombre = request.form.get('nombre_simulations')
        choix_menu = request.form.get('mode_jeu')
        
        try:
            n = int(entree_nombre)
        except (ValueError, TypeError):
            n = 100

        ######-----------Logique python---------------######

        data = pd.read_csv('tennisATPRanking.csv')

        list_players = total_players_list(data)
        index_players = total_players_index(list_players)
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
        
        if choix_menu == "Manuel":
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

    return render_template("welcome.html", plot_url=image_a_afficher, joueurs = players_name, err = error)



if __name__ == "__main__":
    app.run(debug=True)
