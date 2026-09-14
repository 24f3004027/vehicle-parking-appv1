# ⚡ ParkSmart - Anvil Web Application (`anvil/`)

This directory contains a full-stack **Anvil Application** (`anvil.works`) for **ParkSmart Vehicle Parking Management System** written 100% in Python (both client UI and server backend).

---

## ✨ Features

- **Pure-Python Architecture**: Client UI (`client_code/`) and Server API (`server_code/`) built entirely in Python.
- **Server Callable APIs**: `@anvil.server.callable` endpoints for authentication, live spot allocation, check-in, check-out billing, and history.
- **Glassmorphism CSS Theme**: Watery dark glass styling matching the main application.

---

## 🚀 How to Deploy on Anvil Cloud (`anvil.works`) — 100% Free

### Option A: Import via Git on Anvil.works
1. Log in to [Anvil.works](https://anvil.works) (Free Account).
2. Click **Create a new app** ➔ **Clone from Git**.
3. Paste your GitHub repository URL:
   ```text
   git@github.com:24f3004027/vehicle-parking-appv1.git
   ```
4. Point to the `anvil/` directory or push `anvil/` as the Anvil app root.
5. Click **Publish App** to get your free `.anvil.app` live web URL!

---

## 💻 Running Locally with Anvil App Server

Install the open-source Anvil App Server:
```bash
pip install anvil-app-server
anvil-app-server --app anvil/
```
Open [http://localhost:3030](http://localhost:3030) in your browser.

---

## 🔑 Demo Credentials

| Role | Username | Password |
| :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` |
| **User** | `ramrup` | `user123` |

---

## 🯅 License

𯅅 Copyleft Ramrup Satpati (24f3004027) | IIT Madras | Released under GNU GPLv3 License.
All rights reversed.
