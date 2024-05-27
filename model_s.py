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


# Faire une requête à l'API
response = requests.get(url)
data = response.json()

# Extraire les données et les insérer dans la table SQLite
if 'data' in data:
    regions_seen = set()
    departements_seen = set()
    communes_seen = set()
    for station in data['data']:
        code_region = station.get('code_region')
        libelle_region = station.get('libelle_region')
        code_departement = station.get('code_departement')
        libelle_departement = station.get('libelle_departement')
        code_commune = station.get('code_commune')
        libelle_commune = station.get('libelle_commune')
        
        # Insertion des régions sans doublons
        if code_region and libelle_region and code_region not in regions_seen:
            cursor.execute('INSERT OR IGNORE INTO regions (code_region, libelle_region) VALUES (?, ?)',
                           (code_region, libelle_region))
            regions_seen.add(code_region)

        # Insertion des départements sans doublons
        if code_departement and libelle_departement and code_departement not in departements_seen:
            cursor.execute('INSERT OR IGNORE INTO departements (code_departement, libelle_departement, code_region) VALUES (?, ?, ?)',
                           (code_departement, libelle_departement, code_region))
            departements_seen.add(code_departement)

        # Insertion des communes sans doublons
        if code_commune and libelle_commune and code_commune not in communes_seen:
            cursor.execute('INSERT OR IGNORE INTO communes (code_commune, libelle_commune, code_departement) VALUES (?, ?, ?)',
                           (code_commune, libelle_commune, code_departement))
            departements_seen.add(code_commune)
            

# Valider les changement 
conn.commit()

# Fermer la connexion à la base de donnée 
conn.close()