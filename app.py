import requests
from flask import Flask, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def index():
    
    # Faites une requête à l'API pour obtenir les données
    response = requests.get('https://hubeau.eaufrance.fr/api/v1/ecoulement/stations')
    # Parsez le JSON
    data = response.json()
    
    # Extrait les informations nécessaires, par exemple une liste de stations
    stations = data['data']  # ou data['stations'], selon la structure exacte du JSON

    # Passer ces informations à votre template
    return render_template('index.html', stations=stations)

if __name__ == '__main__':
    app.run(debug=True)
