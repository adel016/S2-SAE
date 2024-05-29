import sqlite3
import requests
import os

# Obtenez le chemin d'accès au dossier du script actuel
base_dir = os.path.dirname(os.path.abspath(__file__))

# Spécifiez le chemin de la base de données relativement à ce dossier
db_path = os.path.join(base_dir, 'ecoulement.db')
# URL de l'API
url = 'https://hubeau.eaufrance.fr/api/v1/ecoulement/stations'

# Création ou connexion à la DB
conn = sqlite3.connect(db_path)
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

# Création de la table stations
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
    FOREIGN KEY (code_commune) REFERENCES communes(code_commune)
)
''')

# Faire une requête à l'API
response = requests.get(url)
data = response.json()

print(data['data'][0])  # Affiche les données du premier élément pour vérifier


if 'data' in data:
    communes_seen = set()
    stations_seen = set()
    regions_seen = set()
    departements_seen = set()

    for station in data['data']:
        # Partie régions
        code_region = station.get('code_region')
        libelle_region = station.get('libelle_region')

        if code_region and libelle_region and code_region not in regions_seen:
            cursor.execute('''
                INSERT OR IGNORE INTO regions (code_region, libelle_region)
                VALUES (?, ?)
            ''', (code_region, libelle_region))
            regions_seen.add(code_region)

        # Partie départements
        code_departement = station.get('code_departement')
        libelle_departement = station.get('libelle_departement')

        if code_departement and libelle_departement and code_departement not in departements_seen:
            cursor.execute('''
                INSERT OR IGNORE INTO departements (code_departement, libelle_departement, code_region)
                VALUES (?, ?, ?)
            ''', (code_departement, libelle_departement, code_region))
            departements_seen.add(code_departement)

        # Partie communes
        code_commune = station.get('code_commune')
        libelle_commune = station.get('libelle_commune')

        if code_commune and libelle_commune and code_commune not in communes_seen:
            cursor.execute('''
                INSERT OR IGNORE INTO communes (code_commune, libelle_commune, code_departement)
                VALUES (?, ?, ?)
            ''', (code_commune, libelle_commune, code_departement))
            communes_seen.add(code_commune)

        # Partie stations
        code_station = station.get('code_station')
        libelle_station = station.get('libelle_station')
        uri_station = station.get('uri_station')
        code_cours_eau = station.get('code_cours_eau')
        libelle_cours_eau = station.get('libelle_cours_eau')
        uri_cours_eau = station.get('uri_cours_eau')
        etat_station = station.get('etat_station')
        date_maj_station = station.get('date_maj_station')

        if code_station not in stations_seen:
            cursor.execute('''
                INSERT OR IGNORE INTO stations (
                    code_station, libelle_station, uri_station, code_commune, code_cours_eau,
                    libelle_cours_eau, uri_cours_eau, etat_station, date_maj_station)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (code_station, libelle_station, uri_station, code_commune, code_cours_eau,
                  libelle_cours_eau, uri_cours_eau, etat_station, date_maj_station))
            stations_seen.add(code_station)

# Valider les changements
conn.commit()

# Fermer la connexion à la base de données
conn.close()
