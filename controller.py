from flask import Flask, render_template, abort, request, redirect, url_for
import sqlite3
import os
import requests

app = Flask(__name__)

def get_db():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ecoulement.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

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
    db = get_db()
    try:
        cur = db.execute('SELECT * FROM regions')
        regions = cur.fetchall()
    finally:
        db.close()
    return render_template('regions.html', regions=regions)

@app.route('/region/<code_region>')
def view_region_details(code_region):
    db = get_db()
    try:
        region_query = db.execute('SELECT libelle_region FROM regions WHERE code_region = ?', (code_region,))
        region_name = region_query.fetchone()
        if region_name:
            department_query = db.execute('SELECT * FROM departements WHERE code_region = ?', (code_region,))
            departements = department_query.fetchall()
            return render_template('departements.html', departements=departements, libelle_region=region_name['libelle_region'], code_region=code_region)
        else:
            return "Region not found", 404
    finally:
        db.close()

@app.route('/departement/<code_departement>')
def view_departement_details(code_departement):
    db = get_db()
    try:
        departement_query = db.execute('SELECT libelle_departement FROM departements WHERE code_departement = ?', (code_departement,))
        departement_name = departement_query.fetchone()
        if departement_name:
            commune_query = db.execute('SELECT * FROM communes WHERE code_departement = ?', (code_departement,))
            communes = commune_query.fetchall()
            return render_template('communes.html', communes=communes, libelle_departement=departement_name['libelle_departement'], code_departement=code_departement)
        else:
            abort(404, description="Departement not found")
    finally:
        db.close()

@app.route('/commune/<code_commune>/stations')
def stations_par_commune(code_commune):
    db = get_db()
    try:
        cur = db.execute('SELECT code_station, libelle_station, etat_station, date_maj_station, uri_cours_eau FROM stations WHERE code_commune = ?', (code_commune,))
        stations = cur.fetchall()
        if not stations:
            abort(404, description="No stations found for this commune")
        return render_template('stations.html', stations=stations, libelle_commune='Nom de la commune')
    except sqlite3.Error as e:
        abort(500, description=f"Database error: {e}")
    finally:
        db.close()



@app.route('/select-observation', methods=['GET', 'POST'])
def select_observation():
    db = get_db()
    if request.method == 'POST':
        date = request.form.get('date')
        station_id = request.form.get('station_id')
        if date and station_id:
            return redirect(url_for('fetch_observation', date=date, station_id=station_id))
        else:
            return "Date ou station manquante", 400

    stations = db.execute('SELECT code_station, libelle_station FROM stations').fetchall()
    db.close()
    return render_template('select_observation.html', stations=stations)

@app.route('/fetch-observation')
def fetch_observation():
    date = request.args.get('date')
    station_id = request.args.get('station_id')
    observations = get_observation_data(station_id, date)
    
    # Ajout de la logique pour attribuer un emoji en fonction de l'état de l'écoulement
    for observation in observations:
        label = observation['libelle_ecoulement']
        if label == 'Ecoulement visible':
            observation['emoji'] = '🌊'  # Ecoulement fort
        elif label == 'Ecoulement visible acceptable':
            observation['emoji'] = '💧'  # Ecoulement acceptable
        elif label == 'Ecoulement visible faible':
            observation['emoji'] = '🌧️'  # Ecoulement faible
        elif label == 'Ecoulement non visible':
            observation['emoji'] = '🚫'  # Pas d'écoulement visible
        elif label == 'Assec':
            observation['emoji'] = '🏜️'  # Sec
        elif label == 'Observation impossible':
            observation['emoji'] = '❓'  # Donnée incertaine

    return render_template('display_observation.html', observations=observations, date=date, station_id=station_id)


def get_observation_data(station_id, date):
    observation_url = f"https://hubeau.eaufrance.fr/api/v1/ecoulement/observations?code_station={station_id}&date_observation={date}"
    response = requests.get(observation_url)
    if response.status_code == 200:
        data = response.json()
        return data.get('data', [])
    return []



if __name__ == '__main__':
    app.run(debug=True)
