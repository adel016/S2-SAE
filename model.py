import sqlite3
import os

class Database:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ecoulement.db')
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    def query(self, query, args=(), one=False):
        cur = self.conn.cursor()
        cur.execute(query, args)
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv

    def close(self):
        self.conn.close()

class DataRepository:
    def __init__(self, db):
        self.db = db

    def get_regions(self):
        return self.db.query("SELECT * FROM regions")

    def get_departments_by_region(self, code_region):
        return self.db.query("SELECT * FROM departements WHERE code_region = ?", [code_region])

    def get_communes_by_department(self, code_departement):
        return self.db.query("SELECT * FROM communes WHERE code_departement = ?", [code_departement])

    def get_stations_by_commune(self, code_commune):
        return self.db.query("SELECT code_station, libelle_station, etat_station, date_maj_station, uri_cours_eau FROM stations WHERE code_commune = ?", [code_commune])

    def get_station_list(self):
        return self.db.query("SELECT code_station, libelle_station FROM stations")
