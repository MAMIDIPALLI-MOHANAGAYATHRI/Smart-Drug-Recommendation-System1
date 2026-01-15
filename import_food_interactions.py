"""
Import Drug-Food Interactions Database
Phase 15.5 Implementation
"""

from app import app, db
from models import DrugFoodInteraction
import pandas as pd

def import_food_interactions():
    """Import drug-food interactions from CSV"""
    
    with app.app_context():
        try:
            print("Reading drug_food_interactions.csv...")
            df = pd.read_csv('data/drug_food_interactions.csv')
            
            print(f"Found {len(df)} drug-food interactions")
            
            # Clear existing interactions (optional)
            # DrugFoodInteraction.query.delete()
            
            added_count = 0
            
            for idx, row in df.iterrows():
                # Check if already exists
                existing = DrugFoodInteraction.query.filter_by(
                    drug_name=row['drug_name'],
                    food_item=row['food_item']
                ).first()
                
                if not existing:
                    interaction = DrugFoodInteraction(
                        drug_name=row['drug_name'],
                        food_item=row['food_item'],
                        interaction_type=row['interaction_type'],
                        severity=row['severity'],
                        description=row['description'],
                        recommendation=row['recommendation']
                    )
                    db.session.add(interaction)
                    added_count += 1
                
                if (idx + 1) % 10 == 0:
                    db.session.commit()
                    print(f"Processed {idx + 1}/{len(df)} interactions...")
            
            db.session.commit()
            
            print("\n" + "="*60)
            print("FOOD INTERACTION IMPORT COMPLETE ✅")
            print("="*60)
            print(f"✓ Added: {added_count} new interactions")
            print(f"✓ Total in database: {DrugFoodInteraction.query.count()} interactions")
            print("="*60)
            
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()


if __name__ == '__main__':
    import_food_interactions()
