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

        distributions = run_simulation(list_players, n)
        real_draw = createDraws(list_players)
        luckIndex = luck_index(list_players, distributions, real_draw)

        display_random(distributions, luckIndex, list_players, 3, n)

        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        img.seek(0) # Revenir au début du fichier virtuel
        plt.close()

        image_a_afficher = base64.b64encode(img.getvalue()).decode('utf8')

    return render_template("welcome.html", plot_url=image_a_afficher, joueurs = players_name)



if __name__ == "__main__":
    app.run(debug=True)
