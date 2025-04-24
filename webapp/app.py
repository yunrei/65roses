from flask import Flask, render_template, request, jsonify
import sqlite3
import pandas as pd

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('cftr_variants.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search_variant', methods=['POST'])
def search_variant():
    variant_id = request.form.get('variant_id')
    conn = get_db_connection()
    
    # Get variant information
    variant = conn.execute('''
        SELECT v.*, 
               GROUP_CONCAT(DISTINCT s.name) as symptoms,
               GROUP_CONCAT(DISTINCT t.name) as treatments
        FROM variants v
        LEFT JOIN variant_symptoms vs ON v.id = vs.variant_id
        LEFT JOIN symptoms s ON vs.symptom_id = s.id
        LEFT JOIN variant_treatments vt ON v.id = vt.variant_id
        LEFT JOIN treatments t ON vt.treatment_id = t.id
        WHERE v.gnomad_id = ?
        GROUP BY v.id
    ''', (variant_id,)).fetchone()
    
    if variant:
        # Convert to dictionary
        variant_dict = dict(variant)
        
        # Check if symptoms and treatments are empty or None
        has_symptoms = variant_dict.get('symptoms') is not None and variant_dict.get('symptoms') != ''
        has_treatments = variant_dict.get('treatments') is not None and variant_dict.get('treatments') != ''
        
        # Set symptoms and treatments based on availability
        if has_symptoms:
            symptoms = variant_dict['symptoms'].split(',')
        else:
            symptoms = ['No symptoms data available']
            
        if has_treatments:
            treatments = variant_dict['treatments'].split(',')
        else:
            treatments = ['No treatments data available']
        
        # Check if variant has any meaningful information
        has_info = has_symptoms or has_treatments
        
        return jsonify({
            'found': True,
            'variant': variant_dict,
            'symptoms': symptoms,
            'treatments': treatments,
            'no_info': not has_info
        })
    else:
        return jsonify({'found': False})

@app.route('/variant_suggestions')
def variant_suggestions():
    query = request.args.get('term', '')
    conn = get_db_connection()
    
    # Search for variants that match the query
    variants = conn.execute('''
        SELECT DISTINCT gnomad_id, clinvar_classification
        FROM variants
        WHERE gnomad_id LIKE ? OR clinvar_classification LIKE ?
        LIMIT 10
    ''', (f'%{query}%', f'%{query}%')).fetchall()
    
    # Format suggestions with label and value
    suggestions = [{
        'label': f"{v['gnomad_id']} ({v['clinvar_classification'] or 'No classification'})",
        'value': v['gnomad_id']
    } for v in variants]
    
    return jsonify(suggestions)

@app.route('/search_by_symptoms', methods=['POST'])
def search_by_symptoms():
    selected_symptoms = request.form.getlist('symptoms[]')
    conn = get_db_connection()
    
    # Get variants that match the selected symptoms
    variants = conn.execute('''
        SELECT v.gnomad_id, v.clinvar_classification,
               GROUP_CONCAT(DISTINCT s.name) as matching_symptoms,
               COUNT(DISTINCT s.id) as symptom_match_count
        FROM variants v
        JOIN variant_symptoms vs ON v.id = vs.variant_id
        JOIN symptoms s ON vs.symptom_id = s.id
        WHERE s.name IN ({})
        GROUP BY v.id
        HAVING symptom_match_count >= ?
        ORDER BY symptom_match_count DESC
        LIMIT 5
    '''.format(','.join('?' * len(selected_symptoms))), 
    selected_symptoms + [len(selected_symptoms)//2]).fetchall()
    
    return jsonify([dict(v) for v in variants])

@app.route('/get_symptoms')
def get_symptoms():
    conn = get_db_connection()
    symptoms = conn.execute('''
        SELECT s.*, COUNT(vs.variant_id) as variant_count
        FROM symptoms s
        LEFT JOIN variant_symptoms vs ON s.id = vs.symptom_id
        GROUP BY s.id
        ORDER BY s.category, s.name
    ''').fetchall()
    return jsonify([dict(s) for s in symptoms])

@app.route('/get_treatments')
def get_treatments():
    conn = get_db_connection()
    treatments = conn.execute('SELECT * FROM treatments ORDER BY type').fetchall()
    return jsonify([dict(t) for t in treatments])

if __name__ == '__main__':
    app.run(debug=True) 