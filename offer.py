from data_functions import split_time_stamp
from db_procs import insert_offer


class Offer:
    def __init__(self, search_id, offer):
        search_id = search_id
        price = offer["price"]
        airline = offer["airline"]
        flight_no = offer["flight_number"]
        date, time = split_time_stamp(offer["departure_at"])
        insert_offer(search_id, price, airline, flight_no, date, time)
