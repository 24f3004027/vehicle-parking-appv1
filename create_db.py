from datetime import datetime, timedelta, timezone
from app import app, db, User, ParkingLot, ParkingSpot, Reservation

def init_db():
    # Reset database schema
    db.drop_all()
    db.create_all()

    print("Creating initial users...")
    # Admin User
    admin = User(username="admin", email="admin@parking.app", role="admin")
    admin.set_password("admin123")

    # Regular Users
    ramrup = User(username="ramrup", email="ramrup@iitm.ac.in", role="user")
    ramrup.set_password("user123")

    demo_user = User(username="johndoe", email="john@example.com", role="user")
    demo_user.set_password("user123")

    db.session.add_all([admin, ramrup, demo_user])
    db.session.commit()

    print("Creating sample parking lots and spots...")
    lots_data = [
        {
            "name": "IIT Madras Academic Complex",
            "address": "Sardar Patel Road, Guindy, Chennai",
            "pin_code": "600036",
            "total_spots": 12,
            "price_per_hour": 30.0
        },
        {
            "name": "Phoenix Marketcity Parking Garage",
            "address": "Velachery Main Rd, Near Check Post, Chennai",
            "pin_code": "600042",
            "total_spots": 15,
            "price_per_hour": 60.0
        },
        {
            "name": "Chennai International Airport T2",
            "address": "GST Road, Meenambakkam, Chennai",
            "pin_code": "600027",
            "total_spots": 20,
            "price_per_hour": 100.0
        }
    ]

    created_lots = []
    for lot_info in lots_data:
        lot = ParkingLot(**lot_info)
        db.session.add(lot)
        db.session.commit()
        created_lots.append(lot)

        # Generate spots for each lot
        for i in range(1, lot.total_spots + 1):
            spot = ParkingSpot(lot_id=lot.id, spot_number=f"P{lot.id}-{i:02d}", status='A')
            db.session.add(spot)
        db.session.commit()

    print("Creating sample active and historical parking sessions...")
    # Get spots for seeding
    spot_iitm_1 = ParkingSpot.query.filter_by(lot_id=created_lots[0].id, spot_number="P1-01").first()
    spot_phoenix_1 = ParkingSpot.query.filter_by(lot_id=created_lots[1].id, spot_number="P2-01").first()
    spot_phoenix_2 = ParkingSpot.query.filter_by(lot_id=created_lots[1].id, spot_number="P2-02").first()

    now = datetime.now(timezone.utc)

    # Active Parking for Ramrup
    if spot_iitm_1:
        spot_iitm_1.status = 'O'
        active_res = Reservation(
            spot_id=spot_iitm_1.id,
            user_id=ramrup.id,
            vehicle_number="TN 07 BS 2026",
            vehicle_type="EV",
            parking_timestamp=now - timedelta(hours=2, minutes=15),
            status='ACTIVE'
        )
        db.session.add(active_res)

    # Active Parking for John Doe
    if spot_phoenix_1:
        spot_phoenix_1.status = 'O'
        active_res_2 = Reservation(
            spot_id=spot_phoenix_1.id,
            user_id=demo_user.id,
            vehicle_number="TN 09 AB 4321",
            vehicle_type="SUV",
            parking_timestamp=now - timedelta(minutes=45),
            status='ACTIVE'
        )
        db.session.add(active_res_2)

    # Completed Historical Parking for Ramrup
    if spot_phoenix_2:
        completed_res = Reservation(
            spot_id=spot_phoenix_2.id,
            user_id=ramrup.id,
            vehicle_number="TN 07 BS 2026",
            vehicle_type="EV",
            parking_timestamp=now - timedelta(days=1, hours=4),
            leaving_timestamp=now - timedelta(days=1, hours=1),
            parking_cost=180.0,
            status='COMPLETED'
        )
        db.session.add(completed_res)

    db.session.commit()
    print("Database successfully seeded with realistic sample data!")
    print("-----------------------------------------------------")
    print("Admin Login:    username: admin   | password: admin123")
    print("User Login:     username: ramrup  | password: user123")
    print("-----------------------------------------------------")

    db.session.commit()
    print("Database successfully seeded with realistic sample data!")
    print("-----------------------------------------------------")
    print("Admin Login:    username: admin   | password: admin123")
    print("User Login:     username: ramrup  | password: user123")
    print("-----------------------------------------------------")

if __name__ == "__main__":
    with app.app_context():
        init_db()