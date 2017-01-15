from json import loads
from requests import request
from data_functions import make_id
from db_procs import insert_search
from instance import access_token
from flight_data import airports, airports, countries


class Search:

    def __init__(self, user_id, origin, destination, date):
        self.id = make_id(user_id)
        self._origin_code = None
        self._origin_name = None
        self._origin_city = None
        self._destination_code = None
        self._destination_name = None
        self._date = date
        self.origin = origin
        self.destination = destination
        self._response = self.search()
        self._insert()

    def _insert(self):
        search_id = self.id
        user_id = int(self.id.split('-')[0])
        origin = self._origin_name
        destination = self._destination_name
        date = self._date
        insert_search(search_id, user_id, origin, destination, date)

    def _parse_results(self):
        results = []
        for offer in self._response['data'][self._origin_city].values():
            results.append(offer)
        return results

    @property
    def origin(self):
        return self._origin_code.split(':')[0]

    @origin.setter
    def origin(self, val):
        found_entry = None
        name = ''
        code = ''
        for entry in airports:
            if val.upper() in entry['name'].upper() or \
                    val.upper() == entry['code']:
                found_entry = True
                name = entry['name']
                code = entry['code'] + ':airport'
        if not found_entry:
            for entry in airports:
                if val.upper() in entry['name'].upper() or \
                        val.upper() == entry['code']:
                    found_entry = True
                    name = entry['name']
                    code = entry['code'] + ':city'
        if found_entry:
            self._origin_code = code
            self._origin_name = name
        else:
            raise ValueError('bad place: Place must be a city or an airport')  # todo: 'no such place'.html

    @property
    def destination(self):
        return self._destination_code.split(':')[0]

    @destination.setter
    def destination(self, val):
        found_entry = None
        name = code = city = ''
        for entry in airports:
            if val.upper() in entry['name'].upper() or \
                    val.upper() == entry['code']:
                found_entry = True
                name = entry['name']
                code = entry['code'] + ':airport'
                city = entry['city_code']
        if not found_entry:
            for entry in airports:
                if val.upper() in entry['name'].upper() or \
                        val.upper() == entry['code']:
                    found_entry = True
                    name = entry['name']
                    code = entry['code'] + ':city'
                    city = entry['code']
        if found_entry is not None:
            self._destination_code = code
            self._destination_name = name
            self._origin_city = city
        else:
            raise ValueError('bad place: Place must be a city or an airport')

    @property
    def response(self):
        return self._parse_results()

    def currency(self):
        code, place = self._origin_code.split(':')
        country = None
        if place == 'airport':
            for entry in airports:
                if self._origin_code.split(':')[0] == entry['code']:
                    country = entry['country_code']
        else:
            for entry in airports:
                if code == entry['code']:
                    country = entry['country_code']
        for entry in countries:
            if entry['code'] == country:
                return entry['currency']

    def search(self):
        headers = {'X-Access-Token': access_token}
        return loads(request(
            'GET',
            'http://api.travelpayouts.com/v1/prices/cheap?'
            'currency={currency}&'
            'origin={origin}&'
            'destination={destination}&'
            'departure_date={date}&'
            'page=1'
            .format(
                currency=self.currency(),
                origin=self.origin,
                destination=self.destination,
                date=self._date,
            ),
            headers=headers
        ).text)
