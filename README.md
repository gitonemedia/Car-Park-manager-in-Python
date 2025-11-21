# Car Park Management System - Executable by One Media Asia Co, Ltd

## Quick Start

The executable `CarParkManager.exe` is located in the `dist` folder and can be run on any Windows system without needing Python installed.

### How to Run (Windows EXE)

1. Navigate to the `dist` folder
2. Double-click `CarParkManager.exe`
3. The Car Park Manager GUI will launch

### Distribution

You can copy the `CarParkManager.exe` file to any Windows computer and run it directly. The database file (`carpark.db`) will be created in the same directory as the executable.

### Features

- **Park & Remove Cars**: Track vehicles with timestamps (GMT+7 timezone)
- **Transaction History**: View all transactions with amounts and payment status
- **Editable Comments**: Add notes to each parked car (double-click to edit)
- **Database Storage**: All data persists in SQLite database
- **Search**: Find cars by license plate or spot number
- **Invoicing System**:
  - Print individual transaction invoices
  - Generate daily invoices with payment summaries
  - Direct printer support

### System Requirements

- Windows 7 or later
- No additional software needed (Python is bundled in the executable)

## New: Web Frontend (Flask)

You can now run the Car Park Manager as a lightweight web app that works on phones/tablets (including Android) via any modern browser.

### Setup

1. Install dependencies (preferably inside a virtual environment):
   ```bash
   pip install -r requirements.txt
   ```
2. Set an optional secret and/or database path:
   ```bash
   set FLASK_SECRET_KEY=replace-me
   set CARPARK_DB=C:\path\to\carpark.db
   ```
   (On macOS/Linux use `export` instead of `set`.)

3. Start the server:
   ```bash
   flask --app app run
   ```
   or
   ```bash
   python app.py
   ```

4. Open `http://localhost:5000` (or your LAN IP) on any browser/device. Sign in with the default admin account `admin/admin` (change this immediately via the Admin Tools panel).

### Features

- Same business logic as the desktop GUI (`practice.CarPark` + SQLite persistence)
- Login/logout with role-based access (admin vs standard users)
- Park/remove cars, view live occupancy, inspect recent transactions
- Removal modal lets you override parked hours and the final amount before checkout
- Quick search card filters parked cars by registration and pre-fills the remove modal
- Comments on parked cars can be edited inline via a dedicated modal
- Admin-only actions: set rate, create fresh car park, save/load SQLite snapshots, manage users via API endpoints
- Mobile-first responsive UI (PWA-ready)

### Securing a Deployment

- Always set a strong `FLASK_SECRET_KEY` before deploying.
- Serve behind HTTPS (e.g., reverse proxy with Nginx/Caddy or use a platform like Railway/Render).
- Put the app behind a VPN or firewall if exposing to the public internet.
- Regularly change the default admin password and create separate user accounts for operators.

### Data Files

The application creates a `carpark.db` file in the same directory. This file contains all your car park data and persists between sessions.

### Troubleshooting

If the executable doesn't run:
1. Ensure Windows Defender hasn't blocked it
2. Check that you have write permissions in the directory
3. Try running as Administrator

---

**Car Park Manager v1.0** - Professional parking lot management system | Copyright Peter Greaney @ One Media Asia Co, Ltd
