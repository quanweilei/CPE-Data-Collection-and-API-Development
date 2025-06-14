from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, and_
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)
db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'cpe_data.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
db = SQLAlchemy(app)

# Define CPE model
class CPE(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    cpe_22_uri = db.Column(db.String)
    cpe_23_uri = db.Column(db.String)
    references = db.Column(db.String)
    deprecated_22 = db.Column(db.String)
    deprecation_date_23 = db.Column(db.String)

def format_references(ref_string):
    if not ref_string:
        return []
    return [r.strip() for r in ref_string.split(",") if r.strip()]

# Initialize DB and load full Excel data
with app.app_context():
    db.create_all()
    if CPE.query.count() == 0:
        # change this to the number of entries you want to load, remove nrows=50 to load all
        entry_number = 50
        print("Loading", entry_number,"entries from Excel...")
        df = pd.read_excel("cpe_data.xlsx", nrows=entry_number, engine='openpyxl')
        for _, row in df.iterrows():
            entry = CPE(
                title=row["CPE Title"],
                cpe_22_uri=row["CPE 22 URI"],
                cpe_23_uri=row["CPE 23 URI"],
                references=row["Reference Links"],
                deprecated_22=row["CPE 22 Deprecated"],
                deprecation_date_23=row["CPE 23 Deprecation Date"]
            )
            db.session.add(entry)
        db.session.commit()
        print(f"Database created and loaded with {len(df)} entries.")
    else:
        print("Database already populated.")

@app.route("/api/cpes/search", methods=["GET"])
def search_cpes():
    cpe_title = request.args.get("cpe_title", "").strip()
    cpe_22_uri = request.args.get("cpe_22_uri", "").strip()
    cpe_23_uri = request.args.get("cpe_23_uri", "").strip()
    dep_date_str = request.args.get("deprecation_date", "").strip()

    query = CPE.query

    if cpe_title:
        query = query.filter(CPE.title.ilike(f"%{cpe_title}%"))
    if cpe_22_uri:
        query = query.filter(CPE.cpe_22_uri.ilike(f"%{cpe_22_uri}%"))
    if cpe_23_uri:
        query = query.filter(CPE.cpe_23_uri.ilike(f"%{cpe_23_uri}%"))
    if dep_date_str:
        try:
            dep_date = datetime.strptime(dep_date_str, "%Y-%m-%d").date()
            query = query.filter(
                or_(
                    and_(CPE.deprecated_22 != None, CPE.deprecated_22 <= dep_date_str),
                    and_(CPE.deprecation_date_23 != None, CPE.deprecation_date_23 <= dep_date_str)
                )
            )
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    results = query.all()
    return jsonify([
        {
            "id": c.id,
            "cpe_title": c.title,
            "cpe_22_uri": c.cpe_22_uri,
            "cpe_23_uri": c.cpe_23_uri,
            "reference_links": format_references(c.references),
            "cpe_22_deprecation_date": c.deprecated_22,
            "cpe_23_deprecation_date": c.deprecation_date_23
        } for c in results
    ])

@app.route("/api/cpes", methods=["GET"])
def get_all_cpes():
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    offset = (page - 1) * limit
    total = CPE.query.count()
    cpes = CPE.query.order_by(CPE.id).offset(offset).limit(limit).all()

    return jsonify({
        "page": page,
        "limit": limit,
        "total": total,
        "data": [
            {
                "id": c.id,
                "cpe_title": c.title,
                "cpe_22_uri": c.cpe_22_uri,
                "cpe_23_uri": c.cpe_23_uri,
                "reference_links": format_references(c.references),
                "cpe_22_deprecation_date": c.deprecated_22,
                "cpe_23_deprecation_date": c.deprecation_date_23
            } for c in cpes
        ]
    })

@app.route("/")
def index():
    query = request.args.get("q", "").strip()
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 15))
    offset = (page - 1) * limit

    base_query = CPE.query
    if query:
        base_query = base_query.filter(CPE.title.ilike(f"%{query}%"))

    total = base_query.count()
    cpes = base_query.order_by(CPE.id).offset(offset).limit(limit).all()

    return render_template(
        "index.html",
        cpes=cpes,
        page=page,
        limit=limit,
        total=total,
        request=request  # pass request explicitly so request.args works in template
    )

if __name__ == "__main__":
    app.run(debug=True)
