import sqlite3
import requests

# URL de l'API
url = 'https://hubeau.eaufrance.fr/api/v1/ecoulement/stations'

# Création ou connexion àa la DB
conn = sqlite3.connect('ecoulement.db')

# créer un objet curseur pour utiliser des commande sql 
cursor = conn.cursor()

# Création de la table regions 
cursor.execute('''
    CREATE TABLE IF NOT EXISTS regions(
        code_region INTEGER PRIMARY KEY,
        libelle_region TEXT UNIQUE
    )
''')

# Création de la table departements
cursor.execute('''
    CREATE TABLE IF NOT EXISTS departements (
        code_departement TEXT PRIMARY KEY,
        libelle_departement TEXT UNIQUE,
        code_region TEXT,
        FOREIGN KEY (code_region) REFERENCES regions(code_region)
    )
''')

# Création de la table communes
cursor.execute('''
    CREATE TABLE IF NOT EXISTS communes (
        code_commune TEXT PRIMARY KEY,
        libelle_commune TEXT UNIQUE,
        code_departement TEXT,
        FOREIGN KEY (code_departement) REFERENCES departements(code_departement)
    )
''')

# Création de la table sttions
cursor.execute('''
CREATE TABLE IF NOT EXISTS stations (
    code_station TEXT PRIMARY KEY,
    libelle_station TEXT UNIQUE,
    uri_station TEXT,
    code_commune TEXT,
    code_cours_eau TEXT,
    libelle_cours_eau TEXT,
    uri_cours_eau TEXT,
    etat_station TEXT,
    date_maj_station TEXT,
    FOREIGN KEY (code_commune) REFERENCES commune(code_commune)
)
''')


# Faire une requête à l'API
response = requests.get(url)
data = response.json()

if 'data' in data:
    communes_seen = set()
    stations_seen = set()
    for station in data['data']:
        # Récupérer les informations sur les stations
        code_station = station.get('code_station')
        libelle_station = station.get('libelle_station')
        uri_station = station.get('uri_station')
        code_commune = station.get('code_commune')
        code_cours_eau = station.get('code_cours_eau')
        libelle_cours_eau = station.get('libelle_cours_eau')
        uri_cours_eau = station.get('uri_cours_eau')
        etat_station = station.get('etat_station')
        date_maj_station = station.get('date_maj_station')

        # Insertion des informations de la station dans la base de données
        if code_station not in stations_seen:
            cursor.execute('''
                INSERT OR IGNORE INTO stations (
                    code_station, libelle_station, uri_station, code_commune, code_cours_eau,
                    libelle_cours_eau, uri_cours_eau, etat_station, date_maj_station)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (code_station, libelle_station, uri_station, code_commune, code_cours_eau,
                  libelle_cours_eau, uri_cours_eau, etat_station, date_maj_station))
            stations_seen.add(code_station)

# Valider les changement 
conn.commit()

# Fermer la connexion à la base de donnée 
conn.close()