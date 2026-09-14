import os
import math
from datetime import datetime, timezone
from functools import wraps
from flask import Flask, render_template, request, url_for, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-vehicle-parking-2026'

# Flask-SQLAlchemy 3 standard relative SQLite URI (resolves to instance/vehicle_parking.sqlite3)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vehicle_parking.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -----------------------------------------------------------------------------
# Database Models
# -----------------------------------------------------------------------------

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # 'admin' or 'user'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class ParkingLot(db.Model):
    __tablename__ = 'parking_lots'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    total_spots = db.Column(db.Integer, nullable=False, default=10)
    price_per_hour = db.Column(db.Float, nullable=False, default=50.0)

    spots = db.relationship('ParkingSpot', backref='lot', cascade='all, delete-orphan', lazy=True)

    @property
    def available_spots_count(self):
        return ParkingSpot.query.filter_by(lot_id=self.id, status='A').count()

    @property
    def occupied_spots_count(self):
        return ParkingSpot.query.filter_by(lot_id=self.id, status='O').count()

    @property
    def occupancy_rate(self):
        if self.total_spots == 0:
            return 0
        return round((self.occupied_spots_count / self.total_spots) * 100, 1)

class ParkingSpot(db.Model):
    __tablename__ = 'parking_spots'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lots.id'), nullable=False)
    spot_number = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(5), nullable=False, default='A')  # 'A': Available, 'O': Occupied, 'R': Reserved

    reservations = db.relationship('Reservation', backref='spot', lazy=True)

class Reservation(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spots.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vehicle_number = db.Column(db.String(30), nullable=False)
    vehicle_type = db.Column(db.String(20), nullable=False, default='Car')  # Car, Bike, EV, SUV
    parking_timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    leaving_timestamp = db.Column(db.DateTime, nullable=True)
    parking_cost = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='ACTIVE')  # ACTIVE, COMPLETED

    user = db.relationship('User', backref='reservations', lazy=True)

    @property
    def duration_hours(self):
        end_time = self.leaving_timestamp or datetime.now(timezone.utc)
        p_time = self.parking_timestamp
        if p_time.tzinfo is None and end_time.tzinfo is not None:
            p_time = p_time.replace(tzinfo=timezone.utc)
        duration = end_time - p_time
        hours = duration.total_seconds() / 3600.0
        return max(1.0, round(hours, 2))

# -----------------------------------------------------------------------------
# Auth Helpers & Decorators
# -----------------------------------------------------------------------------

