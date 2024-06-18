from flask import Flask, render_template, request, redirect, url_for, abort, send_file
from model import Database, DataRepository
import requests
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
import matplotlib.dates as mdates

app = Flask(__name__)

@app.before_request
def before_request():
    # Initialise la base de données et le repository de données
    db = Database()
    data_repository = DataRepository(db)
    request.db = db
    request.data_repository = data_repository

@app.teardown_request
def teardown_request(exception):
    db = getattr(request, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/news')
def derniere_nouvelle():
    return render_template('news.html')

@app.route('/about')
def but():
    return render_template('about.html')

@app.route('/region')
def view_region():
    regions = request.data_repository.get_regions()
    return render_template('regions.html', regions=regions)

@app.route('/region/<code_region>')
def view_region_details(code_region):
    region_name = request.data_repository.db.query('SELECT libelle_region FROM regions WHERE code_region = ?', [code_region], one=True)
    if region_name:
        departements = request.data_repository.get_departments_by_region(code_region)
        return render_template('departements.html', departements=departements, libelle_region=region_name['libelle_region'], code_region=code_region)
    else:
        abort(404, description="Region not found")

@app.route('/departement/<code_departement>')
def view_departement_details(code_departement):
    departement_name = request.data_repository.db.query('SELECT libelle_departement FROM departements WHERE code_departement = ?', [code_departement], one=True)
    if departement_name:
        communes = request.data_repository.get_communes_by_department(code_departement)
        return render_template('communes.html', communes=communes, libelle_departement=departement_name['libelle_departement'], code_departement=code_departement)
    else:
        abort(404, description="Departement not found")

@app.route('/commune/<code_commune>/stations')
def stations_par_commune(code_commune):
    stations = request.data_repository.get_stations_by_commune(code_commune)
    if stations:
        return render_template('stations.html', stations=stations, libelle_commune='Nom de la commune')
    else:
        abort(404, description="No stations found for this commune")

@app.route('/select-observation', methods=['GET', 'POST'])
def select_observation():
    if request.method == 'POST':
        date_min = request.form['date_min']
        date_max = request.form['date_max']
        station_id = request.form['station_id']
        return redirect(url_for('fetch_observation', date_min=date_min, date_max=date_max, station_id=station_id))
    stations = request.data_repository.get_station_list()
    return render_template('select_observation.html', stations=stations)

@app.route('/fetch-observation')
def fetch_observation():
    date_min = request.args['date_min']
    date_max = request.args['date_max']
    station_id = request.args['station_id']
    observations = get_observation_data(station_id, date_min, date_max)
    return render_template('display_observation.html', observations=observations, date_min=date_min, date_max=date_max, station_id=station_id)

def get_emoji_for_label(label):
    emojis = {
        'Ecoulement visible': '🌊',
        'Ecoulement visible acceptable': '💧',
        'Ecoulement visible faible': '🌧️',
        'Ecoulement non visible': '🚫',
        'Assec': '🏜️',
        'Observation impossible': '❓'
    }
    return emojis.get(label, '❓')

def get_observation_data(station_id, date_min, date_max):
    url = f"https://hubeau.eaufrance.fr/api/v1/ecoulement/observations?code_station={station_id}&date_observation_min={date_min}&date_observation_max={date_max}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        observations = data.get('data', [])
        for obs in observations:
            obs['emoji'] = get_emoji_for_label(obs.get('libelle_ecoulement'))
        #print("Données reçues:", data)
        return observations
    else:
        print(f"Échec de la requête: HTTP {response.status_code}")
        return []

def generate_graph(observations, station_id):
    df = pd.DataFrame(observations)
    if df.empty:
        return "No data available for the given date range and station."
    
    flow_levels = {
        'Assec': 0, 'Ecoulement non visible': 1, 'Ecoulement visible faible': 2,
        'Ecoulement visible acceptable': 3, 'Ecoulement visible': 4, 'Observation impossible': 5
    }
    df['date_observation'] = pd.to_datetime(df['date_observation'])
    df['flow_category'] = df['libelle_ecoulement'].map(flow_levels)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    scatter = ax.scatter(df['date_observation'], df['flow_category'], c=df['flow_category'], cmap='viridis', marker='o')

    ax.set_yticks(list(flow_levels.values()))
    ax.set_yticklabels(list(flow_levels.keys()))
    ax.set_xlabel('Date d\'observation')
    ax.set_ylabel('Niveau d\'écoulement')
    ax.set_title(f'Observations de la station {station_id}')
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.xticks(rotation=45, ha='right')
    plt.grid(True)
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

@app.route('/generate-graph', endpoint='generate_graph')
def graph_route():
    date_min = request.args.get('date_min')
    date_max = request.args.get('date_max')
    station_id = request.args.get('station_id', '').strip().replace(" ", "")
    observations = get_observation_data(station_id, date_min, date_max)
    return generate_graph(observations, station_id)

if __name__ == '__main__':
    app.run(debug=True)
