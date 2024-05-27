from flask import Flask, render_template, abort
import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('ecoulement.db')
    conn.row_factory = sqlite3.Row # Permet d'accéder aux colonnes par leurs noms 
    return conn

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/region')
def view_region():
    db = get_db()
    cur = db.execute('SELECT * FROM regions')
    regions = cur.fetchall()
    db.close()
    return render_template('regions.html', regions=regions)
    


@app.route('/region/<code_region>')
def view_region_details(code_region):
    db = get_db()
    # Fetch the region name along with the departments
    region_query = db.execute('SELECT libelle_region FROM regions WHERE code_region = ?', (code_region,))
    region_name = region_query.fetchone()
    
    department_query = db.execute('SELECT * FROM departements WHERE code_region = ?', (code_region,))
    departements = department_query.fetchall()
    db.close()
    
    if region_name:
        return render_template('departements.html', departements=departements, libelle_region=region_name['libelle_region'], code_region=code_region)
    else:
        return "Region not found", 404
    
    
@app.route('/departement/<code_departement>')
def view_departement_details(code_departement):
    db = get_db()
    # Récupérer le nom du département
    departement_query = db.execute('SELECT libelle_departement FROM departements WHERE code_departement = ?', (code_departement,))
    departement_name = departement_query.fetchone()

    # Récupérer les communes appartenant à ce département
    commune_query = db.execute('SELECT * FROM communes WHERE code_departement = ?', (code_departement,))
    communes = commune_query.fetchall()
    db.close()
    
    if departement_name:
        return render_template('communes.html', communes=communes, libelle_departement=departement_name['libelle_departement'], code_departement=code_departement)
    else:
        abort(404, description="Departement not found")

    


if __name__ == '__main__':
    app.run(debug=True)
