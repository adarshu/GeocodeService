# Copyright Adarsh Uppula, 2017
#
# This program provides a REST-based Geocoding service to resolve addresses to latitude, longitude coordinates
#
#
import abc


class GeocodeProvider(metaclass=abc.ABCMeta):
    timeout = 10

    def set_timeoout(self, timeout):
        """Connection or read timeout"""
        self.timeout = timeout

    @abc.abstractmethod
    def get_name(self):
        """"Retrieve data from the input source
        and return an object.
        """

    @abc.abstractmethod
    def geocode_address(self, address):
        """Retrieve data from the input source
        and return an object.
        """
