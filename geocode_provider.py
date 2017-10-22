# Copyright Adarsh Uppula, 2017
#
# This program provides a REST-based Geocoding service to resolve addresses to latitude, longitude coordinates
#
#
import abc


class GeocodeProvider(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def geocode_address(self, address):
        """Retrieve data from the input source
        and return an object.
        """