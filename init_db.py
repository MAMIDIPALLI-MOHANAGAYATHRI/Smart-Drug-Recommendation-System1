"""
Initialize Database with Sample Data
"""

from app import app, db
from models import Drug, DrugInteraction, DrugFoodInteraction
import pandas as pd

def init_database():
    """Initialize database and populate with data"""
    
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("✓ Tables created successfully")
        
        # Check if data already exists
        if Drug.query.first():
            print("⚠ Database already contains data. Skipping initialization.")
            return
        
        # Load drugs from CSV
        print("\nLoading drugs from CSV...")
        try:
            drugs_df = pd.read_csv('data/medicines.csv')
            
            for _, row in drugs_df.iterrows():
                drug = Drug(
                    drug_name=row['drug_name'],
                    category=row['category'],
                    age_min=row.get('age_min', 0),
                    age_max=row.get('age_max', 120),
                    kidney_safe=row.get('kidney_safe', 'YES'),
                    liver_safe=row.get('liver_safe', 'YES'),
                    pregnancy_safe=row.get('pregnancy_safe', 'YES')
                )
                db.session.add(drug)
            
            db.session.commit()
            print(f"✓ Added {len(drugs_df)} drugs")
        
        except Exception as e:
            print(f"✗ Error loading drugs: {str(e)}")
            db.session.rollback()
        
        # Load interactions from CSV
        print("\nLoading drug interactions...")
        try:
            interactions_df = pd.read_csv('data/interactions.csv')
            
            for _, row in interactions_df.iterrows():
                interaction = DrugInteraction(
                    drug1=row['drug1'],
                    drug2=row['drug2'],
                    severity=row['severity'],
                    description=f"Interaction between {row['drug1']} and {row['drug2']}"
                )
                db.session.add(interaction)
            
            db.session.commit()
            print(f"✓ Added {len(interactions_df)} drug interactions")
        
        except Exception as e:
            print(f"✗ Error loading interactions: {str(e)}")
            db.session.rollback()
        
        print("\n" + "="*60)
        print("DATABASE INITIALIZATION COMPLETE ✅")
        print("="*60)
        print(f"Drugs: {Drug.query.count()}")
        print(f"Interactions: {DrugInteraction.query.count()}")
        print("="*60)


if __name__ == '__main__':
    init_database()
