import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from create_database import Variant, Symptom, Treatment

# Load environment variables
load_dotenv()

# Create database engine
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///cftr_variants.db')
engine = create_engine(DATABASE_URL)

# Create session
Session = sessionmaker(bind=engine)
session = Session()

def enrich_variants_with_clinvar(clinvar_csv):
    """Add ClinVar classification data to variants."""
    df = pd.read_csv(clinvar_csv)
    
    for _, row in df.iterrows():
        variant = session.query(Variant).filter_by(gnomad_id=row['gnomad_id']).first()
        if variant:
            variant.clinvar_classification = row['clinvar_classification']
            variant.clinvar_review_status = row['clinvar_review_status']
    
    session.commit()

def enrich_variants_with_frequency(frequency_csv):
    """Add population frequency data to variants."""
    df = pd.read_csv(frequency_csv)
    
    for _, row in df.iterrows():
        variant = session.query(Variant).filter_by(gnomad_id=row['gnomad_id']).first()
        if variant:
            variant.population_frequency = row['population_frequency']
            variant.allele_count = row['allele_count']
            variant.allele_number = row['allele_number']
    
    session.commit()

def add_new_symptoms(symptoms_csv):
    """Add new symptoms to the database."""
    df = pd.read_csv(symptoms_csv)
    
    for _, row in df.iterrows():
        existing = session.query(Symptom).filter_by(name=row['name']).first()
        if not existing:
            symptom = Symptom(
                name=row['name'],
                category=row['category'],
                description=row['description']
            )
            session.add(symptom)
    
    session.commit()

def add_new_treatments(treatments_csv):
    """Add new treatments to the database."""
    df = pd.read_csv(treatments_csv)
    
    for _, row in df.iterrows():
        existing = session.query(Treatment).filter_by(name=row['name']).first()
        if not existing:
            treatment = Treatment(
                name=row['name'],
                type=row['type'],
                description=row['description']
            )
            session.add(treatment)
    
    session.commit()

def update_variant_associations(associations_csv):
    """Update associations between variants, symptoms, and treatments."""
    df = pd.read_csv(associations_csv)
    
    for _, row in df.iterrows():
        variant = session.query(Variant).filter_by(gnomad_id=row['gnomad_id']).first()
        if variant:
            # Update symptom associations
            if 'symptoms' in row:
                variant.symptoms = []
                symptom_names = row['symptoms'].split(',')
                for symptom_name in symptom_names:
                    symptom = session.query(Symptom).filter_by(name=symptom_name.strip()).first()
                    if symptom:
                        variant.symptoms.append(symptom)
            
            # Update treatment associations
            if 'treatments' in row:
                variant.treatments = []
                treatment_names = row['treatments'].split(',')
                for treatment_name in treatment_names:
                    treatment = session.query(Treatment).filter_by(name=treatment_name.strip()).first()
                    if treatment:
                        variant.treatments.append(treatment)
    
    session.commit()

def enrich_database():
    """Main function to enrich the database with additional data."""
    try:
        # Create data directory if it doesn't exist
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        # Enrich variants with ClinVar data
        enrich_variants_with_clinvar(os.path.join(data_dir, 'clinvar_data.csv'))
        
        # Enrich variants with frequency data
        enrich_variants_with_frequency(os.path.join(data_dir, 'frequency_data.csv'))
        
        # Add new symptoms
        add_new_symptoms(os.path.join(data_dir, 'new_symptoms.csv'))
        
        # Add new treatments
        add_new_treatments(os.path.join(data_dir, 'new_treatments.csv'))
        
        # Update variant associations
        update_variant_associations(os.path.join(data_dir, 'variant_associations.csv'))
        
        print("Database enriched successfully!")
        
    except Exception as e:
        session.rollback()
        print(f"Error enriching database: {str(e)}")
    finally:
        session.close()

if __name__ == '__main__':
    enrich_database() 