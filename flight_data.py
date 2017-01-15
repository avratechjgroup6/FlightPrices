from json import load


with open('json_files/airlines.json') as f:
    airlines = load(f)
with open('json_files/airports.json') as f:
    airports = load(f)
with open('json_files/cities.json') as f:
    cities = load(f)
with open('json_files/countries.json') as f:
    countries = load(f)