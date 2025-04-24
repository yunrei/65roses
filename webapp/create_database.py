from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create database engine
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///cftr_variants.db')
engine = create_engine(DATABASE_URL)

Base = declarative_base()

# Association tables
variant_symptoms = Table('variant_symptoms', Base.metadata,
    Column('variant_id', Integer, ForeignKey('variants.id')),
    Column('symptom_id', Integer, ForeignKey('symptoms.id'))
)

variant_treatments = Table('variant_treatments', Base.metadata,
    Column('variant_id', Integer, ForeignKey('variants.id')),
    Column('treatment_id', Integer, ForeignKey('treatments.id'))
)

class Variant(Base):
    __tablename__ = 'variants'
    
    id = Column(Integer, primary_key=True)
    gnomad_id = Column(String, unique=True, nullable=False)
    classification = Column(String)
    population_frequency = Column(Float)
    
    symptoms = relationship('Symptom', secondary=variant_symptoms, back_populates='variants')
    treatments = relationship('Treatment', secondary=variant_treatments, back_populates='variants')

class Symptom(Base):
    __tablename__ = 'symptoms'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    category = Column(String)
    description = Column(String)
    
    variants = relationship('Variant', secondary=variant_symptoms, back_populates='symptoms')

class Treatment(Base):
    __tablename__ = 'treatments'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    type = Column(String)
    description = Column(String)
    
    variants = relationship('Variant', secondary=variant_treatments, back_populates='variants')

def create_database():
    Base.metadata.create_all(engine)
    print("Database schema created successfully!")

if __name__ == '__main__':
    create_database() 