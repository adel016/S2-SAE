from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('ecoulement.db')
    conn.row_factory = sqlite3.Row # Permet d'accéder aux colonnes par leurs noms 
    return conn

@app.route('/')
def home():
    db = get_db()
    cur = db.execute('SELECT * FROM regions')
    regions = cur.fetchall()
    db.close()
    return render_template('regions.html', regions=regions)

@app.route('/region/<code_region>')
def view_region_details(code_region):
    db = get_db()
    cur = db.execute('SELECT * FROM departements WHERE code_region = ?', (code_region,))
    departements = cur.fetchall()
    db.close()
    return render_template('departements.html', departements=departements, code_region=code_region)

if __name__ == '__main__':
    app.run(debug=True)
