from flask import Flask, render_template
from Player import *
from tirage import *
import matplotlib
matplotlib.use('Agg')
import io
import base64


data = pd.read_csv('tennisATPRanking.csv')

list_players = total_players_list(data)

distributions = run_simulation(list_players, 100)
real_draw = createDraws(list_players)
luckIndex = luck_index(list_players, distributions, real_draw)

display_random(distributions, luckIndex, list_players, 3)

img = io.BytesIO()
plt.savefig(img, format='png', bbox_inches='tight')
img.seek(0) # Revenir au début du fichier virtuel
plt.close()

app = Flask (__name__)
pl_url = base64.b64encode(img.getvalue()).decode('utf8')

@app.route("/")
def welcome():
    return render_template("welcome.html", plot_url = pl_url)

if __name__ == "__main__":
    app.run(debug=True)
