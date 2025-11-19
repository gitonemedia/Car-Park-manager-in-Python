from practice import CarPark

# Create a park and park a car
p = CarPark(5)
p.park_car('ABC123')

# Check if comments field exists
print("Parked cars:", p.parked_cars)

# Try to save to db
try:
    p.save_to_db('test.db')
    print("✓ Saved to database")
except Exception as e:
    print(f"✗ Save failed: {e}")
    import traceback
    traceback.print_exc()

# Try to load from db
try:
    p2 = CarPark.load_from_db('test.db')
    print("✓ Loaded from database")
    print("Loaded parked cars:", p2.parked_cars)
except Exception as e:
    print(f"✗ Load failed: {e}")
    import traceback
    traceback.print_exc()
