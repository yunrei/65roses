import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from create_database import Base, Variant, Symptom, Treatment

# Load environment variables
load_dotenv()

# Create database engine
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///cftr_variants.db')
engine = create_engine(DATABASE_URL)

# Create session
Session = sessionmaker(bind=engine)
session = Session()

def load_variants_from_csv(csv_path):
    """Load variant data from CSV file."""
    df = pd.read_csv(csv_path)
    variants = []
    
    for _, row in df.iterrows():
        variant = Variant(
            gnomad_id=row['gnomad_id'],
            classification=row['classification'],
            population_frequency=row['population_frequency']
        )
        variants.append(variant)
    
    return variants

def load_symptoms_from_csv(csv_path):
    """Load symptom data from CSV file."""
    df = pd.read_csv(csv_path)
    symptoms = []
    
    for _, row in df.iterrows():
        symptom = Symptom(
            name=row['name'],
            category=row['category'],
            description=row['description']
        )
        symptoms.append(symptom)
    
    return symptoms

def load_treatments_from_csv(csv_path):
    """Load treatment data from CSV file."""
    df = pd.read_csv(csv_path)
    treatments = []
    
    for _, row in df.iterrows():
        treatment = Treatment(
            name=row['name'],
            type=row['type'],
            description=row['description']
        )
        treatments.append(treatment)
    
    return treatments

def create_variant_associations(variants_csv, symptoms_csv, treatments_csv):
    """Create associations between variants, symptoms, and treatments."""
    variants_df = pd.read_csv(variants_csv)
    symptoms_df = pd.read_csv(symptoms_csv)
    treatments_df = pd.read_csv(treatments_csv)
    
    # Create variant-symptom associations
    for _, row in variants_df.iterrows():
        variant = session.query(Variant).filter_by(gnomad_id=row['gnomad_id']).first()
        if variant and 'symptoms' in row:
            symptom_names = row['symptoms'].split(',')
            for symptom_name in symptom_names:
                symptom = session.query(Symptom).filter_by(name=symptom_name.strip()).first()
                if symptom:
                    variant.symptoms.append(symptom)
    
    # Create variant-treatment associations
    for _, row in variants_df.iterrows():
        variant = session.query(Variant).filter_by(gnomad_id=row['gnomad_id']).first()
        if variant and 'treatments' in row:
            treatment_names = row['treatments'].split(',')
            for treatment_name in treatment_names:
                treatment = session.query(Treatment).filter_by(name=treatment_name.strip()).first()
                if treatment:
                    variant.treatments.append(treatment)

def populate_database():
    """Main function to populate the database."""
    try:
        # Create data directory if it doesn't exist
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        # Load data from CSV files
        variants = load_variants_from_csv(os.path.join(data_dir, 'variants.csv'))
        symptoms = load_symptoms_from_csv(os.path.join(data_dir, 'symptoms.csv'))
        treatments = load_treatments_from_csv(os.path.join(data_dir, 'treatments.csv'))
        
        # Add all records to session
        session.add_all(variants)
        session.add_all(symptoms)
        session.add_all(treatments)
        
        # Commit to get IDs
        session.commit()
        
        # Create associations
        create_variant_associations(
            os.path.join(data_dir, 'variants.csv'), 
            os.path.join(data_dir, 'symptoms.csv'), 
            os.path.join(data_dir, 'treatments.csv')
        )
        
        # Final commit
        session.commit()
        print("Database populated successfully!")
        
    except Exception as e:
        session.rollback()
        print(f"Error populating database: {str(e)}")
    finally:
        session.close()

if __name__ == '__main__':
    populate_database() 