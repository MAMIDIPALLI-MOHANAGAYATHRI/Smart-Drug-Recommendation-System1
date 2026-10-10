from app import app, db
from models import User

with app.app_context():
    # Create users table
    db.create_all()
    print("✅ Users table created")
    
    # Create default admin user
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@smartrx.com',
            full_name='System Administrator',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✅ Default admin user created (username: admin, password: admin123)")