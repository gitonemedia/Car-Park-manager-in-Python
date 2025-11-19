class CarPark:
    def __init__(self, capacity):
        self.capacity = capacity
        self.parked_cars = {}
        # parked_cars maps spot -> { 'plate': str, 'time_in': iso str }
        self.parked_cars = {}
        # transactions: list of dicts with spot, plate, time_in, time_out, amount, paid
        self.transactions = []
        # rate per hour for computing amount
        self.rate_per_hour = 2.0
        # timezone for timestamps (GMT+7)
        from datetime import timezone, timedelta
        self.tz = timezone(timedelta(hours=7))

    def park_car(self, license_plate):
        if len(self.parked_cars) < self.capacity:
            # choose the lowest available spot between 1..capacity
            for spot in range(1, self.capacity + 1):
                if spot not in self.parked_cars:
                    from datetime import datetime
                    now = datetime.now(self.tz).isoformat()
                    self.parked_cars[spot] = {'plate': license_plate, 'time_in': now, 'comments': ''}
                    print(f"✓ Car {license_plate} parked at spot {spot}")
                    return True
            # fallback (shouldn't happen): no spot found
            print("✗ Car park is full!")
            return False
        else:
            print("✗ Car park is full!")
            return False

    def remove_car(self, spot):
        if spot in self.parked_cars:
            rec = self.parked_cars.pop(spot)
            plate = rec.get('plate')
            time_in_str = rec.get('time_in')
            from datetime import datetime
            time_out = datetime.now(self.tz).isoformat()

            # compute amount based on elapsed time
            try:
                from datetime import datetime as _dt
                t_in = _dt.fromisoformat(time_in_str)
                t_out = _dt.fromisoformat(time_out)
                seconds = (t_out - t_in).total_seconds()
                hours = seconds / 3600.0
                amount = round(hours * self.rate_per_hour, 2)
            except Exception:
                amount = 0.0

            transaction = {
                'spot': spot,
                'plate': plate,
                'time_in': time_in_str,
                'time_out': time_out,
                'amount': amount,
                'paid': False,
                'comments': '',
            }
            self.transactions.append(transaction)
            print(f"✓ Car {plate} removed from spot {spot}")
            return transaction
        else:
            print("✗ Invalid spot number")
            return False

    def view_cars(self):
        if not self.parked_cars:
            print("Car park is empty")
        else:
            print("\n--- Parked Cars ---")
            for spot in sorted(self.parked_cars):
                r = self.parked_cars[spot]
                print(f"Spot {spot}: {r.get('plate')} (in: {r.get('time_in')})")

    def available_spots(self):
        return self.capacity - len(self.parked_cars)

    def to_dict(self):
        # Convert parked_cars keys to strings for JSON compatibility
        return {
            'capacity': self.capacity,
            'parked_cars': {str(k): v for k, v in self.parked_cars.items()},
            'transactions': self.transactions,
            'rate_per_hour': self.rate_per_hour,
        }

    @classmethod
    def from_dict(cls, data):
        cap = int(data.get('capacity', 0))
        obj = cls(cap)
        parked = data.get('parked_cars', {})
        # keys may be strings when loaded from JSON
        obj.parked_cars = {int(k): v for k, v in parked.items()}
        obj.transactions = data.get('transactions', [])
        obj.rate_per_hour = float(data.get('rate_per_hour', obj.rate_per_hour))
        return obj

    def save_to_file(self, path):
        import json
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_file(cls, path):
        import json
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)

    def save_to_db(self, db_path='carpark.db'):
        """Save car park state to SQLite database."""
        import sqlite3
        import json
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # create tables if not exist
        c.execute('''CREATE TABLE IF NOT EXISTS carpark_state (
            id INTEGER PRIMARY KEY,
            capacity INTEGER,
            rate_per_hour REAL,
            parked_cars TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            spot INTEGER,
            plate TEXT,
            time_in TEXT,
            time_out TEXT,
            amount REAL,
            paid INTEGER,
            comments TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # clear and insert current state
        c.execute('DELETE FROM carpark_state')
        parked_cars_json = json.dumps({str(k): v for k, v in self.parked_cars.items()})
        c.execute('INSERT INTO carpark_state (capacity, rate_per_hour, parked_cars) VALUES (?, ?, ?)',
                  (self.capacity, self.rate_per_hour, parked_cars_json))
        
        # clear and insert transactions
        c.execute('DELETE FROM transactions')
        for tx in self.transactions:
            c.execute('INSERT INTO transactions (spot, plate, time_in, time_out, amount, paid, comments) VALUES (?, ?, ?, ?, ?, ?, ?)',
                      (tx.get('spot'), tx.get('plate'), tx.get('time_in'), tx.get('time_out'), 
                       tx.get('amount'), 1 if tx.get('paid') else 0, tx.get('comments', '')))
        
        conn.commit()
        conn.close()

    @classmethod
    def load_from_db(cls, db_path='carpark.db'):
        """Load car park state from SQLite database."""
        import sqlite3
        import json
        import os
        
        if not os.path.exists(db_path):
            return None
        
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # load state
        c.execute('SELECT capacity, rate_per_hour, parked_cars FROM carpark_state ORDER BY created_at DESC LIMIT 1')
        row = c.fetchone()
        
        if not row:
            conn.close()
            return None
        
        capacity, rate_per_hour, parked_cars_json = row
        obj = cls(capacity)
        obj.rate_per_hour = rate_per_hour
        
        # load parked cars
        try:
            parked_dict = json.loads(parked_cars_json)
            obj.parked_cars = {int(k): v for k, v in parked_dict.items()}
        except Exception:
            obj.parked_cars = {}
        
        # load transactions
        c.execute('SELECT spot, plate, time_in, time_out, amount, paid, comments FROM transactions ORDER BY created_at ASC')
        for row in c.fetchall():
            spot, plate, time_in, time_out, amount, paid, comments = row
            tx = {
                'spot': spot,
                'plate': plate,
                'time_in': time_in,
                'time_out': time_out,
                'amount': amount,
                'paid': bool(paid),
                'comments': comments or ''
            }
            obj.transactions.append(tx)
        
        conn.close()
        return obj


def main():
    park = CarPark(10)
    
    while True:
        print("\n1. Park Car\n2. Remove Car\n3. View Cars\n4. Available Spots\n5. Exit")
        choice = input("Select option: ").strip()

        # Normalize input: allow numbers, words, or full menu line like "2. Remove Car"
        if choice and choice[0].isdigit():
            choice = choice[0]
        else:
            lowered = choice.lower()
            # single-letter shortcuts
            shortcuts = {'p': '1', 'r': '2', 'v': '3', 'a': '4', 'q': '5'}
            if len(lowered) == 1 and lowered in shortcuts:
                choice = shortcuts[lowered]
            elif 'park' in lowered:
                choice = "1"
            elif 'remove' in lowered:
                choice = "2"
            elif 'view' in lowered:
                choice = "3"
            elif 'available' in lowered or 'spots' in lowered:
                choice = "4"
            elif 'exit' in lowered or 'quit' in lowered:
                choice = "5"

        if choice == "1":
            plate = input("Enter license plate: ").strip()
            park.park_car(plate)
        elif choice == "2":
            spot_input = input("Enter spot number: ").strip()
            try:
                spot = int(spot_input)
            except ValueError:
                print("✗ Please enter a valid spot number")
                continue
            park.remove_car(spot)
        elif choice == "3":
            park.view_cars()
        elif choice == "4":
            print(f"Available spots: {park.available_spots()}")
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid option")


if __name__ == "__main__":
    main()