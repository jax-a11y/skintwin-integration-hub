"""
Database seeding script for E2E tests.
Creates test data for comprehensive E2E testing.
"""
import os
import sys

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

def seed_database():
    """Seed the database with test data."""
    os.environ.setdefault('DATABASE_URL', 'sqlite:///instance/e2e_test.db')
    os.environ.setdefault('FLASK_SECRET_KEY', 'e2e-seed-key')
    
    from flask import Flask
    from database import db_sql
    from database_models import User
    from werkzeug.security import generate_password_hash
    from datetime import datetime, timedelta
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'e2e-seed'
    
    db_sql.init_app(app)
    
    with app.app_context():
        # Create all tables
        db_sql.create_all()
        
        # Clear existing test data
        User.query.filter(User.email.like('%@test.com')).delete()
        db_sql.session.commit()
        
        # Create admin user
        admin = User(
            username='TestAdmin',
            email='admin@test.com',
            password_hash=generate_password_hash('TestPassword123!'),
            is_admin=True,
            is_staff=True
        )
        db_sql.session.add(admin)
        
        # Create staff user
        staff = User(
            username='TestStaff',
            email='staff@test.com',
            password_hash=generate_password_hash('TestPassword123!'),
            is_admin=False,
            is_staff=True
        )
        db_sql.session.add(staff)
        
        # Create regular user
        regular = User(
            username='TestUser',
            email='user@test.com',
            password_hash=generate_password_hash('TestPassword123!'),
            is_admin=False,
            is_staff=False
        )
        db_sql.session.add(regular)
        
        db_sql.session.commit()
        print("✓ Users created")
        
        # Try to create clients if model exists
        try:
            from database_models import Client
            
            Client.query.filter(Client.email.like('%@testclient.com')).delete()
            db_sql.session.commit()
            
            for i in range(5):
                client = Client(
                    name=f'Test Client {i+1}',
                    email=f'client{i+1}@testclient.com',
                    phone=f'555-000-{1000+i}',
                    loyalty_points=i * 100
                )
                db_sql.session.add(client)
            
            db_sql.session.commit()
            print("✓ Clients created")
        except ImportError:
            print("⚠ Client model not available")
        except Exception as e:
            print(f"⚠ Could not create clients: {e}")
            db_sql.session.rollback()
        
        # Try to create services if model exists
        try:
            from database_models import Service
            
            Service.query.filter(Service.name.like('Test %')).delete()
            db_sql.session.commit()
            
            services = [
                ('Test Haircut', 'Basic haircut service', 30.00, 30),
                ('Test Color', 'Hair coloring service', 80.00, 90),
                ('Test Treatment', 'Hair treatment service', 50.00, 45),
                ('Test Styling', 'Hair styling service', 40.00, 30),
            ]
            
            for name, desc, price, duration in services:
                service = Service(
                    name=name,
                    description=desc,
                    price=price,
                    duration=duration
                )
                db_sql.session.add(service)
            
            db_sql.session.commit()
            print("✓ Services created")
        except ImportError:
            print("⚠ Service model not available")
        except Exception as e:
            print(f"⚠ Could not create services: {e}")
            db_sql.session.rollback()
        
        # Try to create appointments if model exists
        try:
            from database_models import Appointment
            
            # Get first client and service
            client = Client.query.first() if 'Client' in dir() else None
            service = Service.query.first() if 'Service' in dir() else None
            
            if client and service:
                Appointment.query.filter(Appointment.notes.like('%Test appointment%')).delete()
                db_sql.session.commit()
                
                for i in range(3):
                    apt_date = datetime.now() + timedelta(days=i+1)
                    appointment = Appointment(
                        client_id=client.id,
                        service_id=service.id,
                        staff_id=staff.id if staff else admin.id,
                        date_time=apt_date,
                        status='scheduled',
                        notes=f'Test appointment {i+1}'
                    )
                    db_sql.session.add(appointment)
                
                db_sql.session.commit()
                print("✓ Appointments created")
        except ImportError:
            print("⚠ Appointment model not available")
        except Exception as e:
            print(f"⚠ Could not create appointments: {e}")
            db_sql.session.rollback()
        
        # Try to create inventory/products if model exists
        try:
            from database_models import Product
            
            Product.query.filter(Product.name.like('Test Product%')).delete()
            db_sql.session.commit()
            
            products = [
                ('Test Product 1', 'Test product description', 19.99, 50),
                ('Test Product 2', 'Another test product', 29.99, 30),
                ('Test Product 3', 'Yet another product', 9.99, 100),
            ]
            
            for name, desc, price, qty in products:
                product = Product(
                    name=name,
                    description=desc,
                    price=price,
                    quantity=qty
                )
                db_sql.session.add(product)
            
            db_sql.session.commit()
            print("✓ Products created")
        except ImportError:
            print("⚠ Product model not available")
        except Exception as e:
            print(f"⚠ Could not create products: {e}")
            db_sql.session.rollback()
        
        print("\n✅ Database seeding complete!")


if __name__ == '__main__':
    seed_database()
