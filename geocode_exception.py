# Copyright Adarsh Uppula, 2017
#

class GeocodeException(Exception):
    """Geocode exception"""

    type_geocode_not_found = 'GEOCODE_NOT_FOUND'

    def __init__(self, message):
        self.message = message
        self.type = None

    def set_type(self, type):
        self.type = type
