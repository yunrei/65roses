# CFTR Variant Information Web Application

This web application allows patients with CFTR variants to:
1. Search for their specific variant and get associated symptoms and treatments
2. Input their symptoms to find potentially matching variants
3. View detailed information about variants, symptoms, and treatments

## Project Structure

- `app.py` - The main Flask application
- `templates/index.html` - The web interface
- `cftr_variants.db` - The SQLite database with variant information
- `requirements.txt` - Dependencies for the application

## Setup and Installation

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the Flask application:
   ```
   python app.py
   ```

3. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

## Features

- **Variant Search**: Enter your CFTR variant ID to get associated symptoms and treatments
- **Symptom Search**: Select your symptoms to find potentially matching variants
- **Comprehensive Database**: Contains information about 5,883 CFTR variants
- **Modern UI**: Responsive design that works on all devices

## Database Information

The database includes:
- Variant information (gnomAD ID, clinical classification, etc.)
- Common CF symptoms across 8 categories
- Available treatments with effectiveness ratings
- Population-specific allele frequencies

## Development

This application was developed using:
- Flask for the backend
- SQLite for the database
- Bootstrap 5 for the frontend
- jQuery and Select2 for enhanced UI interactions