def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        return db.session.get(User, user_id)
    return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user or user.role != 'admin':
            flash('Admin authorization required.', 'danger')
            return redirect(url_for('user_dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_user():
    return dict(current_user=get_current_user())

# -----------------------------------------------------------------------------
# DB Auto-Initialization & Seeding Hook
# -----------------------------------------------------------------------------

def perform_seeding():
    print("Auto-seeding initial database...")
    admin = User(username="admin", email="admin@parking.app", role="admin")
    admin.set_password("admin123")

    ramrup = User(username="ramrup", email="ramrup@iitm.ac.in", role="user")
    ramrup.set_password("user123")

    db.session.add_all([admin, ramrup])
    db.session.commit()

    # Seed sample lots
    lot1 = ParkingLot(name="IIT Madras Academic Complex", address="Sardar Patel Road, Guindy, Chennai", pin_code="600036", total_spots=12, price_per_hour=30.0)
    lot2 = ParkingLot(name="Phoenix Marketcity Parking Garage", address="Velachery Main Rd, Chennai", pin_code="600042", total_spots=15, price_per_hour=60.0)
    db.session.add_all([lot1, lot2])
    db.session.commit()

    for i in range(1, 13):
        spot = ParkingSpot(lot_id=lot1.id, spot_number=f"P1-{i:02d}", status='A')
        db.session.add(spot)
    for i in range(1, 16):
        spot = ParkingSpot(lot_id=lot2.id, spot_number=f"P2-{i:02d}", status='A')
        db.session.add(spot)
    db.session.commit()
    print("Auto-seeding complete! Default credentials: admin / admin123 and ramrup / user123")

@app.before_request
def ensure_db_ready():
    if not getattr(app, '_db_initialized', False):
        db.create_all()
        try:
            if User.query.count() == 0:
                perform_seeding()
        except Exception:
            db.session.rollback()
            db.create_all()
            if User.query.count() == 0:
                perform_seeding()
        app._db_initialized = True

@app.route('/favicon.ico')
def favicon():
    return '', 204

# -----------------------------------------------------------------------------
# Routes - General & Auth
# -----------------------------------------------------------------------------

@app.route('/')
def index():
    user = get_current_user()
    if user:
        if user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('user_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if get_current_user():
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['role'] = user.role
            flash(f'Welcome back, {user.username}!', 'success')
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('user_dashboard'))

        flash('Invalid username or password.', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if get_current_user():
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        role = request.form.get('role', 'user')

        if not username or not email or not password:
            flash('All fields are required.', 'warning')
            return render_template('register.html')

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Username or Email already registered.', 'danger')
            return render_template('register.html')

        new_user = User(username=username, email=email, role=role if role in ['user', 'admin'] else 'user')
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# -----------------------------------------------------------------------------
# Routes - Admin Operations
# -----------------------------------------------------------------------------

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    lots = ParkingLot.query.all()
    total_lots = len(lots)
    total_spots = db.session.query(db.func.sum(ParkingLot.total_spots)).scalar() or 0
    occupied_spots = ParkingSpot.query.filter_by(status='O').count()
    available_spots = ParkingSpot.query.filter_by(status='A').count()

    total_revenue = db.session.query(db.func.sum(Reservation.parking_cost)).filter(Reservation.status == 'COMPLETED').scalar() or 0.0

    recent_reservations = Reservation.query.order_by(Reservation.parking_timestamp.desc()).limit(8).all()

    return render_template('admin_dashboard.html',
                           lots=lots,
                           total_lots=total_lots,
                           total_spots=total_spots,
                           occupied_spots=occupied_spots,
                           available_spots=available_spots,
                           total_revenue=total_revenue,
                           recent_reservations=recent_reservations)

@app.route('/admin/lot/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_lot():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        address = request.form.get('address', '').strip()
        pin_code = request.form.get('pin_code', '').strip()
        try:
            total_spots = int(request.form.get('total_spots', 10))
            price_per_hour = float(request.form.get('price_per_hour', 50.0))
        except ValueError:
            flash('Invalid numbers for spots or price.', 'danger')
            return render_template('create_lot.html')

        if not name or not address or not pin_code:
            flash('Please fill in all required fields.', 'warning')
            return render_template('create_lot.html')

        new_lot = ParkingLot(name=name, address=address, pin_code=pin_code,
                             total_spots=total_spots, price_per_hour=price_per_hour)
        db.session.add(new_lot)
        db.session.commit()

        # Generate spots automatically (P1-1, P1-2, etc.)
        for i in range(1, total_spots + 1):
            spot = ParkingSpot(lot_id=new_lot.id, spot_number=f"P{new_lot.id}-{i:02d}", status='A')
            db.session.add(spot)

        db.session.commit()
        flash(f'Parking Lot "{name}" created with {total_spots} spots!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('create_lot.html')

@app.route('/admin/lot/<int:lot_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_lot(lot_id):
    lot = db.session.get(ParkingLot, lot_id)
    if not lot:
        flash('Parking lot not found.', 'danger')
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        lot.name = request.form.get('name', '').strip()
        lot.address = request.form.get('address', '').strip()
        lot.pin_code = request.form.get('pin_code', '').strip()
        try:
            new_price = float(request.form.get('price_per_hour', lot.price_per_hour))
            lot.price_per_hour = new_price
        except ValueError:
            flash('Invalid price input.', 'danger')
            return render_template('edit_lot.html', lot=lot)

        db.session.commit()
        flash(f'Parking Lot "{lot.name}" updated successfully.', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_lot.html', lot=lot)

@app.route('/admin/lot/<int:lot_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_lot(lot_id):
    lot = db.session.get(ParkingLot, lot_id)
    if not lot:
        flash('Parking lot not found.', 'danger')
        return redirect(url_for('admin_dashboard'))

    active_in_lot = db.session.query(Reservation).join(ParkingSpot).filter(
        ParkingSpot.lot_id == lot_id,
        Reservation.status == 'ACTIVE'
    ).count()

    if active_in_lot > 0:
        flash(f'Cannot delete lot "{lot.name}" because there are active parked vehicles.', 'danger')
        return redirect(url_for('admin_dashboard'))

    db.session.delete(lot)
    db.session.commit()
    flash(f'Parking Lot "{lot.name}" deleted successfully.', 'info')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/lot/<int:lot_id>/spots')
@login_required
@admin_required
def lot_spots(lot_id):
    lot = db.session.get(ParkingLot, lot_id)
    if not lot:
        flash('Parking lot not found.', 'danger')
        return redirect(url_for('admin_dashboard'))

    spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
    active_reservations = {
        res.spot_id: res for res in Reservation.query.filter_by(status='ACTIVE').all()
    }

    return render_template('parking_spots.html', lot=lot, spots=spots, active_reservations=active_reservations)

@app.route('/admin/occupancy')
@login_required
@admin_required
def admin_occupancy():
    active_parkings = Reservation.query.filter_by(status='ACTIVE').order_by(Reservation.parking_timestamp.desc()).all()
    return render_template('admin_occupancy.html', active_parkings=active_parkings)

# -----------------------------------------------------------------------------
# Routes - User Operations
# -----------------------------------------------------------------------------

@app.route('/user/dashboard')
@login_required
def user_dashboard():
    user = get_current_user()
    active_reservation = Reservation.query.filter_by(user_id=user.id, status='ACTIVE').first()

    search_query = request.args.get('q', '').strip()
    if search_query:
        lots = ParkingLot.query.filter(
            (ParkingLot.name.ilike(f'%{search_query}%')) |
            (ParkingLot.address.ilike(f'%{search_query}%')) |
            (ParkingLot.pin_code.ilike(f'%{search_query}%'))
        ).all()
    else:
        lots = ParkingLot.query.all()

    return render_template('user_dashboard.html',
                           user=user,
                           active_reservation=active_reservation,
                           lots=lots,
                           search_query=search_query)

@app.route('/user/park/<int:lot_id>', methods=['GET', 'POST'])
@login_required
def park_vehicle(lot_id):
    user = get_current_user()
    lot = db.session.get(ParkingLot, lot_id)
    if not lot:
        flash('Parking lot not found.', 'danger')
        return redirect(url_for('user_dashboard'))

    existing_active = Reservation.query.filter_by(user_id=user.id, status='ACTIVE').first()
    if existing_active:
        flash('You already have an active parking session! Please check out before creating a new reservation.', 'warning')
        return redirect(url_for('user_dashboard'))

    available_spots = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').all()
    if not available_spots:
        flash(f'Sorry, no parking spots available at {lot.name}.', 'danger')
        return redirect(url_for('user_dashboard'))

    if request.method == 'POST':
        vehicle_number = request.form.get('vehicle_number', '').strip().upper()
        vehicle_type = request.form.get('vehicle_type', 'Car')
        spot_id = request.form.get('spot_id')

        if not vehicle_number:
            flash('Vehicle number / License plate is required.', 'warning')
            return render_template('park_vehicle.html', lot=lot, available_spots=available_spots)

        if spot_id:
            spot = ParkingSpot.query.filter_by(id=spot_id, lot_id=lot_id, status='A').first()
        else:
            spot = available_spots[0]

        if not spot:
            flash('Selected spot is no longer available.', 'danger')
            return redirect(url_for('park_vehicle', lot_id=lot_id))

        # Reserve spot
        spot.status = 'O'
        new_reservation = Reservation(
            spot_id=spot.id,
            user_id=user.id,
            vehicle_number=vehicle_number,
            vehicle_type=vehicle_type,
            parking_timestamp=datetime.now(timezone.utc),
            status='ACTIVE'
        )
        db.session.add(new_reservation)
        db.session.commit()

        flash(f'Vehicle {vehicle_number} parked successfully at Spot {spot.spot_number}!', 'success')
        return redirect(url_for('user_dashboard'))

    return render_template('park_vehicle.html', lot=lot, available_spots=available_spots)

@app.route('/user/checkout/<int:reservation_id>', methods=['POST'])
@login_required
def checkout_vehicle(reservation_id):
    user = get_current_user()
    reservation = db.session.get(Reservation, reservation_id)
    if not reservation:
        flash('Reservation not found.', 'danger')
        return redirect(url_for('user_dashboard'))

    if reservation.user_id != user.id and user.role != 'admin':
        flash('Unauthorized checkout attempt.', 'danger')
        return redirect(url_for('user_dashboard'))

    if reservation.status == 'COMPLETED':
        flash('This reservation is already completed.', 'info')
        return redirect(url_for('receipt', reservation_id=reservation.id))

    # Calculate parking fee
    now = datetime.now(timezone.utc)
    reservation.leaving_timestamp = now
    
    p_time = reservation.parking_timestamp
    if p_time.tzinfo is None:
        p_time = p_time.replace(tzinfo=timezone.utc)
    
    duration_secs = (now - p_time).total_seconds()
    duration_hours = max(1.0, math.ceil(duration_secs / 3600.0))
    
    hourly_rate = reservation.spot.lot.price_per_hour
    reservation.parking_cost = round(duration_hours * hourly_rate, 2)
    reservation.status = 'COMPLETED'

    spot = db.session.get(ParkingSpot, reservation.spot_id)
    if spot:
        spot.status = 'A'

    db.session.commit()

    flash(f'Vehicle {reservation.vehicle_number} checked out. Total bill: ₹{reservation.parking_cost:.2f}', 'success')
    return redirect(url_for('receipt', reservation_id=reservation.id))

@app.route('/user/receipt/<int:reservation_id>')
@login_required
def receipt(reservation_id):
    user = get_current_user()
    reservation = db.session.get(Reservation, reservation_id)
    if not reservation:
        flash('Reservation not found.', 'danger')
        return redirect(url_for('user_dashboard'))

    if reservation.user_id != user.id and user.role != 'admin':
        flash('Unauthorized view attempt.', 'danger')
        return redirect(url_for('user_dashboard'))

    return render_template('receipt.html', reservation=reservation)

@app.route('/user/history')
@login_required
def user_history():
    user = get_current_user()
    reservations = Reservation.query.filter_by(user_id=user.id).order_by(Reservation.parking_timestamp.desc()).all()
    return render_template('user_history.html', reservations=reservations)

# Initialize database schema on startup
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5001)