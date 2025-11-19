from practice import CarPark

p = CarPark(2)
assert p.park_car('ABC123')
assert p.park_car('DEF456')
print('Available after parking:', p.available_spots())
# should be full now
assert not p.park_car('GHI789')
assert p.remove_car(1)
print('Available after removal:', p.available_spots())
assert p.park_car('GHI789')
# verify the freed lowest spot (1) was reused
assert p.parked_cars.get(1) == 'GHI789'
print('All tests passed')
