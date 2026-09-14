# 🚗 ParkSmart - Vehicle Parking Management System (v1.0)

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/Database-SQLite%20%2F%20SQLAlchemy-orange.svg)](https://www.sqlalchemy.org/)

**ParkSmart** is a modern, full-stack **Vehicle Parking Management System** built with **Flask**, **SQLAlchemy**, and a sleek **Dark Glassmorphism UI** (Bootstrap 5, FontAwesome 6, and Chart.js).

---

## ✨ Features

- **🔐 Role-Based Portals**:
  - **Admin Portal**: Manage parking lots, create & edit spots, monitor live vehicle occupancy across locations, view revenue metrics and visual utilization charts.
  - **User Portal**: Search nearby parking lots, check live available spot counts, park vehicles (Car, SUV, EV, Bike) with instant spot assignment, and check out with automated billing.
- **🗺️ Interactive Spot Grid**: Visual grid map displaying available (`Green`) vs occupied (`Red`) parking spots.
- **⏱️ Automated Duration & Billing Engine**: Real-time hourly tariff calculation with instant printable invoice receipts.
- **🎨 Glassmorphism UI**: High-contrast, dark-mode glassmorphism interface.

---

## 🚀 Quick Start

### 1. Clone & Navigate
```bash
git clone git@github.com:24f3004027/vehicle-parking-appv1.git
cd vehicle-parking-appv1
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize / Seed Database
```bash
python create_db.py
```

### 4. Run Flask Server
```bash
python app.py
```
Open [http://127.0.0.1:5001](http://127.0.0.1:5001) in your browser.

---

## 🔑 Demo Login Credentials

| Role | Username | Password | Access Rights |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` | Dashboard, Lot Creation, Analytics, Live Occupancy |
| **Standard User** | `ramrup` | `user123` | Spot Search, Vehicle Parking, Check-Out, Receipts |

---

## 🯅 License

𯅅 Copyleft Ramrup Satpati (24f3004027) | IIT Madras | Released under the [GNU General Public License v3.0](LICENSE).
All rights reversed.
