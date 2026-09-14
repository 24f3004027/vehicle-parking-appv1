import anvil.server
import math
from datetime import datetime, timezone

# In-memory / data structure simulation for Anvil server
USERS_DB = [
    {"id": 1, "username": "admin", "password": "admin123", "role": "admin"},
    {"id": 2, "username": "ramrup", "password": "user123", "role": "user"}
]

LOTS_DB = [
    {
        "id": 1,
        "name": "IIT Madras Academic Complex",
        "address": "Sardar Patel Road, Guindy, Chennai",
        "pin_code": "600036",
        "total_spots": 12,
        "price_per_hour": 30.0
    },
    {
        "id": 2,
        "name": "Phoenix Marketcity Parking Garage",
        "address": "Velachery Main Rd, Chennai",
        "pin_code": "600042",
        "total_spots": 15,
        "price_per_hour": 60.0
    }
]

SPOTS_DB = []
for i in range(1, 13):
    SPOTS_DB.append({"id": i, "lot_id": 1, "spot_number": f"P1-{i:02d}", "status": "A"})
for i in range(1, 16):
    SPOTS_DB.append({"id": 12 + i, "lot_id": 2, "spot_number": f"P2-{i:02d}", "status": "A"})

# Pre-occupy spot P1-01 for demo
SPOTS_DB[0]["status"] = "O"

RESERVATIONS_DB = [
    {
        "id": 1,
        "spot_id": 1,
        "user_id": 2,
        "vehicle_number": "TN 07 BS 2026",
        "vehicle_type": "EV",
        "parking_timestamp": datetime.now(timezone.utc).isoformat(),
        "leaving_timestamp": None,
        "parking_cost": None,
        "status": "ACTIVE"
    }
]

@anvil.server.callable
def login_user(username, password):
    for u in USERS_DB:
        if u["username"] == username and u["password"] == password:
            return {"success": True, "user_id": u["id"], "username": u["username"], "role": u["role"]}
    return {"success": False, "message": "Invalid credentials"}

@anvil.server.callable
def get_parking_lots(search_query=None):
    result = []
    for lot in LOTS_DB:
        if search_query:
            sq = search_query.lower()
            if sq not in lot["name"].lower() and sq not in lot["address"].lower() and sq not in lot["pin_code"]:
                continue

        # Count available and occupied spots
        spots = [s for s in SPOTS_DB if s["lot_id"] == lot["id"]]
        avail = sum(1 for s in spots if s["status"] == "A")
        occ = sum(1 for s in spots if s["status"] == "O")

        result.append({
            "id": lot["id"],
            "name": lot["name"],
            "address": lot["address"],
            "pin_code": lot["pin_code"],
            "total_spots": lot["total_spots"],
            "price_per_hour": lot["price_per_hour"],
            "available_spots": avail,
            "occupied_spots": occ
        })
    return result

@anvil.server.callable
def get_lot_spots(lot_id):
    spots = [s for s in SPOTS_DB if s["lot_id"] == lot_id]
    active_res = {r["spot_id"]: r for r in RESERVATIONS_DB if r["status"] == "ACTIVE"}
    
    result = []
    for s in spots:
        res = active_res.get(s["id"])
        result.append({
            "id": s["id"],
            "spot_number": s["spot_number"],
            "status": s["status"],
            "vehicle_number": res["vehicle_number"] if res else None,
            "vehicle_type": res["vehicle_type"] if res else None
        })
    return result

@anvil.server.callable
def park_vehicle(user_id, lot_id, vehicle_number, vehicle_type, spot_id=None):
    # Check active parking
    existing = [r for r in RESERVATIONS_DB if r["user_id"] == user_id and r["status"] == "ACTIVE"]
    if existing:
        return {"success": False, "message": "You already have an active parking session!"}

    target_spot = None
    if spot_id:
        target_spot = next((s for s in SPOTS_DB if s["id"] == spot_id and s["status"] == "A"), None)
    else:
        target_spot = next((s for s in SPOTS_DB if s["lot_id"] == lot_id and s["status"] == "A"), None)

    if not target_spot:
        return {"success": False, "message": "No available parking spot."}

    target_spot["status"] = "O"
    new_res = {
        "id": len(RESERVATIONS_DB) + 1,
        "spot_id": target_spot["id"],
        "user_id": user_id,
        "vehicle_number": vehicle_number,
        "vehicle_type": vehicle_type,
        "parking_timestamp": datetime.now(timezone.utc).isoformat(),
        "leaving_timestamp": None,
        "parking_cost": None,
        "status": "ACTIVE"
    }
    RESERVATIONS_DB.append(new_res)
    return {"success": True, "spot_number": target_spot["spot_number"], "reservation_id": new_res["id"]}

@anvil.server.callable
def checkout_vehicle(reservation_id):
    res = next((r for r in RESERVATIONS_DB if r["id"] == reservation_id), None)
    if not res:
        return {"success": False, "message": "Reservation not found."}

    if res["status"] == "COMPLETED":
        return {"success": True, "cost": res["parking_cost"]}

    now = datetime.now(timezone.utc)
    res["leaving_timestamp"] = now.isoformat()

    start_t = datetime.fromisoformat(res["parking_timestamp"])
    duration_secs = (now - start_t).total_seconds()
    hours = max(1.0, math.ceil(duration_secs / 3600.0))

    spot = next((s for s in SPOTS_DB if s["id"] == res["spot_id"]), None)
    lot = next((l for l in LOTS_DB if l["id"] == spot["lot_id"]), None) if spot else None

    rate = lot["price_per_hour"] if lot else 50.0
    cost = round(hours * rate, 2)
    res["parking_cost"] = cost
    res["status"] = "COMPLETED"

    if spot:
        spot["status"] = "A"

    return {"success": True, "cost": cost, "duration_hours": hours}

@anvil.server.callable
def get_user_history(user_id):
    user_res = [r for r in RESERVATIONS_DB if r["user_id"] == user_id]
    result = []
    for r in user_res:
        spot = next((s for s in SPOTS_DB if s["id"] == r["spot_id"]), None)
        lot = next((l for l in LOTS_DB if l["id"] == spot["lot_id"]), None) if spot else None
        result.append({
            "id": r["id"],
            "lot_name": lot["name"] if lot else "Unknown",
            "spot_number": spot["spot_number"] if spot else "N/A",
            "vehicle_number": r["vehicle_number"],
            "parking_timestamp": r["parking_timestamp"],
            "leaving_timestamp": r["leaving_timestamp"],
            "parking_cost": r["parking_cost"],
            "status": r["status"]
        })
    return result
