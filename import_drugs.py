"""
Import Extended Drug Database
Adds 50+ drugs to the database from CSV file
"""

from app import app, db
from models import Drug
import pandas as pd

def import_drugs_from_csv():
    """Import drugs from extended CSV file"""
    
    with app.app_context():
        try:
            # Read CSV file
            print("Reading drugs_extended.csv...")
            df = pd.read_csv('data/drugs_extended.csv')
            
            print(f"Found {len(df)} drugs in CSV file")
            
            # Clear existing drugs (optional - comment out to keep existing)
            # Drug.query.delete()
            # print("Cleared existing drugs")
            
            added_count = 0
            updated_count = 0
            
            for idx, row in df.iterrows():
                # Check if drug already exists
                existing_drug = Drug.query.filter(
                    Drug.drug_name.ilike(row['drug_name'])
                ).first()
                
                if existing_drug:
                    # Update existing drug
                    existing_drug.generic_name = row.get('generic_name')
                    existing_drug.brand_names = row.get('brand_names')
                    existing_drug.category = row['category']
                    existing_drug.drug_class = row.get('drug_class')
                    existing_drug.indication = row.get('indication')
                    existing_drug.mechanism_of_action = row.get('mechanism_of_action')
                    existing_drug.side_effects = row.get('side_effects')
                    existing_drug.dosage_forms = row.get('dosage_forms')
                    existing_drug.standard_dosage = row.get('standard_dosage')
                    existing_drug.max_daily_dose = row.get('max_daily_dose')
                    existing_drug.age_min = int(row.get('age_min', 0))
                    existing_drug.age_max = int(row.get('age_max', 120))
                    existing_drug.kidney_safe = row.get('kidney_safe', 'YES')
                    existing_drug.liver_safe = row.get('liver_safe', 'YES')
                    existing_drug.pregnancy_category = row.get('pregnancy_category')
                    existing_drug.pregnancy_safe = row.get('pregnancy_safe', 'YES')
                    existing_drug.price = float(row.get('price', 0))
                    existing_drug.prescription_required = str(row.get('prescription_required', 'TRUE')).upper() == 'TRUE'
                    
                    updated_count += 1
                else:
                    # Add new drug
                    drug = Drug(
                        drug_name=row['drug_name'],
                        generic_name=row.get('generic_name'),
                        brand_names=row.get('brand_names'),
                        category=row['category'],
                        drug_class=row.get('drug_class'),
                        indication=row.get('indication'),
                        mechanism_of_action=row.get('mechanism_of_action'),
                        side_effects=row.get('side_effects'),
                        dosage_forms=row.get('dosage_forms'),
                        standard_dosage=row.get('standard_dosage'),
                        max_daily_dose=row.get('max_daily_dose'),
                        age_min=int(row.get('age_min', 0)),
                        age_max=int(row.get('age_max', 120)),
                        kidney_safe=row.get('kidney_safe', 'YES'),
                        liver_safe=row.get('liver_safe', 'YES'),
                        pregnancy_category=row.get('pregnancy_category'),
                        pregnancy_safe=row.get('pregnancy_safe', 'YES'),
                        price=float(row.get('price', 0)),
                        prescription_required=str(row.get('prescription_required', 'TRUE')).upper() == 'TRUE'
                    )
                    db.session.add(drug)
                    added_count += 1
                
                # Commit every 10 drugs
                if (idx + 1) % 10 == 0:
                    db.session.commit()
                    print(f"Processed {idx + 1}/{len(df)} drugs...")
            
            # Final commit
            db.session.commit()
            
            print("\n" + "="*60)
            print("DRUG IMPORT COMPLETE ✅")
            print("="*60)
            print(f"✓ Added: {added_count} new drugs")
            print(f"✓ Updated: {updated_count} existing drugs")
            print(f"✓ Total in database: {Drug.query.count()} drugs")
            print("="*60)
            
        except Exception as e:
            print(f"✗ Error importing drugs: {str(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()


if __name__ == '__main__':
    import_drugs_from_csv()
