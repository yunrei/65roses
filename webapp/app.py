from flask import Flask, render_template, request, jsonify
from sqlalchemy import create_engine, text
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///cftr_variants.db')
engine = create_engine(DATABASE_URL)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/variant_suggestions')
def variant_suggestions():
    term = request.args.get('term', '')
    if len(term) < 2:
        return jsonify([])
    
    query = text("""
        SELECT gnomad_id, classification 
        FROM variants 
        WHERE gnomad_id LIKE :term 
        LIMIT 10
    """)
    
    with engine.connect() as conn:
        results = conn.execute(query, {'term': f'%{term}%'}).fetchall()
    
    suggestions = [
        {
            'value': row[0],
            'label': f"{row[0]} ({row[1] if row[1] else 'Unknown classification'})"
        }
        for row in results
    ]
    
    return jsonify(suggestions)

@app.route('/search_variant', methods=['POST'])
def search_variant():
    variant_id = request.form.get('variant_id')
    if not variant_id:
        return jsonify({'found': False})
    
    # Query variant information
    variant_query = text("""
        SELECT gnomad_id, classification, population_frequency
        FROM variants
        WHERE gnomad_id = :variant_id
    """)
    
    # Query symptoms
    symptoms_query = text("""
        SELECT DISTINCT s.name
        FROM symptoms s
        JOIN variant_symptoms vs ON s.id = vs.symptom_id
        JOIN variants v ON vs.variant_id = v.id
        WHERE v.gnomad_id = :variant_id
    """)
    
    # Query treatments
    treatments_query = text("""
        SELECT DISTINCT t.name
        FROM treatments t
        JOIN variant_treatments vt ON t.id = vt.treatment_id
        JOIN variants v ON vt.variant_id = v.id
        WHERE v.gnomad_id = :variant_id
    """)
    
    with engine.connect() as conn:
        variant = conn.execute(variant_query, {'variant_id': variant_id}).fetchone()
        
        if not variant:
            return jsonify({'found': False})
        
        symptoms = [row[0] for row in conn.execute(symptoms_query, {'variant_id': variant_id}).fetchall()]
        treatments = [row[0] for row in conn.execute(treatments_query, {'variant_id': variant_id}).fetchall()]
    
    if not symptoms:
        symptoms = ['No symptoms data available']
    if not treatments:
        treatments = ['No treatments data available']
    
    return jsonify({
        'found': True,
        'variant': {
            'gnomad_id': variant[0],
            'classification': variant[1],
            'population_frequency': variant[2]
        },
        'symptoms': symptoms,
        'treatments': treatments,
        'no_info': False
    })

@app.route('/get_symptoms')
def get_symptoms():
    query = text("""
        SELECT s.name, s.category, s.description, COUNT(vs.variant_id) as variant_count
        FROM symptoms s
        LEFT JOIN variant_symptoms vs ON s.id = vs.symptom_id
        GROUP BY s.id, s.name, s.category, s.description
        ORDER BY s.category, s.name
    """)
    
    with engine.connect() as conn:
        results = conn.execute(query).fetchall()
    
    symptoms = [
        {
            'name': row[0],
            'category': row[1],
            'description': row[2],
            'variant_count': row[3]
        }
        for row in results
    ]
    
    return jsonify(symptoms)

@app.route('/search_by_symptoms', methods=['POST'])
def search_by_symptoms():
    symptoms = request.form.getlist('symptoms[]')
    if not symptoms:
        return jsonify([])
    
    query = text("""
        SELECT 
            v.gnomad_id,
            v.classification as clinvar_classification,
            GROUP_CONCAT(DISTINCT s.name) as matching_symptoms,
            COUNT(DISTINCT s.name) as symptom_match_count
        FROM variants v
        JOIN variant_symptoms vs ON v.id = vs.variant_id
        JOIN symptoms s ON vs.symptom_id = s.id
        WHERE s.name IN :symptoms
        GROUP BY v.id, v.gnomad_id, v.classification
        HAVING COUNT(DISTINCT s.name) = :symptom_count
        ORDER BY symptom_match_count DESC
        LIMIT 10
    """)
    
    with engine.connect() as conn:
        results = conn.execute(
            query, 
            {'symptoms': tuple(symptoms), 'symptom_count': len(symptoms)}
        ).fetchall()
    
    variants = [
        {
            'gnomad_id': row[0],
            'clinvar_classification': row[1],
            'matching_symptoms': row[2],
            'symptom_match_count': row[3]
        }
        for row in results
    ]
    
    return jsonify(variants)

if __name__ == '__main__':
    app.run(debug=True) 